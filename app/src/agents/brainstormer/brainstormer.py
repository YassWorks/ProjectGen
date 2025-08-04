from app.src.agents.brainstormer.config.config import get_agent
from app.src.config.ui import AgentUI
from rich.console import Console
from app.src.config.base import BaseAgent
import os


class BrainstormerAgent(BaseAgent):

    def __init__(
        self,
        model_name: str,
        api_key: str,
        system_prompt: str = None,
        temperature: float = 0,
    ):

        task_directory = os.path.dirname(os.path.abspath(__file__))
        task_directory = os.path.join(task_directory, "config", "task.txt")
        with open(task_directory, "r") as file:
            minimal_task = file.read().strip()

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
            model_name=model_name,
            api_key=api_key,
            system_prompt=system_prompt,
            agent=agent,
            console=console,
            ui=ui,
            get_agent=get_agent,
            temperature=temperature,
            graph=graph,
        )
        self.minimal_task = minimal_task  # minimal default prompt for brainstorming
