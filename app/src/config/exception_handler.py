import langgraph
import openai
from typing import Callable, Any
from app.src.config.permissions import PermissionDeniedException
from app.src.config.ui import AgentUI


class AgentExceptionHandler:
    """Centralized exception handling for agent operations."""

    @staticmethod
    def handle_agent_exceptions(
        operation: Callable,
        ui: AgentUI,
        propagate: bool = False,
        continue_prompt: str = "Continue where you left. Don't repeat anything already done.",
    ) -> tuple[Any, bool]:
        """Handle common agent exceptions with consistent behavior.

        Args:
            operation: Function to execute that may raise exceptions
            ui: UI handler for displaying messages
            propagate: Whether to re-raise exceptions
            continue_prompt: Prompt to use for recursion recovery

        Returns:
            Tuple of (result, should_continue)
        """
        try:
            return operation(), False

        except PermissionDeniedException:
            if propagate:
                raise
            ui.error("Permission denied")
            return None, False

        except langgraph.errors.GraphRecursionError:
            if propagate:
                raise
            ui.warning("Agent processing took longer than expected")
            if ui.confirm("Continue from where left off?", default=True):
                return continue_prompt, True
            return None, False

        except openai.RateLimitError:
            if propagate:
                raise
            ui.error("Rate limit exceeded. Please try again later")
            return None, False

        except Exception as e:
            if propagate:
                raise
            ui.error(f"An unexpected error occurred: {e}")
            return None, False

    @staticmethod
    def with_retry(
        operation: Callable,
        ui: Any,
        max_retries: int = 3,
        retry_message: str = "Retrying operation...",
    ) -> Any:
        """Execute operation with retry logic for transient failures.

        Args:
            operation: Function to execute
            ui: UI handler for messages
            max_retries: Maximum number of retry attempts
            retry_message: Message to display during retry

        Returns:
            Operation result or None if all retries failed
        """
        for attempt in range(max_retries + 1):
            try:
                return operation()
            except (openai.RateLimitError, ConnectionError) as e:
                if attempt < max_retries:
                    ui.warning(f"{retry_message} (attempt {attempt + 1}/{max_retries})")
                    continue
                ui.error(f"Operation failed after {max_retries} retries: {e}")
                return None
            except Exception as e:
                ui.error(f"Operation failed: {e}")
                return None
