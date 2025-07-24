from app.src.agents.code_gen.code_gen import CodeGenAgent
from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from pathlib import Path
from dotenv import load_dotenv
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage


ROOT_DIR = Path(__file__).resolve().parents[4]
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)
llm_api_key = os.getenv("CEREBRAS_API_KEY")


def orchestrated_codegen(prompt: str):

    code_generator = CodeGenAgent(
        model_name="qwen-3-235b-a22b", api_key=llm_api_key
    ).agent

    web_searcher = WebSearcherAgent(
        model_name="qwen-3-235b-a22b", api_key=llm_api_key
    ).agent

    # brainstormer = BrainstormerAgent(
    #     model_name="qwen-3-235b-a22b",
    #     api_key=llm_api_key,
    # ).agent

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph = StateGraph(State)

    def code_generator_node(state: State):
        response = code_generator.invoke({"messages": state["messages"]})
        return {"messages": response["messages"]}

    @tool
    def call_searcher(query: str) -> str:
        """
        Ask the searcher agent to search the web for the given query.
        """
        response = web_searcher.invoke({"messages": query})
        return response["messages"][-1].content

    tool_node = ToolNode(tools=[call_searcher])

    graph.add_node("code_gen", code_generator_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "code_gen")
    graph.add_conditional_edges("code_gen", tools_condition, {"tools", END})
    graph.add_edge("tools", "code_gen")

    g = graph.compile()
    print(f"Graph compiled: {g}")

    response = g.invoke({"messages": [HumanMessage(content=prompt)]})
    for msg in response["messages"]:
        try:
            print(f"\n=== TOOL CALLED === {msg.tool_calls[0]['name']}\n")
            args = msg.tool_calls[0]["args"]
            for k, v in args.items():
                print(f"------------ ARGUMENT: {k} \n{v}\n")
            print("=" * 50)
        except Exception:
            pass
        print(response["messages"][-1].content)
