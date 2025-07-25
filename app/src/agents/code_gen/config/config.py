import os
from langgraph.checkpoint.memory import MemorySaver
from langchain_cerebras import ChatCerebras
from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from app.src.agents.code_gen.config.tools import (
    create_wd,
    create_file,
    modify_file,
    delete_file,
    read_file,
    list_directory,
)


def get_agent(
    model_name: str, api_key: str, temp_chat: bool = False
) -> CompiledStateGraph:
    """Load configuration and initialize the code generator agent."""

    llm = ChatCerebras(
        model=model_name,
        temperature=0,
        timeout=None,
        max_retries=5,
        api_key=api_key,
    )

    tools = [
        create_wd,
        create_file,
        modify_file,
        delete_file,
        read_file,
        list_directory,
    ]

    dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir, "system_prompt.txt"), "r") as file:
        system_prompt = file.read().strip()

    mem = MemorySaver() if temp_chat else None

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        name="code_generator",
        checkpointer=mem,
    )

    return agent
