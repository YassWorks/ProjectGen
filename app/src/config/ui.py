import traceback
from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown
from typing import Dict, Any
from time import sleep


class AgentUI:
    """Handles all UI rendering for the agent interface."""

    def __init__(self, console: Console):
        self.console = console

    def logo(self, ascii_art: str):
        """Display ASCII art logo."""
        ascii_text = Text(ascii_art)
        ascii_text.stylize("bold magenta", 0, len(ascii_art))
        self.console.print(ascii_text)

    def help(self, model_name: str):
        """Display help instructions and current model."""
        self.console.print("━" * 50, style="yellow")
        self.console.print("[bold yellow] Instructions[/bold yellow]")
        self.console.print()
        self.console.print("   Type your message and press Enter to chat")
        self.console.print(
            "   Type [bold]'quit'[/bold], [bold]'exit'[/bold], or [bold]'q'[/bold] to end the conversation"
        )
        self.console.print("   Type [bold]'clear'[/bold] to clear conversation history")
        self.console.print(
            "   Type [bold]'cls'[/bold], [bold]'clearterm'[/bold], or [bold]'clearscreen'[/bold] to clear terminal"
        )
        self.console.print(f"   Current model: [bold green]{model_name}[/bold green]")
        self.console.print("━" * 50, style="yellow")

    def simulate_thinking(self):
        """Show a thinking animation"""
        self.console.print()
        with self.console.status("[bold green]🧠 AI is thinking...", spinner="dots"):
            sleep(2)

    def tool_call(self, tool_name: str, args: Dict[str, Any]):
        """Display tool call information."""
        self.console.print()
        self.console.print("━" * 42, style="green")
        self.console.print(
            f"  ⚡ [bold green]{tool_name}[/bold green] [dim green]• executing[/dim green]"
        )
        self.console.print("━" * 42, style="dim green")

        for k, v in args.items():
            value_str = str(v)

            # Handle long content
            if len(value_str) > 200:
                # Show first 150 characters and add ellipsis
                value_str = value_str[:150] + "..."

            self.console.print(f"  [cyan]{k}[/cyan] [dim]→[/dim]")

            # Try to render as markdown if it looks like code or markdown
            if "```" in value_str or "\n" in value_str:
                try:
                    markdown_content = Markdown(value_str)
                    self.console.print(markdown_content)
                except:
                    self.console.print(f"    {value_str}")
            else:
                self.console.print(f"    {value_str}")

    def tool_output(self, tool_name: str, content: str):
        """Display tool execution output."""
        output_content = content.strip()
        if output_content.startswith("Output:\n"):
            output_content = output_content[8:]

        self.console.print("━" * 42, style="cyan")
        self.console.print(
            f"  📤 [bold cyan]{tool_name}[/bold cyan] [dim cyan]• completed[/dim cyan]"
        )
        self.console.print("━" * 42, style="dim cyan")

        # Handle very long output
        if len(output_content) > 1000:
            # Show first 800 characters and add ellipsis
            output_content = (
                output_content[:800] + "\n\n[dim cyan]... (output truncated)[/dim cyan]"
            )

        # Try to render as markdown if it looks like code or markdown
        if "```" in output_content or "#" in output_content or "*" in output_content:
            try:
                markdown_content = Markdown(output_content)
                self.console.print(markdown_content)
            except:
                self.console.print(output_content)
        else:
            self.console.print(output_content)
        self.console.print()

    def ai_response(self, content: str):
        """Display AI response with markdown support."""
        self.console.print()
        self.console.print("━" * 52, style="green")
        self.console.print(
            "  🤖 [bold green]AI Assistant[/bold green] [dim green]• responding[/dim green]"
        )
        self.console.print("━" * 52, style="green")
        self.console.print()

        if "```" in content or "#" in content or "*" in content:
            try:
                ai_content = Markdown(content)
            except:
                ai_content = content
        else:
            ai_content = content

        self.console.print(ai_content)
        self.console.print()
        self.console.print()

    def status_message(
        self, title: str, message: str, emoji: str = None, style: str = "blue"
    ):
        """Display a status message with consistent formatting."""
        self.console.print()
        self.console.print("━" * 38, style=style)
        self.console.print(f"  [{style}]{title}[/{style}]")
        emoji_str = f"{emoji} " if emoji else ""
        self.console.print(f"  {emoji_str}[dim]{message}[/dim]")
        self.console.print()

    def goodbye(self):
        """Display goodbye message."""
        self.status_message(
            "👋", "🚪 Goodbye!", "Thanks for using the AI Assistant!", "bright_blue"
        )

    def history_cleared(self):
        """Display history cleared message."""
        self.status_message(
            "✨",
            "🧹 History Cleared",
            "Conversation history has been cleared!",
            "green",
        )

    def session_interrupted(self):
        """Display session interrupted message."""
        self.status_message("🛑", "⚠️ Session Interrupted", "Interrupted by user", "red")

    def recursion_warning(self):
        """Display recursion warning with user prompt."""
        self.console.print()
        self.console.print("━" * 45, style="bold yellow")
        self.console.print(
            "  [bold yellow]⚠️  Agent Running Extended Session[/bold yellow]"
        )
        self.console.print("━" * 45, style="dim yellow")
        self.console.print()
        self.console.print("  [dim]The agent has been processing for a while.[/dim]")
        self.console.print(
            "  Would you like to [bold]continue[/bold] or [bold cyan]refine your prompt[/bold cyan]?"
        )
        self.console.print()
        self.console.print()

    def error(self, error_msg: str):
        """Display error message."""
        self.status_message(
            title="⚠️ Error Occurred",
            message=f"Error: {error_msg}\n[dim]Please try again...",
            emoji="❌",
            style="red",
        )

    def dev_traceback(self):
        """Display traceback for development purposes."""
        traceback.print_exc(file=self.console.file)
