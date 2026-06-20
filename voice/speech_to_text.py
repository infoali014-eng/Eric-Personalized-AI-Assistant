import speech_recognition as sr
import sys

# Ensure PyAudio is installed; otherwise raise ImportError for clean fallback
try:
    import pyaudio
except ImportError:
    raise ImportError("PyAudio is not installed. Please install PyAudio to use voice features.")

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust energy threshold for silence detection
        self.recognizer.dynamic_energy_threshold = True
        
    def listen(self, timeout=5, phrase_time_limit=10):
        """
        Listens to the microphone and converts speech to text.
        Returns the recognized text (lowercased) or None if listening failed/timed out.
        """
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise once on start or periodically
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"Recognized: {text}")
                    return text.strip().lower()
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    return None
                except sr.RequestError as e:
                    print(f"Google Speech Recognition API error: {e}", file=sys.stderr)
                    return None
        except sr.WaitTimeoutError:
            # Listening timed out without speech starting
            return None
        except Exception as e:
            print(f"Audio input error (is microphone connected?): {e}", file=sys.stderr)
            return None

# Global instance
stt_engine = SpeechToText()

def listen_for_speech(timeout=5, phrase_time_limit=10):
    return stt_engine.listen(timeout, phrase_time_limit)
