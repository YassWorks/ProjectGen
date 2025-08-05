from app.src.agents.code_gen.code_gen import CodeGenAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.orchestration.integrate_web_search import integrate_web_search
from app.utils.ascii_art import ASCII_ART
from langchain_cerebras import ChatCerebras
from app.src.config.ui import AgentUI
from pathlib import Path
import os
from rich.markdown import Markdown
from rich.console import Console
from rich.prompt import Prompt
from time import sleep
from typing import Any


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
        assistant: ChatCerebras | Any = None,
    ):
        self.code_gen_agent = code_gen_agent
        self.web_searcher_agent = web_searcher_agent
        self.brainstormer_agent = brainstormer_agent
        self.assistant = assistant
        self.console = Console(width=100)
        self.ui = AgentUI(self.console)

    def enhance_agents(self):
        """Integrate web search capabilities into brainstormer and code generation agents."""
        integrate_web_search(
            agent=self.code_gen_agent, web_searcher=self.web_searcher_agent
        )
        integrate_web_search(
            agent=self.brainstormer_agent, web_searcher=self.web_searcher_agent
        )

    def run(
        self, recursion_limit: int = 100, config: dict = None, stream: bool = False
    ):
        """Start the interactive project generation workflow.
        
        Args:
            recursion_limit: Maximum recursion depth for agent operations
            config: Optional configuration dictionary
            stream: Whether to stream responses during generation
        """
        self.enhance_agents()
        self.console.print()
        self.ui.logo(ASCII_ART)
        self.ui.help()

        working_dir = None
        while not working_dir:
            try:
                self.console.print()
                working_dir = Prompt.ask(
                    "[blue]  Please provide the working directory",
                    console=self.console,
                )
                os.makedirs(working_dir, exist_ok=True)
            except Exception:
                self.ui.error(
                    "An error occurred while creating the project directory. Please try again"
                )
                working_dir = None

        self.console.print()
        user_input = Prompt.ask(
            "[blue]  What cool ideas do you have for me today? ", console=self.console
        ).strip()

        prompts_dir = Path(__file__).resolve().parents[2]
        ces_file_path = prompts_dir / "prompts" / "context_engineering_steps.txt"
        with open(str(ces_file_path), "r") as file:
            context_engineering_steps = file.read()

        brainstormer_prompt = (
            context_engineering_steps
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

        # Creating the context space for the code_gen agent
        self.console.print()
        if not stream:
            with self.console.status(
                "[bold green]🧠 Brainstormer Agent is analyzing your request...",
                spinner="dots",
            ):
                bs_results = self.brainstormer_agent.invoke(
                    message=brainstormer_prompt,
                    config=configuration,
                    stream=stream,
                    quiet=not stream,  # if the user doesn't want to see the steps, errors are useless too
                )
        else:
            bs_results = self.brainstormer_agent.invoke(
                message=brainstormer_prompt,
                config=configuration,
                stream=stream,
                quiet=not stream,
            )

        self.ui.status_message(
            title="Context Engineering steps done!",
            message=f"You can always check the files generated at the following path: {working_dir}",
            emoji="📝",
            style="bold green",
        )

        if "[ERROR]" not in bs_results and not stream:
            self.console.print("[bold green]  Final Brainstormer Agent message:")
            md = Markdown(bs_results)
            self.console.print(md)

        self.console.print()
        usr_answer = (
            Prompt.ask(
                "[blue]  Would you like to add additional context before beginning code generation? (y/n) ",
                console=self.console,
            )
            .strip()
            .lower()
        )

        if usr_answer in ["yes", "y", "yeah"]:
            self.console.print()
            with self.console.status(
                "[bold green]  Starting conversation with the Brainstormer Agent...",
                spinner="dots",
            ):
                sleep(1)
            self.console.print(
                "[bold green]  You may exit anytime by typing '/exit', '/quit', '/q' or by pressing Ctrl+c [/bold green]"
            )

            self.brainstormer_agent.start_chat(config=configuration, show_welcome=False)

        # Starting code generation
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
            codegen_start
            + f"\n\nIMPORTANT: Place your entire work inside {working_dir}"
        )

        # Overwriting the config so that the codegen agent doesn't get confused
        # with the brainstormer's conversation
        configuration = {
            "configurable": {"thread_id": "START2"},
            "recursion_limit": recursion_limit,
        }

        self.console.print()
        if not stream:
            with self.console.status(
                "[bold green]⚡ CodeGen Agent is generating your project...",
                spinner="dots",
            ):
                codegen_results = self.code_gen_agent.invoke(
                    message=codegen_prompt,
                    config=configuration,
                    stream=stream,
                    quiet=not stream,
                )
        else:
            codegen_results = self.code_gen_agent.invoke(
                message=codegen_prompt,
                config=configuration,
                stream=stream,
                quiet=not stream,
            )

        self.ui.status_message(
            title="Initial project generation done!",
            message=f"You can always check the code generated at the following path: {working_dir}",
            emoji="📝",
            style="bold green",
        )

        if "[ERROR]" not in codegen_results:
            self.console.print("[bold green]  Final CodeGen Agent message:")
            md = Markdown(codegen_results)
            self.console.print(md)

        self.console.print()
        with self.console.status(
            "[bold green]  Starting conversation with the CodeGen Agent...",
            spinner="dots",
        ):
            sleep(1)
        self.console.print(
            "[bold green]  You may exit anytime by typing '/exit', '/quit', '/q' or by pressing Ctrl+c [/bold green]"
        )

        self.code_gen_agent.start_chat(config=configuration, show_welcome=False)
