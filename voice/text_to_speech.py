import pyttsx3
import sys

class TextToSpeech:
    def __init__(self):
        self.engine = None
        try:
            self.engine = pyttsx3.init()
            # Set speed and volume defaults
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 1.0)
            
            # Select default voice (usually English)
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"Warning: Failed to initialize pyttsx3 engine ({e}). Falling back to silent mode.", file=sys.stderr)

    def speak(self, text):
        """Speaks the provided text and prints it to the console."""
        print(f"Assistant: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error during TTS speech execution: {e}", file=sys.stderr)

# Global singleton instance for easy import/use
tts_engine = TextToSpeech()

def speak(text):
    tts_engine.speak(text)
