from app import CLI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("CEREBRAS_API_KEY")

if not api_key:
    print("Error: CEREBRAS_API_KEY environment variable not found")
    exit(1)

client = CLI(
    mode="coding",
    stream=True,
    api_key=api_key,
    codegen_model_name="qwen-3-32b",
    brainstormer_model_name="qwen-3-235b-a22b-thinking-2507",
    web_searcher_model_name="qwen-3-235b-a22b-thinking-2507",
    codegen_temperature=0,
    brainstormer_temperature=0.7,
    web_searcher_temperature=0,
)

client.start_chat()
