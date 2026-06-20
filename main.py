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

            from core.command_interceptor import intercept_input
            intercepted, result = intercept_input(user_input)
            if intercepted:
                print(f"Assistant: {result}")
                continue

            from core.task_planner import generate_plan, execute_plan
            plan = generate_plan(result)
            execute_plan(plan)
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

def run_gui_mode():
    try:
        from core.background_agent import BackgroundAgent
        agent = BackgroundAgent()
        agent.run()
    except Exception as e:
        print(f"Could not start GUI Assistant: {e}. Falling back to CLI mode.")
        run_text_mode()

if __name__ == "__main__":
    if "--text" in sys.argv:
        run_text_mode()
    elif "--voice-cli" in sys.argv:
        run_voice_mode()
    else:
        run_gui_mode()
