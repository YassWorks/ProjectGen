from app import BrainstormerAgent, WebSearcherAgent
from dotenv import load_dotenv
import os

load_dotenv()

llm_api_key = os.getenv("CEREBRAS_API_KEY")
model_name = "qwen-3-235b-a22b-thinking-2507"

if not llm_api_key:
    raise ValueError("CEREBRAS_API_KEY environment variable is required")

# agent = BrainstormerAgent(model_name=model_name, api_key=llm_api_key, temperature=0.7)

# res = agent.invoke("what's 2 + 2 in spain?", include_thinking_block=True, intermediary_chunks=True)
# print(res)

srch = WebSearcherAgent(model_name=model_name, api_key=llm_api_key)

srch.start_chat()