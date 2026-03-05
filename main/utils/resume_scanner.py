import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from .logger import log_response_metadata

load_dotenv()

def consistency(response):
    return len(set(response)) / len(response)

# Initialize Env Variables
groq_api_key = os.getenv("GROQ_API_KEY")
hf_token = os.getenv("HF_TOKEN")

# Ensure keys are set in environment for libraries that might look for them automatically
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key
if hf_token:
    os.environ["HF_TOKEN"] = hf_token

def retrieve_documents(file_path):
    """
    Loads PDF, splits it, and creates a retriever.
    """
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # Initialize Embeddings
        # Note: Ensure sentence-transformers is installed
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Create Vector Store
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever()
        return retriever
    except Exception as e:
        print(f"Error in retrieval process: {e}")
        raise e

def analyze_resume(edu_qual, file_path):
    """
    Main function to analyze the resume using RAG.
    """
    if not groq_api_key:
        return "Error: GROQ_API_KEY not set in environment."

    try:
        # 1. Setup Retriever
        retriever = retrieve_documents(file_path)

        # 2. Setup LLM
        llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)

        # 3. Setup Prompt
        prompt = ChatPromptTemplate.from_template("""
            You are an expert resume scanner.
            You are going to scan the resume whose highest qualification is: {edu_qual}.
            
            Your initial task is to check whether the given file is a resume or not.
            File Context: {context}

            If it is a valid resume then:
            - Generate a brief summary which includes the user's profile.
            - Provide a relevant score out of 10.
            - Highlight the strengths and drawbacks which justifies the score you provided.
            - A bottom line.
            - Generate relevant job roles and salary expectations based on extracted user's Information.

            If it is not a resume then just ask the user to again upload a resume file.
                                                  
            Instructions:
            - Use Markdown formatting.
            - Use ASCII characters only.                                      
        """)

        # 4. Create Chain
        rag_chain = (
            {"context": retriever, "edu_qual": RunnablePassthrough()}
            | prompt
            | llm
            #| StrOutputParser()
        )

        msg = rag_chain.invoke(edu_qual)
        
        # ✅ Log Metadata
        log_response_metadata(msg.response_metadata, "Resume Scanner")
        print("[RESUME SCANNER Consistency Value] : ", consistency(msg.content))
        return msg.content

    except Exception as e:
        return f"An error occurred during analysis: {str(e)}"