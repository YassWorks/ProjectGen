from app.src.agents.code_gen.code_gen import CodeGenAgent
from app.src.agents.web_searcher.config.tools import search
from dotenv import load_dotenv
import os

load_dotenv()

LLM_API_KEY = os.getenv("CEREBRAS_API_KEY")
GGL_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
CX_ID = os.getenv("SEARCH_ENGINE_ID")

code_gen = CodeGenAgent(
    model_name="qwen-3-32b",
    api_key=LLM_API_KEY
)

# code_gen.start_chat()

ques = "What command to use to launch a next js app?"

print(search(ques))