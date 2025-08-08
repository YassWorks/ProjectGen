from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from app.src.agents.code_gen.code_gen import CodeGenAgent
from app.src.orchestration.orchestrated_codegen import CodeGenUnit
from app.src.config.ui import AgentUI
from app.utils.constants import CONSOLE_WIDTH
from rich.console import Console


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

    def start_chat(self):
        if self.mode != "coding":
            # handle non coding mode later
            ...

        self._initialize_coding_agents()
        self._initialize_units()

        self.codegen_unit.run(config=self.config, stream=self.stream)

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
