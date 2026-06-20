from plugins.base_plugin import BasePlugin
from actions.file_manager import (
    handle_create_file,
    handle_delete_file,
    handle_create_folder,
    handle_delete_folder,
    handle_rename_file
)

class FileManagerPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="FileManager",
            description="Manages directories and files (creation, deletion, and renaming).",
            actions_supported=["CREATE_FILE", "DELETE_FILE", "CREATE_FOLDER", "DELETE_FOLDER", "RENAME_FILE"]
        )

    def execute(self, action_data):
        action = action_data.get("action", "").upper()
        if action == "CREATE_FILE":
            return handle_create_file(action_data)
        elif action == "DELETE_FILE":
            return handle_delete_file(action_data)
        elif action == "CREATE_FOLDER":
            return handle_create_folder(action_data)
        elif action == "DELETE_FOLDER":
            return handle_delete_folder(action_data)
        elif action == "RENAME_FILE":
            return handle_rename_file(action_data)
        return f"Action '{action}' is not supported by FileManagerPlugin."
