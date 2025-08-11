from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from app.src.agents.code_gen.code_gen import CodeGenAgent
from app.src.orchestration.orchestrated_codegen import CodeGenUnit
from app.src.config.ui import AgentUI
from app.utils.ascii_art import ASCII_ART
from app.utils.constants import CONSOLE_WIDTH
from rich.console import Console
import os


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
        # Validate required parameters for coding mode
        if mode == "coding":
            if not api_key and not all([codegen_api_key, brainstormer_api_key, web_searcher_api_key]):
                raise ValueError("API key must be provided either as 'api_key' or individual agent API keys")
            
            if not all([codegen_model_name, brainstormer_model_name, web_searcher_model_name]):
                raise ValueError("Model names must be provided for all agents in coding mode")
        
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

    def start_chat(self):
        self.ui.logo(ASCII_ART)
        self.ui.help()

        try:
            active_dir = os.getcwd()
            self.ui.status_message(
                title="Current Directory",
                message=f"Working in {active_dir}",
                emoji="📁",
                style="primary"
            )

            if self.ui.confirm("Change working directory?", default=False):
                working_dir = None
                while not working_dir:
                    try:
                        working_dir = self.ui.get_input(
                            message="Enter working directory",
                            default=active_dir,
                            cwd=active_dir
                        )
                        os.makedirs(working_dir, exist_ok=True)
                    except Exception:
                        self.ui.error("Failed to create directory")
                        working_dir = None
                active_dir = working_dir
                self.ui.status_message(
                    title="Directory Updated",
                    message=f"Now working in {os.path.basename(active_dir)}",
                    emoji="📁",
                    style="success"
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
        except KeyboardInterrupt:
            self.ui.goodbye()
        except Exception as e:
            self.ui.error(error_msg=f"An unexpected error occurred: {e}")

    def _initialize_coding_agents(self):
        self.codegen_agent = None
        self.brainstormer_agent = None
        self.web_searcher_agent = None
        
        try:
            self.codegen_agent = CodeGenAgent(
                model_name=self.codegen_model_name,
                api_key=self.codegen_api_key,
                system_prompt=self.codegen_system_prompt,
                temperature=self.codegen_temperature,
            )
        except Exception as e:
            self.ui.error(error_msg=f"Failed to initialize code generation agent: {e}")
            raise RuntimeError(f"Critical agent initialization failed: {e}")
            
        try:
            self.brainstormer_agent = BrainstormerAgent(
                model_name=self.brainstormer_model_name,
                api_key=self.brainstormer_api_key,
                system_prompt=self.brainstormer_system_prompt,
                temperature=self.brainstormer_temperature,
            )
        except Exception as e:
            self.ui.error(error_msg=f"Failed to initialize brainstormer agent: {e}")
            raise RuntimeError(f"Critical agent initialization failed: {e}")
            
        try:
            self.web_searcher_agent = WebSearcherAgent(
                model_name=self.web_searcher_model_name,
                api_key=self.web_searcher_api_key,
                system_prompt=self.web_searcher_system_prompt,
                temperature=self.web_searcher_temperature,
            )
        except Exception as e:
            self.ui.error(error_msg=f"Failed to initialize web searcher agent: {e}")
            raise RuntimeError(f"Critical agent initialization failed: {e}")

    def _initialize_units(self):
        # Validate that all required agents are initialized
        if not all([self.codegen_agent, self.brainstormer_agent, self.web_searcher_agent]):
            error_msg = "Cannot create CodeGenUnit: one or more agents failed to initialize"
            self.ui.error(error_msg=error_msg)
            raise RuntimeError(error_msg)
            
        try:
            self.codegen_unit = CodeGenUnit(
                code_gen_agent=self.codegen_agent,
                web_searcher_agent=self.web_searcher_agent,
                brainstormer_agent=self.brainstormer_agent,
            )
        except Exception as e:
            self.ui.error(error_msg=f"Failed to initialize code generation unit: {e}")
            raise RuntimeError(f"Failed to initialize code generation unit: {e}")
