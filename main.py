from app.src.orchestration.code_generation import orchestrated_codegen
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get required parameters from environment
llm_api_key = os.getenv("CEREBRAS_API_KEY")
model_name = "qwen-3-235b-a22b"

if not llm_api_key:
    raise ValueError("CEREBRAS_API_KEY environment variable is required")
