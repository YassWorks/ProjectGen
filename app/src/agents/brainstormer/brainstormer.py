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
            task = file.read().strip()

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
        self.task = task

    def invoke(
        self,
        message: str,
        recursion_limit: int = 100,
        extra_context: str | list[str] = None,
        include_thinking_block: bool = False,
        stream: bool = False,
        intermediary_chunks: bool = False,
    ):
        if extra_context:
            if isinstance(extra_context, str):
                full_extra_context = (
                    f"{self.task}\n\nExtra context you must know:\n{extra_context}"
                )
            elif isinstance(extra_context, list):
                full_extra_context = (
                    f"{self.task}\n\nExtra context you must know:\n"
                    + "\n".join(extra_context)
                )
        else:
            full_extra_context = self.task

        return super().invoke(
            message=message,
            recursion_limit=recursion_limit,
            extra_context=full_extra_context,
            include_thinking_block=include_thinking_block,
            stream=stream,
            intermediary_chunks=intermediary_chunks,
        )
