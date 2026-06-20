import os
import json
import re
import sys
from core.command_router import route_and_execute
from voice.text_to_speech import speak

WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workflows")
os.makedirs(WORKFLOWS_DIR, exist_ok=True)

class WorkflowEngine:
    """
    Manages automated task chains (workflows).
    Detects repeating action logs to create workflows and handles execution of workflows.
    """
    def __init__(self):
        pass

    def run_workflow_by_name(self, name):
        """Loads and runs the steps in the specified workflow file."""
        # Clean workflow name
        name_clean = name.strip().lower().replace(" ", "_")
        file_path = os.path.join(WORKFLOWS_DIR, f"{name_clean}.json")
        
        if not os.path.exists(file_path):
            return f"Workflow '{name}' not found."
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                workflow_data = json.load(f)
                
            steps = workflow_data.get("steps", [])
            speak(f"Starting workflow: {workflow_data.get('name', name_clean)}")
            
            # Confirm dangerous workflows if they contain dangerous steps
            # Since route_and_execute automatically triggers confirmations through core/executor,
            # we are fully covered and safe!
            for step in steps:
                step_num = step.get("step", "?")
                action = step.get("action", "")
                speak(f"Workflow step {step_num}: {action}")
                
                result = route_and_execute(step)
                speak(result)
                
                if "fail" in result.lower() or "error" in result.lower():
                    return f"Workflow execution halted: Step {step_num} failed."
                    
            return "Workflow executed successfully."
        except Exception as e:
            return f"Failed to execute workflow: {e}"

    def learn_workflows_from_history(self):
        """
        Analyzes past command logs to detect repeated sequential actions
        and automatically compiles them into workflows.
        """
        try:
            from memory.memory_db import get_all_memories, insert_memory
            memories = get_all_memories()
            
            # Extract list of executed commands in chronological order (reverse of database retrieval)
            commands = [m[1] for m in reversed(memories) if m[0] == "command"]
            if len(commands) < 4:
                return
                
            # We look for repeated sequence patterns of length 2 or 3
            # E.g. ["Executed OPEN_APP on chrome", "Executed SEARCH_WEB on news"]
            patterns = {}
            for i in range(len(commands) - 2):
                seq2 = (commands[i], commands[i+1])
                seq3 = (commands[i], commands[i+1], commands[i+2])
                
                patterns[seq2] = patterns.get(seq2, 0) + 1
                patterns[seq3] = patterns.get(seq3, 0) + 1
                
            # Find any sequence that has been executed at least 2 times
            for seq, count in patterns.items():
                if count >= 2:
                    # Construct workflow name based on components
                    actions = []
                    steps = []
                    for idx, cmd_desc in enumerate(seq):
                        # Extract action and target
                        match = re.match(r"Executed (\w+)(?: on (.+))?", cmd_desc)
                        if match:
                            act = match.group(1)
                            targ = match.group(2) or ""
                            actions.append(act.lower())
                            steps.append({
                                "step": idx + 1,
                                "action": act,
                                "target": targ
                            })
                            
                    if not steps:
                        continue
                        
                    wf_name = "_".join(actions[:3]) + "_workflow"
                    wf_file = os.path.join(WORKFLOWS_DIR, f"{wf_name}.json")
                    
                    if not os.path.exists(wf_file):
                        # Save workflow file
                        workflow_data = {
                            "name": wf_name,
                            "steps": steps
                        }
                        with open(wf_file, "w", encoding="utf-8") as f:
                            json.dump(workflow_data, f, indent=2)
                            
                        # Add to memories as an auto-suggested habit
                        msg = f"Created workflow auto-suggest: run my {wf_name.replace('_', ' ')}"
                        insert_memory("preference", f"Auto-workflow: {wf_name}")
                        print(f"💡 Auto-learned Workflow: {wf_name}")
                        speak(f"I noticed you often perform this sequence. I have automated it as: {wf_name.replace('_', ' ')}")
                        
        except Exception as e:
            print(f"Error in learning workflows: {e}", file=sys.stderr)

    def intercept_workflow_command(self, user_input):
        """
        Intercepts commands related to running workflows.
        Returns result string or None.
        """
        user_input_lower = user_input.lower().strip()
        
        # Match "run my X workflow" or "run X workflow"
        match = re.match(r"^run\s+(?:my\s+)?([\w\s]+?)\s+workflow$", user_input_lower)
        if match:
            wf_name = match.group(1).strip()
            result = self.run_workflow_by_name(wf_name)
            return result
            
        return None

# Global instance
workflow_engine = WorkflowEngine()
