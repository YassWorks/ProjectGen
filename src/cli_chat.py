from config import config

agent = config()

ascii_art = r"""

  ____            _           _    ____            
 |  _ \ _ __ ___ (_) ___  ___| |_ / ___| ___ _ __  
 | |_) | '__/ _ \| |/ _ \/ __| __| |  _ / _ \ '_ \ 
 |  __/| | | (_) | |  __/ (__| |_| |_| |  __/ | | |
 |_|   |_|  \___// |\___|\___|\__|\____|\___|_| |_|
               |__/                                

"""

def main():
    print(ascii_art)
    print("Type your message and press Enter to chat with the AI.")
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print("Type 'clear' to clear the conversation history.")
    print("-" * 50)
    
    configuration = {"configurable": {"thread_id": "abc123"}}
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                # create a new session
                import uuid
                configuration["configurable"]["thread_id"] = str(uuid.uuid4())
                print("Conversation history cleared.")
                continue
            
            if not user_input:
                continue
            
            print("\nAI: ")
            
            response = agent.invoke({"input": user_input}, configuration)
            for msg in response["messages"]:
                try:
                    print(msg.additional_kwargs['tool_calls'][0]["function"])
                except Exception:
                    pass
            
            print(response["messages"][-1].content)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
