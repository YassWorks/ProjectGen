from app.src.agents.code_gen.config.config import get_agent
from app.utils.ascii_art import ASCII_ART
import uuid


class CodeGenAgent:

    def __init__(self, model_name, api_key):

        self.model_name = model_name
        self.api_key = api_key
        self.agent = get_agent(model_name=model_name, api_key=api_key, temp_chat=False)

    def start_chat(self, message: str | None = None):
        """
        Start an isolated chat session with the code generation agent.
        During this session, you do not have access to the other agents.
        Arguments:
            message (str | None): Optional message for single-query sessions.
        """

        tmp_chat_agent = get_agent(
            model_name=self.model_name, api_key=self.api_key, temp_chat=True
        )
        
        print(ASCII_ART)
        print("Type your message and press Enter to chat with the AI.")
        print("Type 'quit', 'exit', or 'q' to end the conversation.")
        print("Type 'clear' to clear the conversation history.")
        print("Current agent: Code Generation")
        print("-" * 50)

        configuration = {
            "configurable": {"thread_id": "abc123"},
            "recursion_limit": 100,
        }

        if message:

            print("\nYou:\n")
            print(message)
            print("\nAI:\n")

            response = tmp_chat_agent.invoke({"messages": message}, configuration)
            for msg in response["messages"]:
                try:
                    print(f"\n=== TOOL CALLED === {msg.tool_calls[0]['name']}\n")
                    args = msg.tool_calls[0]["args"]
                    for k, v in args.items():
                        print(f"------------ ARGUMENT: {k} \n{v}\n")
                    print("=" * 50)
                except Exception:
                    pass
            print(response["messages"][-1].content)

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
                        print(f"\n=== TOOL CALLED === {msg.tool_calls[0]['name']}\n")
                        args = msg.tool_calls[0]["args"]
                        for k, v in args.items():
                            print(f"------------ ARGUMENT: {k} \n{v}\n")
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
