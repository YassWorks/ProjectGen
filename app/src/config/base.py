from app.utils.ascii_art import ASCII_ART
from app.src.config.exception_handler import AgentExceptionHandler
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage
from langgraph.graph.state import CompiledStateGraph
from typing import Union, Callable
from langgraph.graph import StateGraph
from app.src.config.ui import AgentUI
from rich.console import Console
import uuid
import os


class BaseAgent:
    """Base class for all agent implementations.

    Provides common functionality including chat interface, model management,
    and message handling for agent interactions.
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
    ) -> bool:
        """Start interactive chat session with the agent."""
        if show_welcome:
            self.ui.logo(ASCII_ART)
            self.ui.help(self.model_name)

        configuration = config or {
            "configurable": {"thread_id": str(uuid.uuid4())},
            "recursion_limit": recursion_limit,
        }

        continue_flag = False

        while True:
            try:
                user_input = self._get_user_input(continue_flag)
                continue_flag = False

                if not user_input:
                    continue

                if self._handle_command(user_input, configuration):
                    continue

                self.ui.tmp_msg("Working on the task...", 2)

                for chunk in self.agent.stream(
                    {"messages": [("human", user_input)]}, configuration
                ):
                    self._display_chunk(chunk)

            except KeyboardInterrupt:
                self.ui.session_interrupted()
                self.ui.goodbye()
                return True
            except Exception:
                result, should_continue = AgentExceptionHandler.handle_agent_exceptions(
                    lambda: None, self.ui, propagate=False
                )
                if should_continue:
                    continue_flag = True
                    continue
                if result is None:
                    return False

    def _get_user_input(self, continue_flag: bool) -> str:
        """Get user input, handling continuation scenarios."""
        if continue_flag:
            self.ui.status_message(
                title="Continuing Session",
                message="Resuming from previous context...",
                style="primary",
            )
            return "Continue where you left. Don't repeat anything already done."
        else:
            return self.ui.get_input(
                message="Your message",
                model=self.model_name,
            ).strip()

    def _handle_command(self, user_input: str, configuration: dict) -> bool:
        """Handle chat commands. Returns True if command was processed."""
        if user_input.lower() in ["/quit", "/exit", "/q"]:
            self.ui.goodbye()
            return True

        if user_input.lower() == "/clear":
            configuration["configurable"]["thread_id"] = str(uuid.uuid4())
            self.ui.history_cleared()
            return True

        if user_input.lower() in ["/cls", "/clearterm", "/clearscreen"]:
            os.system("clear")
            return True

        if user_input.lower() in ["/help", "/h"]:
            self.ui.help(self.model_name)
            return True

        if user_input.lower().startswith("/model"):
            return self._handle_model_command(user_input)

        if user_input.lower().startswith("/"):
            self.ui.error("Unknown command. Type /help for instructions.")
            return True

        return False

    def _handle_model_command(self, user_input: str) -> bool:
        """Handle model-related commands."""
        command_parts = user_input.lower().split(" ")

        if len(command_parts) == 1:
            self.ui.status_message(
                title="Current Model",
                message=self.model_name,
            )
            return True

        if command_parts[1] == "change":
            if len(command_parts) < 3:
                self.ui.error("Please specify a model to change to.")
                return True

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
            return True

        self.ui.error("Unknown model command. Type /help for instructions.")
        return True

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
        propagate_exceptions: bool = False,
    ):
        """Invoke agent with a message and return response."""

        configuration = config or {
            "configurable": {"thread_id": str(uuid.uuid4())},
            "recursion_limit": recursion_limit,
        }

        if extra_context:
            message = self._add_extra_context(message, extra_context)

        def execute_agent():
            if stream:
                last = None
                for chunk in self.agent.stream(
                    {"messages": [("human", message)]},
                    config=configuration,
                ):
                    if not quiet:
                        self._display_chunk(chunk)
                    last = chunk
                return last.get("llm", {}) if last else {}
            else:
                return self.agent.invoke(
                    {"messages": [("human", message)]},
                    config=configuration,
                )

        raw_response, _ = AgentExceptionHandler.handle_agent_exceptions(
            execute_agent, self.ui, propagate=propagate_exceptions
        )

        if raw_response is None:
            return "[ERROR] Agent execution failed."

        if intermediary_chunks and not quiet:
            for chunk in raw_response.get("messages", []):
                self._display_chunk(chunk)

        ret = self._extract_response_content(raw_response)

        if not include_thinking_block:
            ret = self._remove_thinking_block(ret)
        else:
            ret = self._ensure_thinking_block(ret)

        return ret

    def _add_extra_context(self, message: str, extra_context) -> str:
        """Add extra context to the message."""
        if isinstance(extra_context, str):
            return f"{message}\n\nExtra context you must know:\n{extra_context}"
        elif isinstance(extra_context, list):
            return f"{message}\n\nExtra context you must know:\n" + "\n".join(
                extra_context
            )
        return message

    def _extract_response_content(self, raw_response: dict) -> str:
        """Extract content from agent response."""
        messages = raw_response.get("messages", [])
        if (
            messages
            and isinstance(messages[-1], AIMessage)
            and hasattr(messages[-1], "content")
        ):
            return messages[-1].content.strip()
        return "[ERROR] Agent did not return any messages."

    def _remove_thinking_block(self, content: str) -> str:
        """Remove thinking block from response content."""
        think_end = content.find("</think>")
        if think_end != -1:
            return content[think_end + len("</think>") :].strip()
        return content

    def _ensure_thinking_block(self, content: str) -> str:
        """Ensure thinking block is present in response."""
        if content and content[0] != "<":
            return "<think>\n" + content
        return content

    def _display_chunk(self, chunk: Union[BaseMessage, dict]):
        """Display chunk content in the UI."""
        if isinstance(chunk, BaseMessage):
            if isinstance(chunk, AIMessage):
                self._handle_ai_message(chunk)
            elif isinstance(chunk, ToolMessage):
                self._handle_tool_message(chunk)
        elif isinstance(chunk, dict):
            self._handle_dict_chunk(chunk)

    def _handle_dict_chunk(self, chunk: dict):
        """Handle dictionary chunk format."""
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
        """Handle AI message display."""
        if message.tool_calls:
            for tool_call in message.tool_calls:
                self.ui.tool_call(tool_call["name"], tool_call["args"])
        if message.content and message.content.strip():
            self.ui.ai_response(message.content)

    def _handle_tool_message(self, message: ToolMessage):
        """Handle tool message display."""
        self.ui.tool_output(message.name, message.content)
