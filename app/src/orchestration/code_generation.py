from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from app.src.agents.code_gen.code_gen import CodeGenAgent
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.tools import tool
import textwrap


def orchestrated_codegen(prompt: str, llm_api_key: str, model_name: str) -> None:
    """
    Orchestrates the code generation process by coordinating multiple agents.
    Available agents:
    - **BrainstormerAgent**: Analyzes the project description and extracts key ideas.
    - **CodeGenAgent**: Generates code based on the provided prompt.
    - **WebSearcherAgent**: Searches the web for additional information.
    """

    code_generator = CodeGenAgent(model_name=model_name, api_key=llm_api_key).agent
    web_searcher = WebSearcherAgent(model_name=model_name, api_key=llm_api_key).agent
    brainstormer = BrainstormerAgent(model_name=model_name, api_key=llm_api_key).agent

    prompt_to_brainstormer = f"""
    Analyze the project description and extract key ideas, technical details, and potential features.
    The project description is as follows:
    {prompt}
    """

    config = {"recursion_limit": 100}

    prompt_to_brainstormer = textwrap.dedent(prompt_to_brainstormer).strip()
    brainstormer_report = brainstormer.invoke(
        {"messages": prompt_to_brainstormer}, config
    )

    prompt += "\n\n" + brainstormer_report["messages"][-1].content
    print("#" * 50)
    print("############### Final prompt for code generation:")
    print(prompt)
    print("#" * 50)

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph = StateGraph(State)

    def code_generator_node(state: State):
        response = code_generator.invoke({"messages": state["messages"]})
        return {"messages": response["messages"]}

    @tool
    def call_searcher(query: str) -> str:
        """
        Ask the assistant to get reliable info from the web.
        The assistant can choose the best queries for your issue to search for.
        You just need to provide a description of the problem you are facing.
        You can also provide a direct query for the assistant to use if you know it.
        Feel free to prompt it as you wish, but keep it concise.
        Args:
            query (str): The query or description of the problem to search for.
        """
        response = web_searcher.invoke({"messages": query})
        return response["messages"][-1].content

    tool_node = ToolNode(tools=[call_searcher])

    graph.add_node("code_gen", code_generator_node)
    graph.add_node("assistant", tool_node)

    graph.add_edge(START, "code_gen")
    graph.add_conditional_edges(
        "code_gen", tools_condition, {"assistant": "assistant", END: END}
    )
    graph.add_edge("assistant", "code_gen")

    g = graph.compile()
    print(f"Graph compiled: {g}")

    g_config = {"recursion_limit": 100}

    response = g.invoke({"messages": [HumanMessage(content=prompt)]}, g_config)
    
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
