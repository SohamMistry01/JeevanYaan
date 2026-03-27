import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from langchain_community.tools.tavily_search import TavilySearchResults
from .logger import log_response_metadata

# Load environment variables
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not groq_api_key:
    print("Warning: GROQ_API_KEY not found.")
if not tavily_api_key:
    print("Warning: TAVILY_API_KEY not found.")

# Initialize LLM
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=groq_api_key)

# Initialize Tavily Tool
tavily_tool = TavilySearchResults(
    max_results=4,
    tavily_api_key=tavily_api_key
)

# Define State
class State(TypedDict):
    name: str
    career: str
    education: str
    year: str
    skills: str
    advise: str


def consistency(response):
    return len(set(response)) / len(response)


# ----------- Helper: Clean Content -----------
def clean_content(text: str, max_chars: int = 3000):
    """
    Basic cleaning to avoid prompt injection / noise
    """
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = text.replace("  ", " ")
    text = text.strip()

    # truncate to avoid token explosion
    return text[:max_chars]


# ----------- Helper: Web Search -----------
def fetch_web_context(query: str):
    try:
        results = tavily_tool.invoke({"query": query})

        context_chunks = []
        for r in results:
            content = r.get("content", "")
            url = r.get("url", "")
            cleaned = clean_content(content)

            if cleaned:
                context_chunks.append(f"Source: {url}\n{cleaned}")

        return "\n\n".join(context_chunks)

    except Exception as e:
        print("[WEB SEARCH ERROR]:", str(e))
        return None


# ----------- Node Function -----------
def generate_career_advise_node(state: State):

    base_prompt = f"""
You are an expert career counselor. Analyze the following user profile:

Name: {state['name']}
Career Goal: {state['career']}
Education: {state['education']}
Current Status & Experience: {state['year']}
Current Skills: {state['skills']}
"""

    # ----------- Try Web Search -----------
    web_context = fetch_web_context(state["career"])

    try:
        if web_context:
            # Enriched prompt
            prompt = f"""
{base_prompt}

Additionally, use the following latest web insights to enhance your response:
{web_context}

Instructions:
- Combine web knowledge + your own knowledge
- Prefer recent trends, tools, and industry demands
- Avoid copying text directly from sources
- Produce a clean, structured, personalized plan

Return in markdown:

## Personalized Career Plan for {state['name']}

### Suitable Roles & Target Positions
- ...

### Skills Gap Analysis
- ...

### Actionable Learning Roadmap
- ...

### Top Certifications & Platforms
- ...

### Career Tips and Resources
- ...
"""
        else:
            raise Exception("No web context available")

        msg = llm.invoke(prompt)

    except Exception as e:
        print("[FALLBACK TRIGGERED]:", str(e))

        # ----------- FALLBACK (YOUR ORIGINAL LOGIC) -----------
        msg = llm.invoke(f"""
You are an expert career counselor. Analyze the following user profile:

Name: {state['name']}
Career Goal: {state['career']}
Education: {state['education']}
Current Status & Experience: {state['year']}
Current Skills: {state['skills']}

Generate a highly personalized career plan.

## Personalized Career Plan for {state['name']}

### Suitable Roles & Target Positions
- ...

### Skills Gap Analysis
- ...

### Actionable Learning Roadmap
- ...

### Top Certifications & Platforms
- ...

### Career Tips and Resources
- ...
""")

    log_response_metadata(msg.response_metadata, "Career Planner")
    print("[CAREER PLANNER Consistency Value]: ", consistency(msg.content))

    return {"advise": msg.content}


# ----------- Graph -----------
def get_career_planner_graph():
    graph = StateGraph(State)
    graph.add_node("career planner", generate_career_advise_node)
    graph.add_edge(START, "career planner")
    graph.add_edge("career planner", END)
    return graph.compile()


# ----------- Entry -----------
def get_career_plan(name, career, education, year, skills):
    compiled_graph = get_career_planner_graph()

    try:
        state = compiled_graph.invoke({
            "name": name,
            "career": career,
            "education": education,
            "year": year,
            "skills": skills
        })
        return state.get("advise", "Error: No advice generated.")
    except Exception as e:
        return f"An error occurred: {str(e)}"