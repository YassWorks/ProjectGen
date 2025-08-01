from app.src.agents.web_searcher.config.config import get_agent
from app.src.config.ui import AgentUI
from rich.console import Console
from app.src.config.base import BaseAgent


class WebSearcherAgent(BaseAgent):

    def __init__(self, model_name: str, api_key: str, system_prompt: str = None, temprature: float = 0):
                
        agent = get_agent(model_name=model_name, api_key=api_key, system_prompt=system_prompt, temprature=temprature)
        console = Console()
        ui = AgentUI(console)

        super().__init__(model_name, api_key, system_prompt, agent, console, ui, get_agent)
