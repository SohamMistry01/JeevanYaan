import os
import requests
from typing import List, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# ============================
# Schemas
# ============================

class NewsRequest(BaseModel):
    category: Literal[
        "sports", "politics", "technology",
        "business", "health", "science", "general"
    ]
    time_filter: Literal["daily", "weekly", "monthly"]
    limit: int = Field(ge=3, le=10)

class NewsItem(BaseModel):
    headline: str
    summary: str
    url: str

class NewsResponse(BaseModel):
    category: str
    time_range: str
    total_results: int
    news: List[NewsItem]


# ============================
# Helper for Markdown Generation (PDF)
# ============================

def convert_news_to_markdown(news_response: NewsResponse) -> str:
    """Converts the structured news response into a markdown string for PDF generation."""
    md = f"# 📰 Trending News Report\n\n"
    md += f"**Category:** {news_response.category.capitalize()}\n"
    md += f"**Time Range:** {news_response.time_range.capitalize()}\n"
    md += f"**Date Generated:** {os.popen('date').read().strip() if os.name != 'nt' else ''}\n\n"
    md += "---\n\n"
    
    for i, item in enumerate(news_response.news, 1):
        md += f"### {i}. {item.headline}\n"
        md += f"{item.summary}\n\n"
        md += f"**Source:** [{item.url}]({item.url})\n\n"
        md += "---\n\n"
    
    return md

# ============================
# Public API: Tavily Search Integration
# ============================

def get_top_news(request: NewsRequest) -> dict:
    """Fetches news from Tavily and returns a dict with 'data' and 'markdown'"""
    
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"error": "TAVILY_API_KEY not set in environment."}

    # Map your time filters to Tavily's 'days' parameter
    days_map = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30
    }

    # Tavily Search Payload
    payload = {
        "api_key": api_key,
        "query": f"Latest {request.category} news",
        "topic": "news", # This tells Tavily to specifically look for news articles
        "days": days_map[request.time_filter],
        "max_results": request.limit,
        "include_answer": False
    }

    try:
        response = requests.post("https://api.tavily.com/search", json=payload, timeout=30)
        response.raise_for_status()
        raw_data = response.json()
    except Exception as e:
        print(f"Tavily API Error: {e}")
        return {"error": f"Failed to fetch news from Tavily: {str(e)}"}

    # Map the JSON response from Tavily directly into your Pydantic Models
    news_items = []
    for item in raw_data.get("results", []):
        # Tavily's 'content' is a snippet, perfect for the summary
        content_snippet = item.get("content", "No summary available.")
        if len(content_snippet) > 300:
            content_snippet = content_snippet[:297] + "..."
            
        news_items.append(NewsItem(
            headline=item.get("title", "No Title"),
            summary=content_snippet,
            url=item.get("url", "#")
        ))

    news_response = NewsResponse(
        category=request.category,
        time_range=request.time_filter,
        total_results=len(news_items),
        news=news_items
    )

    return {
        "data": news_response,
        "markdown": convert_news_to_markdown(news_response)
    }