from app import CLI
from dotenv import load_dotenv
import os

load_dotenv()
llm_api_key = os.getenv("CEREBRAS_API_KEY")

bs_model_name = "qwen-3-235b-a22b-instruct-2507"
ws_model_name = "qwen-3-235b-a22b-instruct-2507"
codegen_model_name = "qwen-3-235b-a22b-instruct-2507"

client = CLI(
    mode="coding",
    stream=True,
    api_key=llm_api_key,
    codegen_model_name=codegen_model_name,
    brainstormer_model_name=bs_model_name,
    web_searcher_model_name=ws_model_name,
    codegen_temperature=0,
    brainstormer_temperature=0.7,
    web_searcher_temperature=0,
)

client.start_chat()