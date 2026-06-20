from plugins.base_plugin import BasePlugin
from actions.system_control import (
    handle_system_lock,
    handle_system_shutdown,
    handle_system_restart
)

class SystemControlPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="SystemControl",
            description="Controls OS operations including system locking, rebooting, and shutting down.",
            actions_supported=["SYSTEM_LOCK", "SYSTEM_SHUTDOWN", "SYSTEM_RESTART"]
        )

    def execute(self, action_data):
        action = action_data.get("action", "").upper()
        if action == "SYSTEM_LOCK":
            return handle_system_lock(action_data)
        elif action == "SYSTEM_SHUTDOWN":
            return handle_system_shutdown(action_data)
        elif action == "SYSTEM_RESTART":
            return handle_system_restart(action_data)
        return f"Action '{action}' is not supported by SystemControlPlugin."
