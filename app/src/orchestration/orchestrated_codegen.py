from app.src.agents.code_gen.code_gen import CodeGenAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.orchestration.integrate_web_search import integrate_web_search


class CodeGenUnit:

    def __init__(
        self,
        code_gen_agent: CodeGenAgent,
        web_searcher_agent: WebSearcherAgent,
        brainstormer_agent: BrainstormerAgent,
    ):
        self.code_gen_agent = code_gen_agent
        self.web_searcher_agent = web_searcher_agent
        self.brainstormer_agent = brainstormer_agent

    def enhance_agents(self):
        integrate_web_search(agent=self.code_gen_agent, web_searcher=self.web_searcher_agent)
        integrate_web_search(agent=self.brainstormer_agent, web_searcher=self.web_searcher_agent)
        
    