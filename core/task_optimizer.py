import os

def optimize_plan(plan):
    """
    Analyzes task plans, eliminates redundant steps, and combines actions
    to increase execution speed and system safety.
    """
    steps = plan.get("steps", [])
    if not steps:
        return plan

    optimized_steps = []
    skip_steps = set()

    for idx, step in enumerate(steps):
        if idx in skip_steps:
            continue
            
        action = step.get("action", "").upper()
        target = step.get("target", "")
        
        # Optimization 1: Combine open chrome + web search
        if action == "OPEN_APP" and target.lower() == "chrome":
            # Check if next step is a web search
            next_is_search = False
            for next_idx in range(idx + 1, len(steps)):
                next_step = steps[next_idx]
                if next_step.get("action", "").upper() == "SEARCH_WEB":
                    next_is_search = True
                    break
            
            if next_is_search:
                print("⚡ Optimizer: Combined open chrome and search_web into a single search action.")
                # We skip this open app step entirely since web search opens chrome automatically
                continue

        # Optimization 2: Redundant CREATE_FOLDER before CREATE_FILE in the same directory path
        if action == "CREATE_FOLDER" and target:
            # Check if next step creates a file inside this folder
            next_creates_file_inside = False
            for next_idx in range(idx + 1, len(steps)):
                next_step = steps[next_idx]
                next_action = next_step.get("action", "").upper()
                next_target = next_step.get("target", "") or next_step.get("path", "")
                
                if next_action == "CREATE_FILE" and next_target:
                    # Check if next target lies inside the folder we want to create
                    norm_folder = os.path.normpath(target).lower()
                    norm_file = os.path.normpath(next_target).lower()
                    if norm_file.startswith(norm_folder):
                        next_creates_file_inside = True
                        break
            
            if next_creates_file_inside:
                print(f"⚡ Optimizer: Removed redundant folder creation '{target}' (file creation will auto-create directories).")
                continue

        # Optimization 3: Duplicate action consolidation (e.g. locks or shutdowns)
        if action in ["SYSTEM_LOCK", "SYSTEM_SHUTDOWN", "SYSTEM_RESTART"]:
            # Check if there is already a matching action in optimized list
            is_dup = False
            for prev_step in optimized_steps:
                if prev_step.get("action", "").upper() == action:
                    is_dup = True
                    break
            if is_dup:
                print(f"⚡ Optimizer: Removed duplicate system action: {action}.")
                continue

        optimized_steps.append(step)

    # Re-index steps
    for new_idx, step in enumerate(optimized_steps):
        step["step"] = new_idx + 1

    plan["steps"] = optimized_steps
    return plan
