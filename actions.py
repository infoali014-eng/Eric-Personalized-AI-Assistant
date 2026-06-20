import os
import pyautogui

def execute_command(command):
    action = command.get("action")

    if action == "OPEN_APP":
        app = command.get("target")

        if app == "chrome":
            os.startfile("chrome")

        elif app == "vscode":
            os.system("code")

    elif action == "SYSTEM_LOCK":
        os.system("rundll32.exe user32.dll,LockWorkStation")

    elif action == "SYSTEM_SHUTDOWN":
        os.system("shutdown /s /t 5")

    elif action == "CREATE_FOLDER":
        path = command.get("path", "NewFolder")
        os.makedirs(path, exist_ok=True)

    else:
        print("Unknown action:", command)
