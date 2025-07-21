from langchain_core.tools import tool
from typing import List, Dict
from bs4 import BeautifulSoup
import requests
from langchain_cerebras import ChatCerebras
from dotenv import load_dotenv
from pathlib import Path
import os


ROOT_DIR = Path(__file__).resolve().parents[5]
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_config():

    llm_api_key = os.getenv("CEREBRAS_API_KEY")
    ggl_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx_id = os.getenv("SEARCH_ENGINE_ID")
    return llm_api_key, ggl_api_key, cx_id


ENDPOINT = "https://customsearch.googleapis.com/customsearch/v1"
TIMEOUT  = 10  # seconds


# @tool
def search(query: str) -> str:
    """Search the web for the given query and return a summary of the results."""
    
    llm_api_key, ggl_api_key, cx_id = get_config()
    summarizer = ChatCerebras(
        model="llama3.1-8b",
        temperature=0,
        timeout=None,
        max_retries=5,
        api_key=llm_api_key,
    )
    content = search_and_scrape(
        query=query,
        api_key=ggl_api_key,
        cx_id=cx_id,
        n=5
    )
    summary = summarizer.invoke(
        f"Summarize the following text as much as possible while still answering the question: {query}\n\n{content}"
    )
    
    return summary.content


def google_search(query: str, api_key: str, cx_id: str, n: int) -> List[Dict[str, str]]:
    """
    Return up to `n` Google results as a list of dicts
    (title, link, snippet).  Raises requests.HTTPError on failure.
    """
    
    if not api_key or not cx_id:
        raise RuntimeError("Set GOOGLE_SEARCH_API_KEY and SEARCH_ENGINE_ID env vars.")
    if n < 1 or n > 100:
        raise ValueError("n must be 1–100 (API hard limit).")

    results, start = [], 1
    while len(results) < n:
        batch = min(10, n - len(results))
        payload = {
            "key":   api_key,
            "cx":    cx_id,
            "q":     query,
            "num":   batch,
            "start": start,
        }
        resp = requests.get(ENDPOINT, params=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("items", []):
            results.append(
                {"title": item["title"],
                 "link":  item["link"],
                 "snippet": item.get("snippet", "")}
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
        for s in soup(["script", "style", "noscript"]): s.decompose()
        text = soup.get_text(separator=" ")
        res = ("\n".join(line.strip() for line in text.splitlines() if line.strip()))[:1000]
        return res

    except Exception as e:
        return f"[Error scraping {url}]: {e}"


def search_and_scrape(query: str, api_key: str, cx_id: str, n: int) -> str:

    results = google_search(query, api_key, cx_id, n)
    for r in results:
        r["full_text"] = fetch_page_text(r["link"])
    ret = "\n\n".join(r["full_text"] for r in results)
    
    return ret