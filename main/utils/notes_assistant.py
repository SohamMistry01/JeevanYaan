import os
import operator
import tiktoken
from typing import List, TypedDict, Annotated
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from dotenv import load_dotenv
from .logger import log_response_metadata

load_dotenv()

# -------------------------------
# Configuration
# -------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Models configuration
LLM_MODELS = [
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-guard-4-12b",
    "moonshotai/kimi-k2-instruct"
]

FINAL_MODEL = "openai/gpt-oss-120b"
CHUNK_TOKEN_LIMIT = 3500

def consistency(response):
    return len(set(response)) / len(response)

# -------------------------------
# State Definitions
# -------------------------------

class OverallState(TypedDict):
    file_contents: List[str]
    file_outputs: Annotated[List[str], operator.add]
    user_intent: str
    custom_instruction: str
    final_output: str

class FileProcessingState(TypedDict):
    content: str

# -------------------------------
# File Readers (Adapted for Django Uploads)
# -------------------------------

def read_txt(file_obj) -> str:
    """Reads content from a text file object."""
    try:
        return file_obj.read().decode("utf-8")
    except Exception as e:
        return f"Error reading text file: {e}"

def read_pdf(file_obj) -> str:
    """Reads content from a PDF file object."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_obj)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)
    except Exception as e:
        return f"Error reading PDF: {e}"

def read_docx(file_obj) -> str:
    """Reads content from a DOCX file object."""
    try:
        from docx import Document
        doc = Document(file_obj)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"Error reading DOCX: {e}"

def process_uploaded_files(uploaded_files) -> List[str]:
    """
    Processes a list of Django UploadedFile objects and extracts text.
    """
    contents = []
    for file in uploaded_files:
        ext = os.path.splitext(file.name)[1].lower()
        
        # Reset file pointer to beginning
        file.seek(0)
        
        if ext == ".txt":
            content = read_txt(file)
        elif ext == ".pdf":
            content = read_pdf(file)
        elif ext == ".docx":
            content = read_docx(file)
        else:
            continue # Skip unsupported
            
        if content.strip():
            contents.append(content)
            
    return contents

# -------------------------------
# Token & Chunking Utilities
# -------------------------------

def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def chunk_text(text: str, chunk_token_limit: int = CHUNK_TOKEN_LIMIT) -> List[str]:
    words = text.split()
    chunks, current, token_count = [], [], 0

    for w in words:
        t = count_tokens(w)
        if token_count + t > chunk_token_limit and current:
            chunks.append(" ".join(current))
            current, token_count = [], 0
        current.append(w)
        token_count += t

    if current:
        chunks.append(" ".join(current))

    return chunks

# -------------------------------
# Nodes
# -------------------------------

def process_file_node(state: FileProcessingState):
    text = state["content"]
    chunks = chunk_text(text)
    processed_chunks = []

    for i, chunk in enumerate(chunks):
        # Round-robin model selection for variety/load balancing
        model_name = LLM_MODELS[i % len(LLM_MODELS)]

        llm = ChatGroq(
            model=model_name,
            temperature=0.3,
            api_key=GROQ_API_KEY
        )

        prompt = ChatPromptTemplate.from_template(
            """
            Clean and normalize the following content.
            Preserve meaning and structure.
            Output strictly in Markdown.

            Content:
            {content}
            """
        )

        chain = prompt | llm 
        
        try:
            msg = chain.invoke({"content": chunk})
            
            # ✅ Log Metadata for each chunk
            log_response_metadata(msg.response_metadata, f"Notes Assistant (Chunk {i+1})")
            processed_chunks.append(msg.content.strip())
        except Exception as e:
            processed_chunks.append(f"[Error processing chunk: {e}]")

    return {"file_outputs": ["\n\n".join(processed_chunks)]}

def generate_final_output_node(state: OverallState):
    combined_content = "\n\n".join(state["file_outputs"])
    intent = state["user_intent"]
    custom_instruction = state.get("custom_instruction", "")

    if intent == "summary":
        instruction = """
        Generate a concise, well-structured summary.
        Use Markdown headings, bullet points, and a clear hierarchy.
        """
    elif intent == "quick_revision":
        instruction = """
        Generate quick revision notes.
        Use short bullet points, definitions, key formulas (if any), and important keywords.
        Avoid long explanations.
        """
    elif intent == "practice_qa":
        instruction = """
        Generate practice questions and answers in Markdown.
        Include sections for: 
        1. Short Answer Questions
        2. Long Answer Questions
        3. Conceptual Questions
        Provide clear and accurate answers for each.
        """
    elif intent == "custom":
        instruction = custom_instruction if custom_instruction else "Summarize the content."
    else:
        instruction = "Summarize the content."

    llm = ChatGroq(
        model=FINAL_MODEL,
        temperature=0.3,
        api_key=GROQ_API_KEY
    )

    final_prompt = ChatPromptTemplate.from_template(
        """
        You are an academic assistant.

        Instruction:
        {instruction}

        Output Format:
        Markdown only. Use Only ASCII Characters.

        Content:
        {content}
        """
    )

    chain = final_prompt | llm
    
    try:
        msg = chain.invoke({"instruction": instruction, "content": combined_content})
        
        # ✅ Log Metadata
        log_response_metadata(msg.response_metadata, "Notes Assistant (Final)")
        print("[NOTES ASSISTANT Consistency Value] : ", consistency(msg.content))
        result = msg.content
    except Exception as e:
        result = f"Error generating final output: {e}"

    return {"final_output": result}

# -------------------------------
# Graph Construction
# -------------------------------

def map_files_to_workers(state: OverallState):
    return [Send("process_file", {"content": c}) for c in state["file_contents"]]

workflow = StateGraph(OverallState)
workflow.add_node("process_file", process_file_node)
workflow.add_node("generate_final_output", generate_final_output_node)

workflow.add_conditional_edges(START, map_files_to_workers, ["process_file"])
workflow.add_edge("process_file", "generate_final_output")
workflow.add_edge("generate_final_output", END)

app_graph = workflow.compile()

# -------------------------------
# Public API
# -------------------------------

def run_notes_pipeline(file_contents: List[str], user_intent: str, custom_instruction: str = "") -> str:
    """
    Main entry point for the view.
    """
    if not file_contents:
        return "No readable content found in the uploaded files."

    result = app_graph.invoke({
        "file_contents": file_contents,
        "user_intent": user_intent,
        "custom_instruction": custom_instruction,
        "file_outputs": []
    })

    return result["final_output"]