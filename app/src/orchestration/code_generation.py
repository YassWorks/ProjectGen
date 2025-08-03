from app.src.agents.brainstormer.brainstormer import BrainstormerAgent
from app.src.agents.web_searcher.web_searcher import WebSearcherAgent
from app.src.config.base import BaseAgent
from langchain_core.tools import tool



def integrate_web_search(agent: BaseAgent, web_searcher: WebSearcherAgent) -> None:

    @tool
    def call_searcher(query: str) -> str:
        """
        Ask the assistant to get reliable info from the web.
        The assistant can choose the best queries for your issue to search for.
        You just need to provide a description of the problem you are facing.
        You can also provide a direct query for the assistant to use if you know it.
        Feel free to prompt it as you wish, but keep it concise.
        Args:
            query (str): The query or description of the problem to search for.
        """
        return web_searcher.invoke(
            message=query,
            recursion_limit=100,
            quiet=True,
        )

    enhanced_agent, enhanced_graph = agent.get_agent(
        model_name=agent.model_name,
        api_key=agent.api_key,
        extra_tools=[call_searcher],
        temperature=agent.temperature,
        include_graph=True,
    )

    agent.agent = enhanced_agent
    agent.graph = enhanced_graph


# def orchestrated_codegen(prompt: str, llm_api_key: str, model_name: str) -> None:
#     """
#     Orchestrates the code generation process by coordinating multiple agents.
#     Available agents:
#     - **BrainstormerAgent**: Analyzes the project description and extracts key ideas.
#     - **CodeGenAgent**: Generates code based on the provided prompt.
#     - **WebSearcherAgent**: Searches the web for additional information.
#     """

#     web_searcher = WebSearcherAgent(model_name=model_name, api_key=llm_api_key).agent
#     brainstormer = BrainstormerAgent(model_name=model_name, api_key=llm_api_key).agent

#     prompt_to_brainstormer = f"""
#     Analyze the project description and extract key ideas, technical details, and potential features.
#     The project description is as follows:
#     {prompt}
#     """

#     config = {"recursion_limit": 100}

#     prompt_to_brainstormer = textwrap.dedent(prompt_to_brainstormer).strip()
#     brainstormer_report = brainstormer.invoke(
#         {"messages": prompt_to_brainstormer}, config
#     )

#     prompt += "\n\n" + brainstormer_report["messages"][-1].content
#     print("#" * 50)
#     print("############### Final prompt for code generation:")
#     print(prompt)
#     print("#" * 50)
