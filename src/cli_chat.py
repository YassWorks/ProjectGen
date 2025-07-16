import os
import sys
from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from tools import add, multiply, subtract, divide, call_larry

load_dotenv()

API_KEY = os.getenv("CEREBRAS_API_KEY")

if not API_KEY:
    print("Error: CEREBRAS_API_KEY not found in environment variables.")
    print("Please create a .env file with your Cerebras API key.")
    sys.exit(1)

llm = ChatCerebras(  
    model="llama-4-scout-17b-16e-instruct",  
    temperature=0,  
    max_tokens=10000,  
    timeout=None,  
    max_retries=2,  
    api_key=API_KEY,
)

memory = MemorySaver()

tools = [add, multiply, subtract, divide, call_larry]

agent_executor = create_react_agent(llm, tools, checkpointer=memory)

config = {"configurable": {"thread_id": "cli_chat_session"}}

def main():
    print("=== AI Chat CLI Tool ===")
    print("Type your message and press Enter to chat with the AI.")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("Type 'clear' to clear the conversation history.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                # create a new thread ID to effectively clear history
                import uuid
                config["configurable"]["thread_id"] = str(uuid.uuid4())
                print("Conversation history cleared.")
                continue
            
            if not user_input:
                continue
            
            input_message = {
                "role": "user",
                "content": user_input,
            }
            
            print("\nAI: ", end=" ")
            
            response = agent_executor.invoke({"messages": [input_message]}, config)
            print(response["messages"][-1].content)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
