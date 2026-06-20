from voice.speech_to_text import listen_for_speech

WAKE_WORDS = ["hey eric", "eric", "hello eric", "okay eric"]

def detect_wake_word():
    """
    Listens briefly and checks if the user said one of the wake words.
    Returns True if detected, False otherwise.
    """
    # Use shorter timeout for responsive wake word checking
    phrase = listen_for_speech(timeout=2, phrase_time_limit=3)
    if phrase:
        for word in WAKE_WORDS:
            if word in phrase:
                return True
    return False
