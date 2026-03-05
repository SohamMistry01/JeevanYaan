import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from .logger import log_response_metadata

# Load environment variables
load_dotenv()

# Ensure API Key is available
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    # You might want to handle this more gracefully in production settings
    print("Warning: GROQ_API_KEY not found in environment.")

# Initialize LLM (Global instantiation to avoid reloading on every request)
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=groq_api_key)

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

# Node Function
def generate_career_advise_node(state: State):
    msg = llm.invoke(f"""
        You are an expert career counselor. Based on the following user profile:

        Name: {state['name']}
        Career Goal: {state['career']}
        Education: {state['education']}
        Current Year/Status: {state['year']}
        Skills: {state['skills']}

        Please return (in neat markdown format, avoid tabular format, use only ASCII characters):

        ## Personalized Career Plan for {state['name']}
        - ...

        ### Suitable Roles
        - ...

        ### Skills Required
        - ...

        ### Learning Roadmap (Year-wise)
        - ...

        ### Top Certifications & Platforms
        - ...

        ### Career Tips and Resources
        - ...
    """)
    log_response_metadata(msg.response_metadata, "Career Planner")
    print("[CAREER PLANNER Consistency Value]: ", consistency(msg.content))
    return {"advise": msg.content}

# Build the Graph
def get_career_planner_graph():
    graph = StateGraph(State)
    graph.add_node("career planner", generate_career_advise_node)
    graph.add_edge(START, "career planner")
    graph.add_edge("career planner", END)
    return graph.compile()

# Main Entry Point for the View
def get_career_plan(name, career, education, year, skills):
    """
    Invokes the LangGraph agent and returns the markdown advice string.
    """
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
        return f"An error occurred while generating the plan: {str(e)}"