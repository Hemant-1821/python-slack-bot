from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

from constants import system_prompt
from mcp_server import fetch_conversation_history, update_conversation_history


load_dotenv()


DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_MAX_TOKENS = 1000


class MCPClient:
    """Python port scaffold of the JS MCP client.

    This preserves the JS method flow while keeping external integrations as
    placeholders until corresponding server/client files are ported.
    """

    def __init__(self) -> None:
        self.server_script_path: str | None = None
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.tools: list[dict[str, Any]] = []

    def connect_to_server(self, server_script_path: str) -> None:
        """Connect to an MCP server.

        Placeholder: stores path and registers pseudo tools for now.
        """
        self.server_script_path = server_script_path
        # Placeholder tools list. Replace with real MCP tool discovery.
        self.tools = [
            {
                "name": "select_db",
                "description": "Selects a DB for the current user session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "db_name": {"type": "string"},
                        "userId": {"type": "string"},
                    },
                    "required": ["db_name", "userId"],
                },
            }
        ]

    def get_llm_response(self, user_id: str, messages: list[dict[str, Any]]) -> str:
        """Generate an LLM response.

        Placeholder behavior intentionally mirrors the JS recursion shape but
        returns deterministic text until Anthropic + MCP transport is wired.
        """
        if not messages:
            return ""

        last_user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                content = message.get("content", "")
                if isinstance(content, str):
                    last_user_message = content
                break

        if not last_user_message.strip():
            return "Please send a non-empty message."

        if not self.anthropic_api_key:
            return (
                "[placeholder] ANTHROPIC_API_KEY is not set. "
                f"Echoing query for {user_id}: {last_user_message.strip()}"
            )

        # Placeholder until Anthropic + MCP tool-calling integration is ported.
        return (
            f"[placeholder LLM response using model {DEFAULT_MODEL}] "
            f"{last_user_message.strip()}"
        )

    def process_query(self, query: str, user_id: str) -> str:
        """Process query with history-aware flow equivalent to JS implementation."""
        history = fetch_conversation_history(user_id)
        messages: list[dict[str, Any]] = [
            *history,
            {"role": "user", "content": query},
        ]

        final_result = self.get_llm_response(user_id, messages)
        chat = [
            *history[-8:],
            {"role": "user", "content": query},
            {"role": "assistant", "content": final_result},
        ]
        update_conversation_history(user_id, chat)
        return final_result

    def cleanup(self) -> None:
        """Clean up resources.

        Placeholder cleanup currently clears ephemeral connection state.
        """
        self.server_script_path = None
        self.tools = []

