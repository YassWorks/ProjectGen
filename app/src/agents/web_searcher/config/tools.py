import os
from langchain_core.tools import tool


@tool
def search_web(query: str) -> str:
    """Search the web for a given query."""
    
    ...