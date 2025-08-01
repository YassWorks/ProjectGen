from app.src.config.create_base_agent import create_base_agent
from app.src.agents.code_gen.config.tools import ALL_TOOLS
import os


def get_agent(model_name: str, api_key: str):
    
    dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir, "system_prompt.txt"), "r") as file:
        system_prompt = file.read().strip()

    return create_base_agent(
        model_name=model_name,
        api_key=api_key,
        tools=ALL_TOOLS,
        system_prompt=system_prompt,
        temperature=0,
    )
