from langchain_core.tools import tool

@tool
def add(x: int, y: int) -> int:
    """Adds two numbers."""
    return x + y

@tool
def multiply(x: int, y: int) -> int:
    """Multiplies two numbers."""
    return x * y

@tool
def subtract(x: int, y: int) -> int:
    """Subtracts the second number from the first."""
    return x - y

@tool
def divide(x: int, y: int) -> float:
    """Divides the first number by the second."""
    if y == 0:
        return "Error: Division by zero is not allowed."
    return x / y

@tool 
def call_larry() -> str:
    """Calls Larry."""
    return "Hey Larry!"