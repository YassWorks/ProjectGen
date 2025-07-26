from langchain_core.tools import tool
from typing import List, Dict
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from pathlib import Path
import os


ROOT_DIR = Path(__file__).resolve().parents[5]
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


GGL_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
CX_ID = os.getenv("SEARCH_ENGINE_ID")


ENDPOINT = "https://customsearch.googleapis.com/customsearch/v1"
TIMEOUT = 10  # seconds


def google_search(query: str, n: int = 5) -> List[Dict[str, str]]:
    """
    Return up to `n` Google results as a list of dicts
    (title, link, snippet).  Raises requests.HTTPError on failure.
    """

    if not GGL_API_KEY or not CX_ID:
        raise ValueError("Google API key or Search Engine ID not set in .env")

    results, start = [], 1
    while len(results) < n:
        batch = min(10, n - len(results))
        payload = {
            "key": GGL_API_KEY,
            "cx": CX_ID,
            "q": query,
            "num": batch,
            "start": start,
        }
        resp = requests.get(ENDPOINT, params=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("items", []):
            results.append(
                {
                    "title": item["title"],
                    "link": item["link"],
                }
            )
            if len(results) == n:
                break

        # prepare next page (if any)
        start += batch
        if "nextPage" not in data.get("queries", {}):
            break

    return results


def fetch_page_text(url: str) -> str:

    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        # kill script/style
        for s in soup(["script", "style", "noscript"]):
            s.decompose()
        text = soup.get_text(separator=" ")
        res = ("\n".join(line.strip() for line in text.splitlines() if line.strip()))[
            :1000
        ]
        return res

    except Exception as e:
        return f"[Error scraping {url}]: {e}"


@tool
def search_and_scrape(query: str) -> str:
    """
    Search Google for a query and get the top results structured as "title" and "content".
    This tool is used to extract information from all sources across the web.
    Args:
        query (str): The search query to use.
    """

    results = google_search(query, 5)
    for r in results:
        r["full_text"] = fetch_page_text(r["link"])

    results = "This answer is possibly incomplete. Consider refining search terms if needed.\n\n"
    # results has "title" and "full_text" keys. Let's structure it nicely for the agent:
    for r in results:
        results += f"Title: {r['title']}\n"
        results += f"Content: {r['full_text']}\n\n"

    return results
