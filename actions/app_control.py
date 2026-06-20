import os
import subprocess
import webbrowser
import urllib.parse

def handle_open_app(command):
    app = command.get("target", "").lower()
    if not app:
        return "App target unspecified"

    if app == "chrome":
        os.startfile("chrome")
        return "Opening Chrome"
    elif app == "vscode" or app == "code":
        os.system("code")
        return "Opening VS Code"
    else:
        # Generic app opening fallback
        try:
            subprocess.Popen(f"start {app}", shell=True)
            return f"Attempting to open {app}"
        except Exception as e:
            return f"Failed to open {app}: {e}"

def handle_close_app(command):
    app = command.get("target", "")
    if not app:
        return "App target unspecified"
    
    # Try ending process
    try:
        # Standard taskkill
        subprocess.Popen(f"taskkill /f /im {app}.exe", shell=True)
        return f"Closing {app}"
    except Exception as e:
        return f"Failed to close {app}: {e}"

def handle_search_web(command):
    query = command.get("target", "")
    if not query:
        return "Search query unspecified"
        
    try:
        encoded_query = urllib.parse.quote(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded_query}")
        return f"Searching web for {query}"
    except Exception as e:
        return f"Failed to search web: {e}"

def handle_whatsapp_message(command):
    target = command.get("target", "")
    content = command.get("content", "")
    if not target or not content:
        return "WhatsApp recipient or message content unspecified"
        
    try:
        phone = "".join(filter(str.isdigit, target))
        msg = urllib.parse.quote(content)
        webbrowser.open(f"https://web.whatsapp.com/send?phone={phone}&text={msg}")
        return f"Sending WhatsApp message to {phone}"
    except Exception as e:
        return f"Failed to send WhatsApp message: {e}"
