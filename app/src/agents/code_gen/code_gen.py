from app.src.agents.code_gen.config.config import get_agent
from app.src.config.ui import AgentUI
from rich.console import Console
from app.src.config.base import BaseAgent


class CodeGenAgent(BaseAgent):

    def __init__(self, model_name: str, api_key: str, system_prompt: str = None, temperature: float = 0):
        
        graph, agent = get_agent(
            model_name=model_name,
            api_key=api_key,
            system_prompt=system_prompt,
            temperature=temperature,
            include_graph=True,
        )
        
        console = Console(width=80)
        ui = AgentUI(console)

        super().__init__(
            model_name, api_key, system_prompt, agent, console, ui, get_agent, graph
        )