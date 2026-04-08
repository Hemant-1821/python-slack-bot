from langchain_core.tools import tool

@tool
def default_tool() -> str:
    """If there's no specific tool for the request, use this tool to handle general queries. Do not answer from memory or guess."""
    return "I didn't understand that as a DB operation. Try commands like:\n• Get all users from the last 30 days"