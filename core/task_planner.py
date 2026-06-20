import json
import sys
from agent import get_command
from utils.json_cleaner import clean_and_parse_json
from core.command_router import route_and_execute
from memory.memory_manager import process_memory_command
from voice.text_to_speech import speak

def generate_plan(user_input):
    """
    Calls Gemini using the task planning prompt and returns a parsed plan dictionary.
    Supports retrying once if the returned plan is invalid.
    """
    print(f"Generating execution plan for: '{user_input}'")
    
    response = get_command(user_input)
    print(f"Gemini Raw Plan Response: {response}")
    
    try:
        plan = clean_and_parse_json(response)
        return plan
    except ValueError as e:
        print(f"Invalid plan format received. Retrying once... Error: {e}")
        # Retry once
        response = get_command(user_input)
        print(f"Gemini Retry Raw Plan Response: {response}")
        try:
            plan = clean_and_parse_json(response)
            return plan
        except ValueError as re_err:
            raise ValueError(f"Failed to generate a valid plan: {re_err}")

def update_memory_from_actions(command):
    """
    Analyzes successfully executed actions to learn user patterns and preferences automatically.
    """
    action = command.get("action")
    target = command.get("target")
    if not action:
        return
        
    from memory.memory_db import insert_memory, get_all_memories
    
    # 1. Log the action to memory
    action_log = f"Executed {action}"
    if target:
        action_log += f" on {target}"
    insert_memory("command", action_log)
    
    # 2. Learn preferences from patterns (e.g. app preference)
    if action == "OPEN_APP" and target:
        target_lower = target.lower()
        memories = get_all_memories()
        
        # Count how many times this app has been opened
        open_logs = [m[1] for m in memories if m[0] == "command" and m[1].startswith("Executed OPEN_APP on ")]
        app_opens = [log.replace("Executed OPEN_APP on ", "").lower() for log in open_logs]
        
        open_count = app_opens.count(target_lower)
        
        if open_count >= 3:
            preference_desc = f"User prefers {target} as default application"
            # Check if this preference is already saved
            existing_prefs = [m[1].lower() for m in memories if m[0] == "preference"]
            if preference_desc.lower() not in existing_prefs:
                insert_memory("preference", preference_desc)
                print(f"💡 Auto-learned preference: {preference_desc}")

def execute_plan(plan):
    """
    Executes a multi-step task plan sequentially.
    Optimizes steps first, stops execution if any step fails, and triggers workflow learning.
    """
    from core.task_optimizer import optimize_plan
    from core.workflow_engine import workflow_engine
    
    # 1. Optimize plan steps
    plan = optimize_plan(plan)
    
    task = plan.get("task", "Unnamed Task")
    steps = plan.get("steps", [])
    
    speak(f"Starting optimized plan execution for task: {task}")
    
    for step_data in steps:
        step_num = step_data.get("step")
        action = step_data.get("action")
        target = step_data.get("target", "")
        
        speak(f"Running step {step_num}: {action} {target}")
        
        try:
            # Route and execute step
            result_msg = route_and_execute(step_data)
            speak(result_msg)
            
            # Check if execution failed
            if "fail" in result_msg.lower() or "error" in result_msg.lower():
                speak(f"Execution halted: Step {step_num} failed.")
                return False
                
            # Learn from successful action
            update_memory_from_actions(step_data)
            
        except Exception as e:
            speak(f"Execution halted: Exception in step {step_num}. Error: {e}")
            return False
            
    # 2. Check for repeating patterns to automate workflows
    workflow_engine.learn_workflows_from_history()
    
    speak("All task plan steps executed successfully.")
    return True
