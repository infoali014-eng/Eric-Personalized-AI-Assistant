import sys
from actions.system_control import (
    handle_system_lock,
    handle_system_shutdown,
    handle_system_restart
)
from actions.app_control import (
    handle_open_app,
    handle_close_app,
    handle_search_web,
    handle_whatsapp_message
)
from actions.file_manager import (
    handle_create_file,
    handle_delete_file,
    handle_create_folder,
    handle_delete_folder,
    handle_rename_file
)

from actions.whatsapp import handle_automated_whatsapp

from core.executor import execute_action

def _route_only(command):
    """
    Directly routes the command to the correct action handler.
    """
    action = command.get("action", "").upper()
    
    if action == "OPEN_APP":
        return handle_open_app(command)
        
    elif action == "CLOSE_APP":
        return handle_close_app(command)
        
    elif action == "SEARCH_WEB":
        return handle_search_web(command)
        
    elif action == "WHATSAPP_MESSAGE":
        return handle_automated_whatsapp(command)
        
    elif action == "SYSTEM_LOCK":
        return handle_system_lock(command)
        
    elif action == "SYSTEM_SHUTDOWN":
        return handle_system_shutdown(command)
        
    elif action == "SYSTEM_RESTART":
        return handle_system_restart(command)
        
    elif action == "CREATE_FILE":
        return handle_create_file(command)
        
    elif action == "DELETE_FILE":
        return handle_delete_file(command)
        
    elif action == "CREATE_FOLDER":
        return handle_create_folder(command)
        
    elif action == "DELETE_FOLDER":
        return handle_delete_folder(command)
        
    elif action == "RENAME_FILE":
        return handle_rename_file(command)
        
    elif action == "UNKNOWN" or not action:
        return "I am not sure how to handle that instruction"
        
    else:
        return f"Unknown action: {action}"

def route_and_execute(command):
    """
    Routes and executes a command through the reliable unified executor.
    """
    if not isinstance(command, dict):
        return "Invalid command format received"
        
    success, message = execute_action(command, _route_only)
    return message
