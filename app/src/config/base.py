from app.utils.ascii_art import ASCII_ART
from app.src.config.permissions import PermissionDeniedException
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage
from langgraph.graph.state import CompiledStateGraph
from typing import Union, Callable
from langgraph.graph import StateGraph
from app.src.config.ui import AgentUI
from rich.console import Console
import uuid
import os
import langgraph
import openai


class BaseAgent:
    """Base class for all agent implementations.

    Provides common functionality including chat interface, model management,
    and message handling for agent interactions.

    Args:
        model_name: LLM model identifier
        api_key: API key for model provider
        system_prompt: System prompt for agent behavior
        agent: Compiled state graph for agent execution
        console: Rich console for UI rendering
        ui: Agent UI handler
        get_agent: Function to create new agent instances
        temperature: Model temperature for randomness control
        graph: Optional state graph for advanced operations
    """

    def __init__(
        self,
        model_name: str,
        api_key: str,
        system_prompt: str,
        agent: CompiledStateGraph,
        console: Console,
        ui: AgentUI,
        get_agent: Callable,
        temperature: float = 0,
        graph: StateGraph = None,
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.agent = agent
        self.console = console
        self.ui = ui
        self.get_agent = get_agent
        self.temperature = temperature
        self.graph = graph

    def start_chat(
        self, recursion_limit: int = 100, config: dict = None, show_welcome: bool = True
    ):
        """Start interactive chat session with the agent.

        Args:
            recursion_limit: Maximum recursion depth for agent operations
            config: Optional configuration dictionary
            show_welcome: Whether to display welcome message and logo
        """
        if show_welcome:
            self.ui.logo(ASCII_ART)
            self.ui.help(self.model_name)

        configuration = (
            {
                "configurable": {"thread_id": str(uuid.uuid4())},
                "recursion_limit": recursion_limit,
            }
            if config is None
            else config
        )

        continue_flag = False

        while True:
            try:

                if continue_flag:
                    user_input = (
                        "Continue where you left. Don't repeat anything already done."
                    )
                    self.ui.status_message(
                        title="Continuing Session",
                        message="Resuming from previous context...",
                        emoji="🔄",
                        style="primary",
                    )
                    continue_flag = False
                else:
                    user_input = self.ui.get_input(
                        message="Your message",
                        model=self.model_name,
                    ).strip()

                if user_input.lower() in ["/quit", "/exit", "/q"]:
                    self.ui.goodbye()
                    break

                if user_input.lower() == "/clear":
                    # new session
                    configuration["configurable"]["thread_id"] = str(uuid.uuid4())
                    self.ui.history_cleared()
                    continue

                if user_input.lower() in ["/cls", "/clearterm", "/clearscreen"]:
                    os.system("clear")
                    continue

                if user_input.lower() in ["/help", "/h"]:
                    self.ui.help(self.model_name)
                    continue

                if not user_input:
                    continue

                command_parts = user_input.lower().split(" ")

                if command_parts[0] == "/model":
                    if len(command_parts) == 1:
                        self.ui.status_message(
                            title="Current Model",
                            message=self.model_name,
                        )
                        continue

                    if command_parts[1] == "change":
                        if len(command_parts) < 3:
                            self.ui.error("Please specify a model to change to.")
                            continue

                        new_model = command_parts[2]
                        self.ui.status_message(
                            title="Change Model",
                            message=f"Changing model to {new_model}",
                        )
                        self.model_name = new_model
                        self.agent = self.get_agent(
                            model_name=self.model_name,
                            api_key=self.api_key,
                            system_prompt=self.system_prompt,
                        )
                        continue

                    self.ui.error("Unknown model command. Type /help for instructions.")
                    continue

                if len(user_input.lower()) > 0 and user_input.lower()[0] == "/":
                    self.ui.error("Unknown command. Type /help for instructions.")
                    continue

                self.ui.tmp_msg("Working on the task...", 2)

                for chunk in self.agent.stream(
                    {"messages": [("human", user_input)]}, configuration
                ):
                    self._display_chunk(chunk)

            except KeyboardInterrupt:
                self.ui.session_interrupted()
                self.ui.goodbye()
                break

            except PermissionDeniedException:
                self.console.print("[dim]\nTool call was blocked by the user. ⚠️\n[/dim]")
                self.ui.session_interrupted()
                self.ui.goodbye()
                break

            except langgraph.errors.GraphRecursionError:
                self.ui.recursion_warning()
                if self.ui.confirm("Continue?", default=True):
                    continue_flag = True

            except openai.RateLimitError:
                self.ui.status_message(
                    "⏳",
                    title="Rate Limit Exceeded",
                    message="Please try again later or switch to a different model.",
                    style="red",
                )

            except Exception as e:
                self.ui.error(str(e))

    def invoke(
        self,
        message: str,
        recursion_limit: int = 100,
        config: dict = None,
        extra_context: str | list[str] = None,
        include_thinking_block: bool = False,
        stream: bool = False,
        intermediary_chunks: bool = False,
        quiet: bool = False,
    ):
        """Invoke agent with a message and return response.

        Args:
            message: Input message for the agent
            recursion_limit: Maximum recursion depth
            config: Optional configuration dictionary
            extra_context: Additional context string or list of strings
            include_thinking_block: Whether to include thinking process
            stream: Whether to stream response chunks
            intermediary_chunks: Whether to show intermediate processing
            quiet: Whether to suppress UI output

        Returns:
            Agent response as string
        """
        configuration = (
            {
                "configurable": {"thread_id": str(uuid.uuid4())},  # for compatibility
                "recursion_limit": recursion_limit,
            }
            if config is None
            else config
        )

        if extra_context:
            if isinstance(extra_context, str):
                message = f"{message}\n\nExtra context you must know:\n{extra_context}"
            elif isinstance(extra_context, list):
                message = f"{message}\n\nExtra context you must know:\n" + "\n".join(
                    extra_context
                )

        try:
            if stream:
                last = None
                for chunk in self.agent.stream(
                    {"messages": [("human", message)]},
                    config=configuration,
                ):
                    if not quiet:
                        self._display_chunk(chunk)
                    last = chunk
                raw_response = last.get(
                    "llm", {}
                )  # NOTE this line depends on the graph implementation
            else:
                raw_response = self.agent.invoke(
                    {"messages": [("human", message)]},
                    config=configuration,
                )
                
        except PermissionDeniedException:
            msg = "[ERROR] The tool call was blocked by the user."
            self.ui.status_message(
                title="Permission Denied",
                message=msg,
            )
            return msg

        except langgraph.errors.GraphRecursionError:
            msg = "[ERROR] The recursion limit has been exceeded. Please try a clearer input."
            if not quiet:
                self.ui.status_message(
                    title="Recursion Limit Exceeded",
                    message=msg,
                    style="red",
                )
            return msg

        except openai.RateLimitError:
            msg = "[ERROR] Rate limit exceeded. Please try again later or switch to a different model."
            if not quiet:
                self.ui.status_message(
                    title="Rate Limit Exceeded",
                    message=msg,
                    style="red",
                )
            return msg

        except Exception as e:
            msg = f"[ERROR] Unexpected error occurred: {str(e)}"
            if not quiet:
                self.ui.error(msg)
            return msg

        if intermediary_chunks and not quiet:
            for chunk in raw_response.get("messages", []):
                self._display_chunk(chunk)

        ret = (
            raw_response.get("messages", [])
            and isinstance(raw_response["messages"][-1], AIMessage)
            and hasattr(raw_response["messages"][-1], "content")
            and raw_response["messages"][-1].content.strip()
        ) or "[ERROR] Agent did not return any messages."

        if not include_thinking_block:
            think_end = ret.find("</think>")
            if think_end != -1:
                ret = ret[think_end + len("</think>") :].strip()
        else:
            if ret and ret[0] != "<":
                ret = "<think>\n" + ret  # some models omit the first "<think>" token
        return ret

    def _display_chunk(self, chunk: Union[BaseMessage, dict]):
        if isinstance(chunk, BaseMessage):
            # Direct message object
            if isinstance(chunk, AIMessage):
                self._handle_ai_message(chunk)
            elif isinstance(chunk, ToolMessage):
                self._handle_tool_message(chunk)

        elif isinstance(
            chunk, dict
        ):  # NOTE that this part depends on the graph implementation
            # Streamed message format
            llm_data = chunk.get("llm", {})
            if "messages" in llm_data:
                messages = llm_data["messages"]
                if messages and isinstance(messages[0], AIMessage):
                    self._handle_ai_message(messages[0])

            tools_data = chunk.get("tools", {})
            if "messages" in tools_data:
                for tool_message in tools_data["messages"]:
                    self._handle_tool_message(tool_message)

    def _handle_ai_message(self, message: AIMessage):
        if message.tool_calls:
            for tool_call in message.tool_calls:
                self.ui.tool_call(tool_call["name"], tool_call["args"])
        if message.content and message.content.strip():
            self.ui.ai_response(message.content)

    def _handle_tool_message(self, message: ToolMessage):
        self.ui.tool_output(message.name, message.content)
