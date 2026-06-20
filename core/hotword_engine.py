import speech_recognition as sr
import sys
import time

class HotwordEngine:
    """
    Continuous background streaming audio wake-word listener.
    Runs on a background thread and triggers a callback when "hey eric" is detected.
    """
    def __init__(self, callback):
        self.callback = callback
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.stop_listening_fn = None
        
        # Verify PyAudio presence
        try:
            import pyaudio
        except ImportError:
            raise ImportError("PyAudio is not installed. Hotword Engine requires PyAudio.")
            
    def start(self):
        """Starts continuous streaming microphone wake-word listener."""
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                # Adjust once for background noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                
            # listen_in_background runs in a background thread automatically
            self.stop_listening_fn = self.recognizer.listen_in_background(
                self.microphone, self.audio_callback, phrase_time_limit=3
            )
            print("Hotword Engine successfully started.")
            return True
        except Exception as e:
            print(f"Failed to start Hotword Engine: {e}", file=sys.stderr)
            return False

    def stop(self):
        """Stops the streaming background thread."""
        if self.stop_listening_fn:
            self.stop_listening_fn(wait_for_stop=False)
            self.stop_listening_fn = None
            print("Hotword Engine stopped.")

    def audio_callback(self, recognizer, audio):
        """Callback function called by SpeechRecognition whenever a phrase is spoken."""
        try:
            text = recognizer.recognize_google(audio).strip().lower()
            print(f"[Hotword Listener] Recognized phrase: '{text}'")
            if "hey eric" in text or "eric" in text:
                print("[Hotword Listener] Wake word matched!")
                self.callback()
        except sr.UnknownValueError:
            # Audio was not clear/no speech, keep listening silently
            pass
        except Exception as e:
            print(f"Error in background hotword recognition: {e}", file=sys.stderr)
