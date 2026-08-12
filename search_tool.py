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

        if not TAVILY_API_KEY:
            return {
                "error": "Tavily API key is missing."
            }

        response = client.search(
            query=query,
            max_results=3
        )

        results = []

        for item in response.get("results", []):

            title = item.get("title", "")
            content = item.get("content", "")
            url = item.get("url", "")

            # Limit content size
            content = content[:1000]

            results.append({
                "title": title,
                "content": content,
                "url": url
            })

        return results

    except Exception as e:

        return {
            "error": f"Web search failed: {str(e)}"
        }