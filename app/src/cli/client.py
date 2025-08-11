from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from app.src.agents.code_gen.code_gen import CodeGenAgent
from app.src.orchestration.orchestrated_codegen import CodeGenUnit
from app.src.config.ui import AgentUI
from app.utils.ascii_art import ASCII_ART
from app.utils.constants import CONSOLE_WIDTH
from rich.console import Console
import os
import signal
import sys
import time
import threading


class CLI:

    def __init__(
        self,
        mode: str = "coding",
        stream: bool = True,
        config: dict = None,
        api_key: str = None,
        codegen_model_name: str = None,
        brainstormer_model_name: str = None,
        web_searcher_model_name: str = None,
        codegen_api_key: str = None,
        brainstormer_api_key: str = None,
        web_searcher_api_key: str = None,
        codegen_temperature: float = None,
        brainstormer_temperature: float = None,
        web_searcher_temperature: float = None,
        codegen_system_prompt: str = None,
        brainstormer_system_prompt: str = None,
        web_searcher_system_prompt: str = None,
    ):
        """
        mode can be "coding" or "default" for now
        """
        self.mode = mode
        self.api_key = api_key
        self.stream = stream
        self.config = config
        self.console = Console(width=CONSOLE_WIDTH)
        self.ui = AgentUI(self.console)

        # === coding mode config ===
        self.codegen_model_name = codegen_model_name
        self.brainstormer_model_name = brainstormer_model_name
        self.web_searcher_model_name = web_searcher_model_name

        # if the models stem from different inference providers
        # or the user wants to customize his billing
        self.codegen_api_key = codegen_api_key or api_key
        self.brainstormer_api_key = brainstormer_api_key or api_key
        self.web_searcher_api_key = web_searcher_api_key or api_key

        self.codegen_temperature = codegen_temperature
        self.brainstormer_temperature = brainstormer_temperature
        self.web_searcher_temperature = web_searcher_temperature

        self.codegen_system_prompt = codegen_system_prompt
        self.brainstormer_system_prompt = brainstormer_system_prompt
        self.web_searcher_system_prompt = web_searcher_system_prompt
        
        # utils
        self.last_ctrl_c_time = 0
        self.first_press_message = None
        self.message_timer = None

    def start_chat(self):
        
        signal.signal(signal.SIGINT, self.handle_ctrl_c)
        
        self.console.print()
        self.ui.logo(ASCII_ART)
        self.ui.help()
        
        try:
            active_dir = os.getcwd()
            self.ui.status_message(
                title="Current Directory",
                message=f"You are currently inside [green]{active_dir}[/green]",
            )

            cwd_change = self.ui.get_input(
                message="Do you wish to change the active directory?",
                default="n",
                choices=["y", "n"],
                show_choices=True,
            )
            if cwd_change == "y":
                working_dir = None
                while not working_dir:
                    try:
                        self.console.print()
                        working_dir = self.ui.get_input(
                            message="Please provide the working directory",
                            default=active_dir,
                        )
                        os.makedirs(working_dir, exist_ok=True)
                    except Exception:
                        self.ui.error(
                            "An error occurred while creating the project directory. Please try again"
                        )
                        working_dir = None
                active_dir = working_dir
                self.ui.status_message(
                    title="Current Directory",
                    message=f"You are currently inside [green]{active_dir}[/green]",
                )

            if self.mode != "coding":
                # handle non coding mode later
                return

            self._initialize_coding_agents()
            self._initialize_units()

            self.codegen_unit.run(
                config=self.config,
                stream=self.stream,
                show_welcome=False,
                working_dir=active_dir,
            )
        except SystemExit:
            self.ui.goodbye()

    def _initialize_coding_agents(self):
        try:
            self.codegen_agent = CodeGenAgent(
                model_name=self.codegen_model_name,
                api_key=self.codegen_api_key,
                system_prompt=self.codegen_system_prompt,
                temperature=self.codegen_temperature,
            )
        except Exception as e:
            self.ui.error(error_msg=f"Failed to initialize code generation agent: {e}")
        try:
            self.brainstormer_agent = BrainstormerAgent(
                model_name=self.brainstormer_model_name,
                api_key=self.brainstormer_api_key,
                system_prompt=self.brainstormer_system_prompt,
                temperature=self.brainstormer_temperature,
            )
        except Exception as e:
            self.ui.error(error_msg=f"Failed to initialize brainstormer agent: {e}")
        try:
            self.web_searcher_agent = WebSearcherAgent(
                model_name=self.web_searcher_model_name,
                api_key=self.web_searcher_api_key,
                system_prompt=self.web_searcher_system_prompt,
                temperature=self.web_searcher_temperature,
            )
        except Exception as e:
            self.ui.error(error_msg=f"Failed to initialize web searcher agent: {e}")

    def _initialize_units(self):
        try:
            self.codegen_unit = CodeGenUnit(
                code_gen_agent=self.codegen_agent,
                web_searcher_agent=self.web_searcher_agent,
                brainstormer_agent=self.brainstormer_agent,
            )
        except Exception as e:
            self.ui.error(error_msg=f"Failed to initialize code generation unit: {e}")

    def clear_message(self):
        self.first_press_message = None

    def handle_ctrl_c(self, signum, frame):

        now = time.time()

        if now - self.last_ctrl_c_time < 3:  # Second press within 3 seconds
            print("\n\nGoodbye 👋")
            sys.exit(0)
        else:
            # First press
            self.last_ctrl_c_time = now
            if not self.first_press_message:
                self.first_press_message = "[Press Ctrl+C again within 3s to exit]"
                # Print message at bottom without breaking current output
                sys.stdout.write("\n" + self.first_press_message)
                sys.stdout.flush()
                # Schedule message removal
                if self.message_timer and self.message_timer.is_alive():
                    self.message_timer.cancel()
                self.message_timer = threading.Timer(3, self.clear_message)
                self.message_timer.start()