import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def web_search(query: str):
    response = client.search(
        query=query,
        max_results=5
    )

    results = []

    for item in response["results"]:
        results.append({
            "title": item["title"],
            "url": item["url"],
            "content": item["content"]
        })

    return results