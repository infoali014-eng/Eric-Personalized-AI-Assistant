import sys
from memory.memory_manager import process_memory_command
from core.workflow_engine import workflow_engine

class CommandInterceptor:
    """
    Central command interceptor representing the first layer of input validation.
    Normalizes inputs, intercepts workflow/memory triggers, and ensures system safety.
    """
    def __init__(self):
        pass

    def intercept_and_normalize(self, user_input):
        """
        Normalizes spacing, spelling, and intercepts specialized commands.
        Returns:
            (handled_bool, response_message_or_normalized_input)
        """
        if not user_input or not user_input.strip():
            return True, "No input provided."

        normalized = user_input.strip()
        # Remove trailing periods or question marks
        normalized = normalized.rstrip(".?!")
        
        normalized_lower = normalized.lower()

        # 1. Intercept Workflows
        wf_result = workflow_engine.intercept_workflow_command(normalized)
        if wf_result is not None:
            return True, wf_result

        # 2. Intercept Memory
        memory_result = process_memory_command(normalized)
        if memory_result is not None:
            return True, memory_result

        # 3. Intercept Screen Reader and Assist Mode
        if "help me fix this" in normalized_lower or "assist mode" in normalized_lower:
            from vision.smart_screen_agent import capture_and_assist
            result = capture_and_assist()
            return True, result

        if "look at my screen" in normalized_lower or "look at screen" in normalized_lower:
            from vision.screen_reader import capture_and_analyze_screen
            from voice.text_to_speech import speak
            analysis = capture_and_analyze_screen()
            speak(analysis)
            return True, analysis

        # Returns False to indicate it was not intercepted and should continue to task planning
        return False, normalized

# Global instance
interceptor = CommandInterceptor()

def intercept_input(user_input):
    return interceptor.intercept_and_normalize(user_input)
