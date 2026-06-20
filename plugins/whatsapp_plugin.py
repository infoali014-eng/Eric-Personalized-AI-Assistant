from plugins.base_plugin import BasePlugin
from actions.whatsapp import handle_automated_whatsapp

class WhatsAppPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="WhatsApp",
            description="Automates sending messages on WhatsApp Web with safety approvals.",
            actions_supported=["WHATSAPP_MESSAGE"]
        )

    def execute(self, action_data):
        action = action_data.get("action", "").upper()
        if action == "WHATSAPP_MESSAGE":
            return handle_automated_whatsapp(action_data)
        return f"Action '{action}' is not supported by WhatsAppPlugin."
