import json
from agent import get_command
from actions import execute_command

def run():
    print("🔥 Eric AI Started (Type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        try:
            response = get_command(user_input)
            print("Gemini Raw Output:", response)
            command = json.loads(response)
            execute_command(command)
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n(Please check your internet connection or API key config)\n")

if __name__ == "__main__":
    run()
