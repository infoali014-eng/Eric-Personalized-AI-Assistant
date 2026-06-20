import os
import sys
import logging
import time
from voice.text_to_speech import speak

# Configure logging
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "eric_execution.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

DANGEROUS_ACTIONS = {"SYSTEM_SHUTDOWN", "SYSTEM_RESTART", "DELETE_FILE", "DELETE_FOLDER", "WHATSAPP_MESSAGE"}

def ask_user_confirmation(action_name):
    """Asks the user for confirmation before performing dangerous actions."""
    speak(f"Danger: You are requesting {action_name}. Do you want to proceed?")
    
    # Try voice input first
    try:
        from voice.speech_to_text import listen_for_speech
        print("Waiting for confirmation voice input...")
        user_response = listen_for_speech(timeout=5, phrase_time_limit=4)
        if user_response:
            response_clean = user_response.strip().lower()
            if any(yes in response_clean for yes in ["yes", "yeah", "yep", "sure", "proceed", "okay", "ok"]):
                return True
            if any(no in response_clean for no in ["no", "nope", "cancel", "don't", "stop"]):
                return False
    except Exception:
        pass
        
    # Fallback to console input confirmation
    try:
        console_input = input("Confirm execution (yes/no): ").strip().lower()
        return console_input in ["yes", "y", "yeah", "ok", "proceed"]
    except Exception:
        return False

def execute_action(action_data, run_handler_callback):
    """
    Executes an action cleanly, handling retries, logging, safe mode, and feedback.
    Returns: (success_bool, message_str)
    """
    if not isinstance(action_data, dict):
        return False, "Invalid action command format"

    action = action_data.get("action", "").upper()
    target = action_data.get("target", "")
    
    # 1. Logging the attempt
    logging.info(f"Attempting action: {action} with target: {target}")
    
    # 2. Safe Mode check for dangerous actions
    if action in DANGEROUS_ACTIONS:
        confirmed = ask_user_confirmation(action)
        if not confirmed:
            msg = f"Action {action} aborted by user."
            logging.info(msg)
            return False, msg

    # 3. Execution with Retry System (retry once)
    success = False
    result_msg = ""
    attempts = 2
    
    for attempt in range(1, attempts + 1):
        try:
            logging.info(f"Execution attempt {attempt} for {action}...")
            # Call the callback handler
            result_msg = run_handler_callback(action_data)
            
            # Check for errors in return message
            if "fail" in result_msg.lower() or "error" in result_msg.lower():
                success = False
            else:
                success = True
                
            if success:
                break
        except Exception as e:
            result_msg = f"Exception occurred: {e}"
            success = False
            
        if not success and attempt < attempts:
            logging.warning(f"Attempt {attempt} failed: {result_msg}. Retrying once...")
            time.sleep(1) # Small cooling time before retry

    # 4. Log completion status
    status_str = "SUCCESS" if success else "FAILURE"
    logging.info(f"Action {action} completed with status: {status_str}. Message: {result_msg}")
    
    return success, result_msg
