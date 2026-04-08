import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from .logger import log_response_metadata

load_dotenv()

def consistency(response):
    return len(set(response)) / len(response)

def get_roadmap(domain):
    """
    Generates a learning roadmap based on GitHub repositories.
    """
    groq_key = os.getenv("GROQ_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")

    if not groq_key or not github_token:
        return "Error: Missing GROQ_API_KEY or GITHUB_TOKEN in environment variables."

    try:
        # 1. Search GitHub
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github+json"
        }
        query = f"{domain} in:name,description"
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=5"
        
        res = requests.get(url, headers=headers)
        
        if res.status_code != 200:
            return f"Error connecting to GitHub API: {res.status_code} - {res.text}"
            
        items = res.json().get("items", [])
        if not items:
            return f"No repositories found for '{domain}'. Please try a different keyword."

        # 2. Format Repository Data for LLM
        repo_data = "\n".join(
            [f"{i+1}. {repo['name']}: {repo['description'] or 'No description'} (URL: {repo['html_url']})" 
             for i, repo in enumerate(items)]
        )

        # 3. Generate Roadmap with LLM
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5, api_key=groq_key, max_tokens=3500)
        
        prompt = f""" 
        You are a career assistant AI.

        Using the following top GitHub repositories in the domain of {domain}:
        {repo_data}

        Please generate a **skill-based learning roadmap**.
        Include:

        - Key learning modules
        - Topics to cover (basic to advanced)
        - When and how to refer these repositories (provide links)
        - Recommended certifications or projects to build

        Format the output using clean markdown and ASCII characters only.
        """
        
        output = llm.invoke(prompt)
        # log response metadata
        log_response_metadata(output.response_metadata, "Roadmap Creator")
        print("[ROADMAP CREATOR Consistency Value] : ", consistency(output.content))
        return output.content

    except Exception as e:
        return f"An error occurred: {str(e)}"