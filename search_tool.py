import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = TavilyClient(
    api_key=TAVILY_API_KEY
)


def web_search(query: str):

    try:

        response = client.search(
            query=query,
            max_results=5
        )

        results = []

        for item in response.get("results", []):

            results.append({
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "url": item.get("url", "")
            })

        return results

    except Exception as e:

        return {
            "error": f"Web search failed: {str(e)}"
        }