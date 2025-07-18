from config.config import get_agent
import uuid


ASCII_ART = r"""

  ____            _           _    ____            
 |  _ \ _ __ ___ (_) ___  ___| |_ / ___| ___ _ __  
 | |_) | '__/ _ \| |/ _ \/ __| __| |  _ / _ \ '_ \ 
 |  __/| | | (_) | |  __/ (__| |_| |_| |  __/ | | |
 |_|   |_|  \___// |\___|\___|\__|\____|\___|_| |_|
               |__/                                

"""


class CodeGenAgent:

    def __init__(self, model_name):

        self.agent = get_agent(model_name=model_name)

    def start_chat(self, message=None):

        print(ASCII_ART)
        print("Type your message and press Enter to chat with the AI.")
        print("Type 'quit', 'exit', or 'q' to end the conversation.")
        print("Type 'clear' to clear the conversation history.")
        print("-" * 50)

        configuration = {
            "configurable": {"thread_id": "abc123"},
            "recursion_limit": 100,
        }

        if message:
            print("\nYou:\n")
            print(message)
            print("\nAI:\n")
            response = self.agent.invoke({"messages": message}, configuration)
            for msg in response["messages"]:
                try:
                    print(f"=== TOOL CALLED === {msg.tool_calls[0]['name']}")
                    args = msg.tool_calls[0]["args"]
                    for k, v in args.items():
                        print(f"------------ Argument: {k}: \n{v}")
                    print("=" * 50)
                except Exception:
                    pass
            return

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if user_input.lower() == "clear":
                    # create a new session
                    configuration["configurable"]["thread_id"] = str(uuid.uuid4())
                    print("Conversation history cleared.")
                    continue

                if not user_input:
                    continue

                print("\nAI:\n")

                response = self.agent.invoke({"messages": user_input}, configuration)
                for msg in response["messages"]:
                    try:
                        print(f"Called tool: {msg.tool_calls[0]['name']}")
                        args = msg.tool_calls[0]["args"]
                        for k, v in args.items():
                            print(f"{k}: {v}")
                            print("-" * 50)
                        print("=" * 50)
                    except Exception:
                        pass

                print(response["messages"][-1].content)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.")
