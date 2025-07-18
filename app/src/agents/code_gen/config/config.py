import os
import sys
from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from .tools import (
    create_wd,
    create_file,
    modify_file,
    delete_file,
    read_file,
    list_directory,
)

def get_agent(model_name):
    """Load configuration and initialize the chat agent."""
    
    load_dotenv()

    API_KEY = os.getenv("CEREBRAS_API_KEY")

    if not API_KEY:
        print("Error: CEREBRAS_API_KEY not found in environment variables.")
        print("Please create a .env file with your Cerebras API key.")
        sys.exit(1)

    llm = ChatCerebras(  
        model=model_name,  
        temperature=0,    
        timeout=None,  
        max_retries=2,  
        api_key=API_KEY,
    )

    memory = MemorySaver()

    tools = [create_wd, create_file, modify_file, delete_file, read_file, list_directory]

    dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir, "system_prompt.txt"), "r") as file:
        system_prompt = file.read().strip()
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{messages}"),
    ])

    agent = create_react_agent(llm, tools, checkpointer=memory, prompt=prompt)
    
    return agent