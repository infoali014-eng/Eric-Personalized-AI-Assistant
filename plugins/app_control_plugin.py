from plugins.base_plugin import BasePlugin
from actions.app_control import (
    handle_open_app,
    handle_close_app,
    handle_search_web
)

class AppControlPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="AppControl",
            description="Launches, closes, and searches the web inside desktop apps.",
            actions_supported=["OPEN_APP", "CLOSE_APP", "SEARCH_WEB"]
        )

    def execute(self, action_data):
        action = action_data.get("action", "").upper()
        if action == "OPEN_APP":
            return handle_open_app(action_data)
        elif action == "CLOSE_APP":
            return handle_close_app(action_data)
        elif action == "SEARCH_WEB":
            return handle_search_web(action_data)
        return f"Action '{action}' is not supported by AppControlPlugin."
