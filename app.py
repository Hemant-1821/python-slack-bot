import os
import re
from typing import Any

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from mcp_client import MCPClient
from mcp_server import select_db


load_dotenv()


app = App(token=os.environ["SLACK_BOT_TOKEN"])
mcp_client = MCPClient()


@app.message("hello")
def handle_hello_message(say):
    say("Hello!")


@app.message(re.compile(".*"))
def handle_all_messages(message: dict[str, Any], say, client, context: dict[str, Any]):
    if message.get("subtype") == "bot_message":
        return

    message_text = message.get("text")
    if not isinstance(message_text, str):
        return
    if message_text.strip().lower() == "hello":
        return

    channel = message.get("channel")
    if not channel:
        return

    thinking_message = client.chat_postMessage(channel=channel, text="Thinking...")
    user_id = message.get("user") or context.get("user_id") or "unknown"

    try:
        mcp_message = mcp_client.process_query(message_text, user_id)
    finally:
        if thinking_message.get("ts"):
            client.chat_delete(channel=channel, ts=thinking_message["ts"])

    say(mcp_message)


@app.command("/test")
def handle_test_command(ack, respond):
    ack()
    respond("/test command received!")


@app.command("/clearbotchat")
def handle_clearbotchat_command(ack, command: dict[str, Any], client, respond):
    ack()

    channel_id = command.get("channel_id")
    if not channel_id:
        respond("Couldn't find a channel for this command.")
        return

    try:
        count_to_delete = int(command.get("text", "").strip() or "20")
    except ValueError:
        count_to_delete = 20

    try:
        history = client.conversations_history(channel=channel_id, limit=100)
        messages = history.get("messages", [])
        if not messages:
            respond("Couldn't fetch messages.")
            return

        bot_user_id = client.auth_test().get("user_id")
        bot_messages = [
            msg
            for msg in messages
            if msg.get("user") == bot_user_id and not msg.get("subtype")
        ][:count_to_delete]

        deleted_count = 0
        for msg in bot_messages:
            ts = msg.get("ts")
            if not ts:
                continue
            client.chat_delete(channel=channel_id, ts=ts)
            deleted_count += 1

        respond(f"Cleared {deleted_count} message(s) posted by the bot.")
    except Exception as error:  # pragma: no cover - network/runtime dependent
        app.logger.error(f"Error clearing chat: {error}")
        respond("Failed to clear messages.")


@app.command("/selectdb")
def handle_selectdb_command(ack, command: dict[str, Any], respond, context: dict[str, Any], client):
    ack()

    db_name = command.get("text", "").strip()
    channel_id = command.get("channel_id")
    if not db_name:
        respond("invalid db name. Please mention just the db name after the slash command")
        return

    user_id = command.get("user_id") or context.get("user_id") or "unknown"
    try:
        select_db(db_name, user_id)
        respond("DB Selection successfully saved.")
        if channel_id:
            client.conversations_setTopic(channel=channel_id, topic=f"Selected DB: {db_name}")
    except Exception as error:  # pragma: no cover - network/runtime dependent
        app.logger.error(str(error))
        respond(f"An error occurred: {error}")


if __name__ == "__main__":
    try:
        mcp_client.connect_to_server(os.getenv("MCP_SERVER_SCRIPT", "./dist/mcp-server.js"))
        SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    except Exception as error:  # pragma: no cover - startup/runtime dependent
        app.logger.error(str(error))
        mcp_client.cleanup()
        raise

