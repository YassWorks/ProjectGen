from app.src.config.create_base_agent import create_base_agent
from app.src.agents.code_gen.config.tools import ALL_TOOLS
import os


def get_agent(
    model_name: str,
    api_key: str,
    system_prompt: str = None,
    extra_tools: list = None,
    temperature: float = 0,
    include_graph: bool = False,
):
    if extra_tools:
        ALL_TOOLS.extend(extra_tools)

    if system_prompt is None:
        dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dir, "system_prompt.txt"), "r") as file:
            system_prompt = file.read().strip()

    return create_base_agent(
        model_name=model_name,
        api_key=api_key,
        tools=ALL_TOOLS,
        system_prompt=system_prompt,
        temperature=temperature,
        include_graph=include_graph,
    )
