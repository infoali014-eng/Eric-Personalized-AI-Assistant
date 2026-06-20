import sys
import json

def run_text_mode():
    from agent import get_command
    from core.command_router import route_and_execute
    from utils.json_cleaner import clean_and_parse_json

    print("🔥 Eric AI Started (Text Mode) - (Type 'exit' to quit)\n")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break

            response = get_command(user_input)
            print("Gemini Raw Output:", response)
            command = clean_and_parse_json(response)
            result = route_and_execute(command)
            print(f"Assistant: {result}")
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")

def run_voice_mode():
    try:
        from core.assistant import EricAssistant
        assistant = EricAssistant()
        assistant.run_loop()
    except Exception as e:
        print(f"Could not start voice assistant: {e}. Falling back to text mode.")
        run_text_mode()

if __name__ == "__main__":
    if "--text" in sys.argv:
        run_text_mode()
    else:
        run_voice_mode()
