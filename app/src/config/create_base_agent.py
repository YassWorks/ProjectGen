from langchain_cerebras import ChatCerebras
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate


class State(TypedDict):
    """Common state structure for all agents."""
    messages: Annotated[list, add_messages]


def create_base_agent(
    model_name: str,
    api_key: str,
    tools: list,
    system_prompt: str,
    temperature: float = 0,
) -> CompiledStateGraph:
    """
    Create a base agent with common configuration and error handling.
    
    Args:
        model_name: The model to use
        api_key: API key for the model
        tools: List of tools to bind to the agent
        system_prompt: System prompt for the agent
        agent_name: Name for the agent (for debugging)
        temperature: Temperature for the model
        temp_chat: Whether to use temporary chat memory
    
    Returns:
        Compiled state graph agent
    """
    
    llm = ChatCerebras(
        model=model_name,
        temperature=temperature,
        timeout=None,
        max_retries=5,
        api_key=api_key,
    )

    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{messages}"),
        ]
    )

    llm_with_tools = llm.bind_tools(tools=tools)
    llm_chain = template | llm_with_tools
    graph = StateGraph(State)

    def llm_node(state: State):
        return {"messages": [llm_chain.invoke(state["messages"])]}

    tool_node = ToolNode(tools=tools)

    def forward(state: State):
        return {}

    graph.add_node("llm", llm_node)
    graph.add_node("tools", tool_node)
    graph.add_node("toolcall_checker", forward)

    graph.add_edge(START, "llm")
    graph.add_conditional_edges(
        "llm", tool_call_attempted, {"toolcall_checker": "toolcall_checker", END: END}
    )
    graph.add_conditional_edges(
        "toolcall_checker", valid_toolcall, {"tools": "tools", "llm": "llm"}
    )
    graph.add_edge("tools", "llm")

    mem = MemorySaver()
    return graph.compile(checkpointer=mem)


def tool_call_attempted(state: State):
    """Check if the agent attempted to make a tool call."""
    if state["messages"]:
        ai_message = state["messages"][-1]
        content = ai_message.content
        tool_calls = ai_message.tool_calls
    else:
        raise ValueError("No messages found in input state to check for tool calls.")

    # Check if tool calls were made or if it looks like the agent tried to make one
    if tool_calls or any(
        substr in content for substr in ("{", "}", "tool_call", "arguments")
    ):  
        return "toolcall_checker"
    else:
        return END


def valid_toolcall(state: State):
    """Validate tool calls and handle malformed ones."""
    if state["messages"]:
        ai_message = state["messages"][-1]
        content = ai_message.content
        tool_calls = ai_message.tool_calls
    else:
        raise ValueError("No messages found in input state to check for tool calls.")
    
    # Check for malformed tool calls
    if not tool_calls and any(
        substr in content for substr in ("{", "}", "tool_call", "arguments", "<tool")
    ):
        error_message = ToolMessage(
            tool_call_id="retry",
            content="Error: Your tool call was malformed or non-JSON. Please fix and retry.",
            invalid=True,
        )

        if "messages" not in state:
            state["messages"] = []
        state["messages"].append(error_message)

        return "llm"
    else:
        return "tools"
