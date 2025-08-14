from app.src.orchestration.base_unit import BaseUnit
from app.src.config.exception_handler import AgentExceptionHandler
from app.src.orchestration.integrate_web_search import integrate_web_search
from app.utils.constants import UI_MESSAGES
from app.utils.ascii_art import ASCII_ART
from pathlib import Path
import sys
import os


class CodeGenUnit(BaseUnit):
    """Orchestrates multiple agents for complete project generation."""

    def __init__(self, code_gen_agent, web_searcher_agent, brainstormer_agent):
        agents = {
            "code_gen": code_gen_agent,
            "web_searcher": web_searcher_agent,
            "brainstormer": brainstormer_agent,
        }
        super().__init__(agents)

    def _validate_agents(self):
        """Validate that all required agents are present."""
        required_agents = ["code_gen", "web_searcher", "brainstormer"]
        for agent_name in required_agents:
            if agent_name not in self.agents or self.agents[agent_name] is None:
                raise ValueError(f"Missing required agent: {agent_name}")

    def run(
        self,
        recursion_limit: int = 100,
        config: dict = None,
        stream: bool = False,
        show_welcome: bool = True,
        working_dir: str = None,
    ) -> bool:
        """Execute the complete project generation workflow."""
        try:
            self._enhance_agents()

            if show_welcome:
                self.ui.logo(ASCII_ART)
                self.ui.help()

            working_dir = working_dir or self._setup_working_directory()

            return self._execute_generation_workflow(
                working_dir, recursion_limit, config, stream
            )

        except KeyboardInterrupt:
            self.ui.session_interrupted()
            return True
        except Exception as e:
            self.ui.error(f"Workflow execution failed: {e}")
            return False

    def _execute_generation_workflow(
        self, working_dir: str, recursion_limit: int, config: dict, stream: bool
    ) -> bool:
        """Execute the main generation workflow steps."""
        # Step 1: Context Engineering
        if not self._run_brainstorming_phase(
            working_dir, recursion_limit, config, stream
        ):
            return False

        # Step 2: Optional additional context
        if not self._handle_additional_context(working_dir, recursion_limit, config):
            return False

        # Step 3: Code Generation
        if not self._run_code_generation_phase(
            working_dir, recursion_limit, config, stream
        ):
            return False

        # Step 4: Interactive coding session
        return self._run_interactive_session(recursion_limit, config)

    def _run_brainstorming_phase(
        self, working_dir: str, recursion_limit: int, config: dict, stream: bool
    ) -> bool:
        """Execute the brainstorming and context engineering phase."""
        user_input = self.ui.get_input(
            message=UI_MESSAGES["project_prompt"],
            cwd=working_dir,
        ).strip()

        brainstormer_prompt = self._create_brainstormer_prompt(user_input, working_dir)
        configuration = config or self._create_agent_config("START", recursion_limit)

        return self._execute_with_retry(
            lambda: self.agents["brainstormer"].invoke(
                message=brainstormer_prompt,
                config=configuration,
                stream=stream,
                quiet=not stream,
                propagate_exceptions=True,
            ),
            "Performing brainstorming and generating the context space...",
            UI_MESSAGES["titles"]["context_complete"],
            f"Files generated at {working_dir}",
            stream,
        )

    def _run_code_generation_phase(
        self, working_dir: str, recursion_limit: int, config: dict, stream: bool
    ) -> bool:
        """Execute the code generation phase."""
        self.ui.status_message(
            title=UI_MESSAGES["titles"]["generation_starting"],
            message="The CodeGen Agent is now generating code based on the context provided.",
            style="success",
        )

        codegen_prompt = self._create_codegen_prompt(working_dir)
        configuration = self._create_agent_config("START2", recursion_limit)

        return self._execute_with_retry(
            operation=lambda: self.agents["code_gen"].invoke(
                message=codegen_prompt,
                config=configuration,
                stream=stream,
                quiet=not stream,
                propagate_exceptions=True,
            ),
            status_msg="Generating project. Please wait while the coding agent does all the work...",
            success_title=UI_MESSAGES["titles"]["generation_complete"],
            success_msg=f"Code generated at {working_dir}",
            stream=stream,
        )

    def _handle_additional_context(
        self, working_dir: str, recursion_limit: int, config: dict
    ) -> bool:
        """Handle optional additional context gathering."""
        usr_answer = self.ui.get_input(
            message=UI_MESSAGES["add_context"],
            default="y",
            choices=["y", "n"],
            show_choices=True,
            cwd=working_dir,
            model=getattr(self.agents["brainstormer"], "model_name", "Brainstormer"),
        )

        if usr_answer in ["yes", "y", "yeah"]:
            self.ui.status_message(
                title=UI_MESSAGES["titles"]["brainstormer_ready"],
                message="Type '/exit' or press Ctrl+C to continue to code generation",
                style="accent",
            )

            configuration = config or self._create_agent_config(
                "START", recursion_limit
            )
            exited_safely = self.agents["brainstormer"].start_chat(
                config=configuration, show_welcome=False
            )

            if not exited_safely and not self.ui.confirm(
                message=UI_MESSAGES["continue_generation"],
                default=True,
            ):
                self.ui.session_interrupted()
                self.ui.goodbye()
                return False

        return True

    def _run_interactive_session(self, recursion_limit: int, config: dict) -> bool:
        """Run the interactive coding session."""
        self.ui.status_message(
            title=UI_MESSAGES["titles"]["codegen_ready"],
            message="Starting interactive coding session with the coding agent...",
            style="accent",
        )

        configuration = self._create_agent_config("START2", recursion_limit)
        exited_safely = self.agents["code_gen"].start_chat(
            config=configuration, show_welcome=False
        )

        if not exited_safely:
            self.ui.error("The interactive coding session did not exit safely")
            return False

        return True

    def _execute_with_retry(
        self,
        operation,
        status_msg: str,
        success_title: str,
        success_msg: str,
        stream: bool,
    ):
        """Execute an operation with retry logic and consistent UI handling."""
        continue_flag = True
        result = None

        while continue_flag:
            try:
                if not stream:
                    with self.console.status(f"[bold]{status_msg}", spinner="dots"):
                        result = operation()
                else:
                    result = operation()
                continue_flag = False

            except Exception:
                result, continue_flag = AgentExceptionHandler.handle_agent_exceptions(
                    operation, self.ui, propagate=True
                )
                if result is None:
                    return False
                if isinstance(result, str) and continue_flag:
                    # This is a continue prompt, update operation
                    original_op = operation
                    operation = lambda: original_op()  # Keep the same operation

        self.ui.status_message(
            title=success_title,
            message=success_msg,
            style="success",
        )

        if not stream and result:
            self.ui.ai_response(result)

        return True

    def _create_brainstormer_prompt(self, user_input: str, working_dir: str) -> str:
        """Create the brainstormer prompt with context engineering steps."""
        prompts_dir = Path(__file__).resolve().parents[2]
        ces_file_path = prompts_dir / "prompts" / "context_engineering_steps.txt"

        with open(str(ces_file_path), "r") as file:
            context_engineering_steps = file.read()

        return (
            f"\n\nIMPORTANT: Place your entire work inside {working_dir}\n\n"
            + context_engineering_steps
            + "\n\n# User input:\n"
            + user_input
            + f"\n\nIMPORTANT: Place your entire work inside {working_dir}"
        )

    def _create_codegen_prompt(self, working_dir: str) -> str:
        """Create the code generation prompt."""
        prompts_dir = Path(__file__).resolve().parents[2]
        codegen_file_path = prompts_dir / "prompts" / "codegen_start.txt"

        with open(str(codegen_file_path), "r") as file:
            codegen_start = file.read()

        return (
            f"\n\nIMPORTANT: Place your entire work inside {working_dir}\n\n"
            + codegen_start
            + f"\n\nIMPORTANT: Place your entire work inside {working_dir}"
        )

    def _enhance_agents(self):
        """Integrate web search capabilities into agents."""
        try:
            integrate_web_search(
                agent=self.agents["code_gen"], web_searcher=self.agents["web_searcher"]
            )
            integrate_web_search(
                agent=self.agents["brainstormer"],
                web_searcher=self.agents["web_searcher"],
            )
        except Exception as e:
            error_msg = f"Failed to integrate web search capabilities: {e}"
            self.ui.error(error_msg)
            raise RuntimeError(error_msg)
