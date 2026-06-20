import os
import sys
import json
import ctypes
import shutil
import subprocess
import webbrowser
import urllib.parse
from google import genai
from google.genai import types

# Supported Actions list for reference
SUPPORTED_ACTIONS = [
    "OPEN_APP",
    "CLOSE_APP",
    "CREATE_FILE",
    "DELETE_FILE",
    "CREATE_FOLDER",
    "DELETE_FOLDER",
    "RENAME_FILE",
    "SYSTEM_LOCK",
    "SYSTEM_SHUTDOWN",
    "SYSTEM_RESTART",
    "SEARCH_WEB",
    "WHATSAPP_MESSAGE"
]

def get_gemini_client():
    """Initializes and returns the Gemini client using environmental API key."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Gemini Client: {e}", file=sys.stderr)
        return None

def get_action_from_llm(client, user_instruction):
    """Uses Gemini API to convert user instruction into action JSON."""
    prompt = f"""You are "Eric AI", a local desktop assistant that converts user instructions into structured executable commands.

You do NOT chat normally.

Your job is ONLY to:
1. Understand user intent
2. Convert it into a valid ACTION JSON
3. Never include explanations
4. Never add extra text

---

SUPPORTED ACTIONS:

1. OPEN_APP
2. CLOSE_APP
3. CREATE_FILE
4. DELETE_FILE
5. CREATE_FOLDER
6. DELETE_FOLDER
7. RENAME_FILE
8. SYSTEM_LOCK
9. SYSTEM_SHUTDOWN
10. SYSTEM_RESTART
11. SEARCH_WEB
12. WHATSAPP_MESSAGE

---

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "action": "ACTION_NAME",
  "target": "optional target app/file/person",
  "content": "optional message or file content",
  "path": "optional file path"
}}

---

RULES:
- If user says "open chrome" → OPEN_APP with target "chrome"
- If user says "lock laptop" → SYSTEM_LOCK
- If user says "create file test.txt" → CREATE_FILE
- If user gives message → use WHATSAPP_MESSAGE
- If unsure → return:
  {{ "action": "UNKNOWN" }}

NEVER explain anything.
NEVER respond in natural language.
ONLY return JSON.

User Instruction: {user_instruction}
"""
    try:
        # Use gemini-2.5-flash as the default model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        return json.dumps({"action": "UNKNOWN"})

def execute_action(action_json_str):
    """Parses and executes the action specified in the JSON string."""
    try:
        action_data = json.loads(action_json_str)
    except Exception as e:
        print(f"Failed to parse Action JSON: {e}", file=sys.stderr)
        return False

    action = action_data.get("action")
    target = action_data.get("target", "")
    content = action_data.get("content", "")
    path = action_data.get("path", "")

    print(f"Executing Action: {action}")
    if target:
        print(f"  Target: {target}")
    if content:
        print(f"  Content: {content}")
    if path:
        print(f"  Path: {path}")

    if action == "OPEN_APP":
        if not target:
            print("Error: Target application not specified.", file=sys.stderr)
            return False
        # Windows command to open application
        subprocess.Popen(f"start {target}", shell=True)
        return True

    elif action == "CLOSE_APP":
        if not target:
            print("Error: Target application not specified.", file=sys.stderr)
            return False
        # Terminate process on Windows
        subprocess.Popen(f"taskkill /f /im {target}.exe", shell=True)
        return True

    elif action == "CREATE_FILE":
        filepath = path or target
        if not filepath:
            print("Error: Path or target file name must be specified.", file=sys.stderr)
            return False
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created file: {filepath}")
            return True
        except Exception as e:
            print(f"Failed to create file {filepath}: {e}", file=sys.stderr)
            return False

    elif action == "DELETE_FILE":
        filepath = path or target
        if not filepath:
            print("Error: Path or target file name must be specified.", file=sys.stderr)
            return False
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Deleted file: {filepath}")
                return True
            else:
                print(f"File not found: {filepath}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"Failed to delete file {filepath}: {e}", file=sys.stderr)
            return False

    elif action == "CREATE_FOLDER":
        folderpath = path or target
        if not folderpath:
            print("Error: Path or target folder name must be specified.", file=sys.stderr)
            return False
        try:
            os.makedirs(folderpath, exist_ok=True)
            print(f"Created folder: {folderpath}")
            return True
        except Exception as e:
            print(f"Failed to create folder {folderpath}: {e}", file=sys.stderr)
            return False

    elif action == "DELETE_FOLDER":
        folderpath = path or target
        if not folderpath:
            print("Error: Path or target folder name must be specified.", file=sys.stderr)
            return False
        try:
            if os.path.exists(folderpath):
                shutil.rmtree(folderpath, ignore_errors=True)
                print(f"Deleted folder: {folderpath}")
                return True
            else:
                print(f"Folder not found: {folderpath}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"Failed to delete folder {folderpath}: {e}", file=sys.stderr)
            return False

    elif action == "RENAME_FILE":
        if not path or not target:
            print("Error: Both current path and target name must be specified for rename.", file=sys.stderr)
            return False
        try:
            os.rename(path, target)
            print(f"Renamed {path} to {target}")
            return True
        except Exception as e:
            print(f"Failed to rename {path} to {target}: {e}", file=sys.stderr)
            return False

    elif action == "SYSTEM_LOCK":
        print("Locking system...")
        ctypes.windll.user32.LockWorkStation()
        return True

    elif action == "SYSTEM_SHUTDOWN":
        print("Shutting down system...")
        os.system("shutdown /s /t 1")
        return True

    elif action == "SYSTEM_RESTART":
        print("Restarting system...")
        os.system("shutdown /r /t 1")
        return True

    elif action == "SEARCH_WEB":
        if not target:
            print("Error: Search query not specified.", file=sys.stderr)
            return False
        query = urllib.parse.quote(target)
        url = f"https://www.google.com/search?q={query}"
        print(f"Searching web for: {target}")
        webbrowser.open(url)
        return True

    elif action == "WHATSAPP_MESSAGE":
        if not target or not content:
            print("Error: Both target (phone number) and content (message) must be specified.", file=sys.stderr)
            return False
        # Remove non-digit characters from the phone number
        phone = "".join(filter(str.isdigit, target))
        msg = urllib.parse.quote(content)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={msg}"
        print(f"Sending WhatsApp message to {phone}...")
        webbrowser.open(url)
        return True

    else:
        print(f"Action '{action}' is not supported or unknown.", file=sys.stderr)
        return False

def main():
    if len(sys.argv) > 1:
        # Command line mode
        user_instruction = " ".join(sys.argv[1:])
        client = get_gemini_client()
        if not client:
            sys.exit(1)
        action_json = get_action_from_llm(client, user_instruction)
        print("Gemini Output:")
        print(action_json)
        print("-" * 40)
        execute_action(action_json)
    else:
        # Interactive mode loop
        print("=== Eric AI Local Desktop Assistant ===")
        print("Type exit or quit to end.")
        client = get_gemini_client()
        if not client:
            print("Please set GEMINI_API_KEY environment variable to use AI mode.")
        
        while True:
            try:
                user_instruction = input("\nHow can I help you? > ").strip()
                if not user_instruction:
                    continue
                if user_instruction.lower() in ["exit", "quit"]:
                    break
                
                if client:
                    action_json = get_action_from_llm(client, user_instruction)
                else:
                    # Fallback to local parsing or warn
                    print("AI client offline. Run with local mocked JSON or set api key.")
                    continue

                print(f"Decoded Action: {action_json}")
                execute_action(action_json)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
