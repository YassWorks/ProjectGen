from app.utils.ascii_art import ASCII_ART
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage
from langgraph.graph.state import CompiledStateGraph
from typing import Union, Callable
from langgraph.graph import StateGraph
from app.src.config.ui import AgentUI
from rich.console import Console
from rich.prompt import Prompt
import uuid
import os
import langgraph
import openai


class BaseAgent:

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

    def start_chat(self, recursion_limit: int = 100, config: dict = None):
        self.ui.logo(ASCII_ART)
        self.ui.help(self.model_name)

        if config is None:
            configuration = {
                "configurable": {"thread_id": str(uuid.uuid4())},
                "recursion_limit": recursion_limit,
            }

        continue_flag = False

        while True:
            try:

                if continue_flag:
                    user_input = (
                        "Continue where you left. Don't repeat anything already done."
                    )
                    self.console.print(
                        f"\n[bold blue]You[/bold blue]: {user_input}",
                        style="blue",
                    )
                    continue_flag = False
                else:
                    user_input = Prompt.ask(
                        "\n[bold blue]You[/bold blue]", console=self.console
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

                self.ui.simulate_thinking()

                # start response streaming
                for chunk in self.agent.stream(
                    {"messages": [("human", user_input)]}, configuration
                ):
                    self._display_chunk(chunk)

            except KeyboardInterrupt:
                self.ui.session_interrupted()
                self.ui.goodbye()
                break
            except langgraph.errors.GraphRecursionError:
                self.ui.recursion_warning()
                cont = Prompt.ask(
                    "\n[bold blue]Continue? (y/n): [/bold blue]", console=self.console
                ).strip()
                if cont.lower() in ["y", "yes", "yeah"]:
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
                self.ui.dev_traceback()  # dev (remove later)

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
        if config is None:
            configuration = {
                "configurable": {"thread_id": str(uuid.uuid4())},  # for compatibility
                "recursion_limit": recursion_limit,
            }

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
            msg = "[ERROR] Please try again later or switch to a different model."
            if not quiet:
                self.ui.status_message(
                    title="Rate Limit Exceeded",
                    message=msg,
                    style="red",
                )
            return msg
        except Exception as e:
            if not quiet:
                self.ui.error(str(e))
            return "[ERROR] Unexpected error occurred. Please try again."

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
                ret = "<think>\n" + ret  # some models omit the "<think>" token
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
