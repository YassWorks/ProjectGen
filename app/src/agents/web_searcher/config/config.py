from app.src.config.create_base_agent import create_base_agent
from app.src.agents.web_searcher.config.tools import (
    search_and_scrape
)
import os


def get_agent(model_name: str, api_key: str, system_prompt: str = None, temprature: float = 0):
    
    tools = [
        search_and_scrape,
    ]

    if system_prompt is None:
        dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dir, "system_prompt.txt"), "r") as file:
            system_prompt = file.read().strip()

    return create_base_agent(
        model_name=model_name,
        api_key=api_key,
        tools=tools,
        system_prompt=system_prompt,
        temperature=temprature,
    )
