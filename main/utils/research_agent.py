import os
from typing import TypedDict, List
from langchain_groq import ChatGroq
from langchain_community.tools import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from newspaper import Article
from dotenv import load_dotenv
from .logger import log_response_metadata

load_dotenv()

def consistency(response):
    return len(set(response)) / len(response)

# --- State Definition ---
class ResearchState(TypedDict):
    topic: str
    urls: List[str]
    articles: List[dict]
    summary: str

# --- Graph Nodes ---

def search_node(state: ResearchState):
    """Searches for relevant articles using Tavily."""
    try:
        # Initialize tool inside the node or globally if preferred
        search_tool = TavilySearchResults(max_results=4)
        results = search_tool.invoke(state['topic'])
        # Handle case where results might be None or malformed
        urls = [res['url'] for res in results] if results else []
        return {"urls": urls}
    except Exception as e:
        print(f"Search error: {e}")
        return {"urls": []}

def scrape_node(state: ResearchState):
    """Scrapes content from the found URLs."""
    scraped_articles = []
    for url in state['urls']:
        try:
            article = Article(url)
            article.download()
            article.parse()
            # Truncate content to avoid context limit issues
            scraped_articles.append({"url": url, "content": article.text[:4000]}) 
        except Exception as e:
            print(f"Could not scrape {url}: {e}")
            # Continue even if one fails
            continue
    return {"articles": scraped_articles}

def summarize_node(state: ResearchState):
    """Generates a summary from the scraped articles."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return {"summary": "Error: GROQ_API_KEY not set."}
    
    try:
        llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, api_key=groq_api_key)
        
        # Create a unified text from all articles
        text_content = ""
        for article in state['articles']:
            text_content += f"--- Article from {article['url']} ---\n\n{article['content']}\n\n"

        if not text_content:
            return {"summary": "No articles could be scraped to generate a summary."}

        prompt = f"""
        You are an expert research assistant.
        Your task is to create a concise, easy-to-read summary in bullet points based on the provided articles for the topic: "{state['topic']}".

        Instructions:
        1.  Synthesize information from all the articles into a single, cohesive summary.
        2.  Do NOT list summaries for each article separately.
        3.  The summary must be in bullet points.
        4.  The tone should be informative and objective.

        Here is the content from the articles:
        {text_content}
        """
        
        summary_result = llm.invoke(prompt)
        # ✅ Log Metadata
        log_response_metadata(summary_result.response_metadata, "Research Agent")
        print("[RESEARCH AGENT Consistency Value] : ", consistency(summary_result.content))
        return {"summary": summary_result.content}
    except Exception as e:
        return {"summary": f"Error generating summary: {e}"}

# --- Main Graph Builder & Execution ---

def get_research_summary(topic):
    """
    Main entry point to run the research agent graph.
    """
    if not topic:
        return None

    # Build Graph
    builder = StateGraph(ResearchState)
    builder.add_node("search", search_node)
    builder.add_node("scrape", scrape_node)
    builder.add_node("summarize", summarize_node)

    builder.add_edge(START, "search")
    builder.add_edge("search", "scrape")
    builder.add_edge("scrape", "summarize")
    builder.add_edge("summarize", END)

    graph = builder.compile()

    try:
        # Invoke Graph
        result = graph.invoke({"topic": topic})
        return {
            "summary": result.get("summary", "No summary generated."),
            "urls": result.get("urls", [])
        }
    except Exception as e:
        return {
            "summary": f"An error occurred during the research process: {str(e)}",
            "urls": []
        }