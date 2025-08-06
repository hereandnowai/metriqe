import os
from langchain_tavily import TavilySearch

def research_agent(state):
    """
    Uses the TavilySearch tool to get content from the given urls.
    """
    print("--- RESEARCH AGENT ---")
    urls = state.get("urls", [])
    if not urls:
        print(" > No URLs provided for the research")
        return {"research_results": ""}
    
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        print(" > Tavily API not found in the .env file")
        return {"research_results": ""}
    

    tool = TavilySearch(api_key=tavily_api_key)

    all_content = ""
    for url in urls:
        try:
            results = tool.invoke(f"get_contents:{url}")
            all_content += f"--- content from {url} ---\n{results}\n\n"
            print(f" > Fetched content from {url}")
        except Exception as e:
            print(f" > Error fetching content from {url}: {e}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    research_file_path = os.path.join(project_dir, "research_results.txt")
    with open(research_file_path, "w") as f:
        f.write(all_content)

    print(f" > Research results written to {research_file_path}")
    return {"research_results": research_file_path}




