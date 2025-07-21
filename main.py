from app.src.agents.code_gen.code_gen import CodeGenAgent
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("CEREBRAS_API_KEY")

code_gen = CodeGenAgent(
    model_name="qwen-3-32b",
    api_key=API_KEY
)

code_gen.start_chat()