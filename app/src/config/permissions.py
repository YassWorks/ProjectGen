from app.src.config.ui import AgentUI
from app.utils.constants import CONSOLE_WIDTH
from rich.console import Console
from rich.markdown import Markdown


class PermissionManager:
    
    def __init__(self):
        self.ui = AgentUI(Console(width=CONSOLE_WIDTH))
        self.always_allow = False
        self.always_allowed_tools = set()
    
    def get_permission(self, tool_name: str = None, **kwargs) -> bool:
        if self.always_allow:
            return True
        if tool_name in self.always_allowed_tools:
            return True
        
        message = f"**Attempting to call '{tool_name}'**"
        args = [f"{key}: \n\n```{value}```" for key, value in kwargs.items()]
        if args:
            message += "\n\nWith arguments:\n" + "\n".join(args)
        
        try:
            rendered_message = Markdown(message)
        except:
            rendered_message = message
            
        options = [
            "Yes, allow once",
            "No, deny access (exit now)",
            f"Yes, always allow this tool ({tool_name}) to run",
            "Yes, always allow all tools to run freely (USE AT YOUR OWN RISK)"
        ]

        idx = self.ui.select_option(
            message=rendered_message,
            options=options
        )

        if idx == 0:
            return True
        elif idx == 1:
            return False
        elif idx == 2:
            self.always_allowed_tools.add(tool_name)
            return True
        elif idx == 3:
            self.always_allow = True
            return True

permission_manager = PermissionManager()