class BasePlugin:
    """
    Abstract base class for all Eric AI plugins.
    All custom plugins must inherit from this class.
    """
    def __init__(self, name, description, actions_supported):
        self.name = name
        self.description = description
        self.actions_supported = actions_supported  # list of action name strings

    def execute(self, action_data):
        """
        Executes the supported action.
        Returns: text response of the result.
        """
        raise NotImplementedError("Plugins must implement the execute method.")
