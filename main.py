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

            # Intercept screen understanding commands
            user_input_clean = user_input.lower().strip()
            if "help me fix this" in user_input_clean or "assist mode" in user_input_clean:
                print("Assistant: Activating Assist Mode...")
                from vision.smart_screen_agent import capture_and_assist
                result = capture_and_assist()
                print(f"Assistant: {result}")
                continue

            if "look at my screen" in user_input_clean or "look at screen" in user_input_clean:
                print("Assistant: Let me look at your screen...")
                from vision.screen_reader import capture_and_analyze_screen
                analysis = capture_and_analyze_screen()
                print(f"Assistant: {analysis}")
                continue

            # Intercept memory commands
            from memory.memory_manager import process_memory_command
            memory_result = process_memory_command(user_input)
            if memory_result is not None:
                print(f"Assistant: {memory_result}")
                continue

            from core.task_planner import generate_plan, execute_plan
            plan = generate_plan(user_input)
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

if __name__ == "__main__":
    if "--text" in sys.argv:
        run_text_mode()
    else:
        run_voice_mode()
