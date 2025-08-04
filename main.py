from app import BrainstormerAgent, WebSearcherAgent, CodeGenAgent, CodeGenUnit
from dotenv import load_dotenv
import os

load_dotenv()
llm_api_key = os.getenv("CEREBRAS_API_KEY")

bs_model_name = "qwen-3-235b-a22b-thinking-2507"
codegen_model_name = "qwen-3-coder-480b"

srch = WebSearcherAgent(model_name=bs_model_name, api_key=llm_api_key, temperature=0.7)
codegen = CodeGenAgent(model_name=codegen_model_name, api_key=llm_api_key, temperature=0)
bs = BrainstormerAgent(model_name=bs_model_name, api_key=llm_api_key, temperature=0.7)

unit1 = CodeGenUnit(
    code_gen_agent=codegen,
    web_searcher_agent=srch,
    brainstormer_agent=bs,
)

unit1.run(stream=True)
