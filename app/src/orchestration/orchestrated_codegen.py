from app.src.config.permissions import PermissionDeniedException
from app.src.orchestration.integrate_web_search import integrate_web_search
from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from app.src.agents.code_gen.code_gen import CodeGenAgent
from app.utils.constants import CONSOLE_WIDTH
from app.utils.ascii_art import ASCII_ART
from app.src.config.ui import AgentUI
from rich.console import Console
from pathlib import Path
import langgraph
import openai
import sys
import os


class CodeGenUnit:
    """Orchestrates multiple agents for complete project generation.

    Coordinates between brainstormer, code generation, and web search agents
    to transform project concepts into functional codebases.

    Args:
        code_gen_agent: Agent for generating project code and structure
        web_searcher_agent: Agent for web research and information gathering
        brainstormer_agent: Agent for project analysis and idea extraction
        assistant: Optional additional assistant for complex operations
    """

    def __init__(
        self,
        code_gen_agent: CodeGenAgent,
        web_searcher_agent: WebSearcherAgent,
        brainstormer_agent: BrainstormerAgent,
    ):
        self.code_gen_agent = code_gen_agent
        self.web_searcher_agent = web_searcher_agent
        self.brainstormer_agent = brainstormer_agent
        self.console = Console(width=CONSOLE_WIDTH)
        self.ui = AgentUI(self.console)

    def run(
        self,
        recursion_limit: int = 100,
        config: dict = None,
        stream: bool = False,
        show_welcome: bool = True,
        working_dir: str = None,
    ) -> bool:
        """Start the interactive project generation workflow.

        Args:
            recursion_limit: Maximum recursion depth for agent operations
            config: Optional configuration dictionary
            stream: Whether to stream responses during generation
            show_welcome: Whether to show the welcome message
            working_dir: The working directory for the project
        """

        try:
            self._enhance_agents()

            if show_welcome:
                self.ui.logo(ASCII_ART)
                self.ui.help()

            while not working_dir:
                try:
                    working_dir = self.ui.get_input(
                        message="Enter project directory",
                        default=os.getcwd(),
                        cwd=os.getcwd(),
                    )
                    os.makedirs(working_dir, exist_ok=True)
                except Exception:
                    self.ui.error("Failed to create project directory")
                    working_dir = None

            user_input = self.ui.get_input(
                message="What would you like to build?",
                cwd=working_dir,
            ).strip()

            prompts_dir = Path(__file__).resolve().parents[2]
            ces_file_path = prompts_dir / "prompts" / "context_engineering_steps.txt"
            with open(str(ces_file_path), "r") as file:
                context_engineering_steps = file.read()

            brainstormer_prompt = (
                f"\n\nIMPORTANT: Place your entire work inside {working_dir}\n\n"
                + context_engineering_steps
                + "\n\n# User input:\n"
                + user_input
                + f"\n\nIMPORTANT: Place your entire work inside {working_dir}"
            )

            configuration = (
                {
                    "configurable": {"thread_id": "START"},
                    "recursion_limit": recursion_limit,
                }
                if config is None
                else config
            )

            continue_flag = True
            while continue_flag:
                try:
                    if not stream:
                        with self.console.status(
                            "[bold]Performing brainstorming and generating the context space...",
                            spinner="dots",
                        ):
                            bs_results = self.brainstormer_agent.invoke(
                                message=brainstormer_prompt,
                                config=configuration,
                                stream=stream,
                                quiet=not stream,  # if the user doesn't want to see the steps, errors are useless too
                                propagate_exceptions=True,
                            )
                    else:
                        bs_results = self.brainstormer_agent.invoke(
                            message=brainstormer_prompt,
                            config=configuration,
                            stream=stream,
                            quiet=not stream,
                            propagate_exceptions=True,
                        )
                    continue_flag = False
                
                except PermissionDeniedException:
                    self.ui.error("Permission denied")
                    return False

                except langgraph.errors.GraphRecursionError:
                    brainstormer_prompt = "Continue where you left. Don't repeat anything already done."
                    self.ui.recursion_warning()
                    if not self.ui.confirm("Continue?", default=True):
                        continue_flag = False
                        self.ui.session_interrupted()
                        sys.exit(0)
                
                except openai.RateLimitError:
                    self.ui.error("Rate limit exceeded")
                    return False
                
                except Exception as e:
                    self.ui.error(f"An unexpected error occurred: {e}")
                    return False

            self.ui.status_message(
                title="Context Engineering Complete",
                message=f"Files generated at {working_dir}",
                emoji="📝",
                style="success",
            )
            
            if not stream:
                self.ui.ai_response(bs_results)

            usr_answer = self.ui.get_input(
                message="Add more context before code generation?",
                default="y",
                choices=["y", "n"],
                show_choices=True,
                cwd=working_dir,
                model=getattr(self.brainstormer_agent, "model_name", "Brainstormer"),
            )

            if usr_answer in ["yes", "y", "yeah"]:
                self.ui.status_message(
                    title="Brainstormer Ready",
                    message="Type '/exit' or press Ctrl+C to continue to code generation",
                    emoji="💭",
                    style="accent",
                )

                exited_safely = self.brainstormer_agent.start_chat(
                    config=configuration, show_welcome=False
                )

                if not exited_safely and not self.ui.confirm(
                    message="Brainstormer session did not exit safely. Do you want to continue to code generation anyway?",
                    default="y",
                ):
                    self.ui.session_interrupted()
                    self.ui.goodbye()
                    return False

            ##################################### starting code generation #####################################
            self.ui.status_message(
                title="Starting code generation",
                message="The CodeGen Agent is now generating code based on the context provided.",
                emoji="🚀",
                style="bold green",
            )

            codegen_file_path = prompts_dir / "prompts" / "codegen_start.txt"
            with open(str(codegen_file_path), "r") as file:
                codegen_start = file.read()

            codegen_prompt = (
                f"\n\nIMPORTANT: Place your entire work inside {working_dir}\n\n"
                + codegen_start
                + f"\n\nIMPORTANT: Place your entire work inside {working_dir}"
            )

            # overwriting the config so that the codegen agent doesnt get confused
            # with the brainstormer's conversation
            configuration = {
                "configurable": {"thread_id": "START2"},
                "recursion_limit": recursion_limit,
            }

            continue_flag = True
            while continue_flag:
                try:
                    if not stream:
                        with self.console.status(
                            "[bold]Generating project. Please wait while the coding agent does all the work...",
                            spinner="dots",
                        ):
                            codegen_results = self.code_gen_agent.invoke(
                                message=codegen_prompt,
                                config=configuration,
                                stream=stream,
                                quiet=not stream,
                                propagate_exceptions=True,
                            )
                    else:
                        codegen_results = self.code_gen_agent.invoke(
                            message=codegen_prompt,
                            config=configuration,
                            stream=stream,
                            quiet=not stream,
                            propagate_exceptions=True,
                        )
                    continue_flag = False
                
                except PermissionDeniedException:
                    self.ui.error("Permission denied")
                    return False

                except langgraph.errors.GraphRecursionError:
                    codegen_prompt = "Continue where you left. Don't repeat anything already done."
                    self.ui.recursion_warning()
                    if not self.ui.confirm("Continue?", default=True):
                        continue_flag = False
                        self.ui.session_interrupted()
                        sys.exit(0)
                
                except openai.RateLimitError:
                    self.ui.error("Rate limit exceeded")
                    return False
                
                except Exception as e:
                    self.ui.error(f"An unexpected error occurred: {e}")
                    return False

            self.ui.status_message(
                title="Project Generation Complete",
                message=f"Code generated at {working_dir}",
                emoji="🎉",
                style="success",
            )

            if not stream:
                self.ui.ai_response(codegen_results)

            self.ui.status_message(
                title="CodeGen Ready",
                message="Starting interactive coding session with the coding agent...",
                emoji="⚡",
                style="accent",
            )

            exited_safely = self.code_gen_agent.start_chat(
                config=configuration, show_welcome=False
            )

            if not exited_safely:
                self.ui.error("The interactive coding session did not exit safely")
                return False

            return True

        except KeyboardInterrupt:
            self.ui.session_interrupted()
            return True

        except Exception as e:
            self.ui.error(f"An error occurred: {e}")
            return False

    def _enhance_agents(self):
        """Integrate web search capabilities into brainstormer and code generation agents."""
        try:
            integrate_web_search(
                agent=self.code_gen_agent, web_searcher=self.web_searcher_agent
            )
        except Exception as e:
            error_msg = f"Failed to integrate web search as a tool to the code generation agent: {e}"
            self.ui.error(error_msg)
            raise RuntimeError(error_msg)
        try:
            integrate_web_search(
                agent=self.brainstormer_agent, web_searcher=self.web_searcher_agent
            )
        except Exception as e:
            error_msg = f"Failed to integrate web search as a tool to the brainstormer agent: {e}"
            self.ui.error(error_msg)
            raise RuntimeError(error_msg)