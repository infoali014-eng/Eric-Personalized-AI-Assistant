import time
import sys
from voice.speech_to_text import listen_for_speech
from voice.text_to_speech import speak
from voice.wake_word import detect_wake_word
from agent import get_command
from utils.json_cleaner import clean_and_parse_json
from core.command_router import route_and_execute

from memory.memory_manager import process_memory_command
from vision.screen_reader import capture_and_analyze_screen
from vision.smart_screen_agent import capture_and_assist

class EricAssistant:
    def __init__(self):
        self.mode = "IDLE"  # IDLE or ACTIVE
        self.last_active_time = time.time()
        self.inactivity_timeout = 15.0  # seconds before returning to IDLE

    def process_command(self, user_speech):
        """Sends user speech to Gemini, handles retries, and executes the action."""
        print(f"Processing command: '{user_speech}'")
        
        user_speech_clean = user_speech.lower().strip()
        
        # Intercept Assist Mode / help commands
        if "help me fix this" in user_speech_clean or "assist mode" in user_speech_clean:
            speak("Activating Assist Mode.")
            result = capture_and_assist()
            speak(result)
            return
            
        # Intercept screen understanding commands
        if "look at my screen" in user_speech_clean or "look at screen" in user_speech_clean:
            speak("Let me look at your screen.")
            analysis = capture_and_analyze_screen()
            speak(analysis)
            return
            
        # Intercept memory commands
        memory_result = process_memory_command(user_speech)
        if memory_result is not None:
            speak(memory_result)
            return
        
        # Generate and execute task plan
        try:
            from core.task_planner import generate_plan, execute_plan
            plan = generate_plan(user_speech)
            execute_plan(plan)
        except Exception as e:
            speak(f"Could not execute task plan: {e}")

    def run_loop(self):
        print("🔥 Eric AI Voice Assistant Started (Press Ctrl+C to quit)\n")
        speak("Eric AI is online.")
        
        while True:
            try:
                if self.mode == "IDLE":
                    # Check for wake word
                    print("[Mode: IDLE] Listening for wake word...")
                    if detect_wake_word():
                        speak("Yes?")
                        self.mode = "ACTIVE"
                        self.last_active_time = time.time()
                
                elif self.mode == "ACTIVE":
                    print("[Mode: ACTIVE] Listening for commands...")
                    user_speech = listen_for_speech(timeout=5, phrase_time_limit=8)
                    
                    if user_speech:
                        # Reset inactivity timer and process command
                        self.last_active_time = time.time()
                        
                        if "exit" in user_speech or "quit" in user_speech:
                            speak("Goodbye.")
                            break
                        
                        self.process_command(user_speech)
                    else:
                        # Check for inactivity timeout
                        elapsed = time.time() - self.last_active_time
                        if elapsed >= self.inactivity_timeout:
                            print("Inactivity timeout reached. Returning to IDLE mode.")
                            speak("Going to sleep mode")
                            self.mode = "IDLE"
                            
            except KeyboardInterrupt:
                speak("Shutting down assistant.")
                break
            except Exception as e:
                print(f"Error in main loop: {e}", file=sys.stderr)
                # Fail-safe sleep to prevent rapid infinite looping in case of persistent errors
                time.sleep(1)

if __name__ == "__main__":
    assistant = EricAssistant()
    assistant.run_loop()
