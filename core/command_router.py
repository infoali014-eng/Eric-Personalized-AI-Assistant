from core.executor import execute_action
from plugins.plugin_manager import execute_plugin_action

def _route_only(command):
    """
    Directly routes the command to the appropriate plugin.
    """
    return execute_plugin_action(command)

def route_and_execute(command):
    """
    Routes and executes a command through the reliable unified executor.
    """
    if not isinstance(command, dict):
        return "Invalid command format received"
        
    success, message = execute_action(command, _route_only)
    return message
