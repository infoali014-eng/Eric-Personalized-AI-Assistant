import time
import sys
from voice.speech_to_text import listen_for_speech
from voice.text_to_speech import speak
from voice.wake_word import detect_wake_word
from agent import get_command
from utils.json_cleaner import clean_and_parse_json
from core.command_router import route_and_execute

class EricAssistant:
    def __init__(self):
        self.mode = "IDLE"  # IDLE or ACTIVE
        self.last_active_time = time.time()
        self.inactivity_timeout = 15.0  # seconds before returning to IDLE

    def process_command(self, user_speech):
        """Sends user speech to Gemini, handles retries, and executes the action."""
        print(f"Processing command: '{user_speech}'")
        
        # Try once
        response = get_command(user_speech)
        print(f"Gemini Raw Response: {response}")
        
        try:
            command = clean_and_parse_json(response)
        except ValueError as e:
            print(f"Invalid JSON returned. Retrying once... Error: {e}")
            # Retry once
            response = get_command(user_speech)
            print(f"Gemini Retry Raw Response: {response}")
            try:
                command = clean_and_parse_json(response)
            except ValueError:
                speak("I didn't understand that instruction")
                return

        # Execute and speak the confirmation
        tts_response = route_and_execute(command)
        speak(tts_response)

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
