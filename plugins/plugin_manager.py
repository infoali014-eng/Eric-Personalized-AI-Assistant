import json
import os
import sys
import importlib

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "registry.json")

class PluginManager:
    """
    Orchestrates dynamic discovery, loading, and execution of capability plugins.
    Ensures all actions are executed modularly.
    """
    def __init__(self):
        self.plugins = []
        self.action_map = {}  # maps action_name string -> plugin instance
        self.load_plugins()

    def load_plugins(self):
        """Loads all plugins declared in registry.json."""
        if not os.path.exists(REGISTRY_PATH):
            print(f"Warning: registry.json not found at {REGISTRY_PATH}", file=sys.stderr)
            return

        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            plugin_paths = data.get("plugins", [])
            for path in plugin_paths:
                self.register_plugin_by_path(path)
        except Exception as e:
            print(f"Error loading plugin registry: {e}", file=sys.stderr)

    def register_plugin_by_path(self, path):
        """Dynamically imports and instantiates a plugin class."""
        try:
            # E.g. "plugins.app_control_plugin.AppControlPlugin"
            parts = path.split(".")
            module_name = ".".join(parts[:-1])
            class_name = parts[-1]
            
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            plugin_instance = plugin_class()
            
            self.plugins.append(plugin_instance)
            
            # Map actions
            for action in plugin_instance.actions_supported:
                self.action_map[action.upper()] = plugin_instance
                
            print(f"Successfully loaded plugin: {plugin_instance.name}")
        except Exception as e:
            print(f"Failed to load plugin from path {path}: {e}", file=sys.stderr)

    def execute_action(self, action_data):
        """
        Routes the action to the correct plugin for execution.
        """
        action = action_data.get("action", "").upper()
        plugin = self.action_map.get(action)
        if not plugin:
            return f"Error: No registered plugin handles action '{action}'."
            
        try:
            return plugin.execute(action_data)
        except Exception as e:
            return f"Error: Plugin {plugin.name} execution failed: {e}"

# Global singleton
manager = PluginManager()

def execute_plugin_action(action_data):
    return manager.execute_action(action_data)
