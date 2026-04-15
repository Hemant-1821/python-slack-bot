import os
import re
import asyncio
from typing import Any

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from werkzeug.serving import is_running_from_reloader
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from agent.query_agent import query_agent
from operations import make_set_selected_db
from tools import get_tools

load_dotenv()

# MongoDB setup
uri = os.getenv("MONGODB_URI")
mongo_client = MongoClient(uri, server_api=ServerApi("1"))

# Tools and Slack/Flask setup
tools = get_tools(mongo_client)
app = App(token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SLACK_SIGNING_SECRET"])
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@app.message(re.compile(".*"))
def handle_all_messages(message: dict[str, Any], say, client, context: dict[str, Any]):
    if message.get("subtype") == "bot_message":
        return

    message_text = message.get("text")
    if not isinstance(message_text, str):
        return

    channel = message.get("channel")
    if not channel:
        return

    thinking_message = client.chat_postMessage(channel=channel, text="Thinking...")
    user_id = message.get("user") or context.get("user_id") or "unknown"

    try: # main
        response = asyncio.run(query_agent(message_text, user_id, mongo_client, tools))
    finally:
        if thinking_message.get("ts"):
            client.chat_delete(channel=channel, ts=thinking_message["ts"])

    say(text=response or "I could not generate a response.")


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

        respond(f"✅ Cleared {deleted_count} message(s) posted by the bot.")
    except Exception as error:
        app.logger.error(f"Error clearing chat: {error}")
        respond("❌ Failed to clear messages.")


@app.command("/selectdb")
def handle_selectdb_command(ack, command: dict[str, Any], respond, context: dict[str, Any], client):
    ack()
    db_name = command.get("text", "").strip()
    channel_id = command.get("channel_id")

    if not db_name:
        # handle wrong db name input
        respond("❌ Invalid db name. Please mention just the db name after the slash command")
        return

    user_id = command.get("user_id") or context.get("user_id") or "unknown"
    try:
        # Save the selected DB for the user in MongoDB
        make_set_selected_db(mongo_client)(user_id, db_name)
        respond("DB Selection successfully saved.")
        if channel_id:
            client.conversations_setTopic(channel=channel_id, topic=f"Selected DB: {db_name}")
    except Exception as error:
        app.logger.error(str(error))
        respond(f"An error occurred: {error}")


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/slack/command", methods=["POST"])
def slack_commands():
    return handler.handle(request)


@flask_app.route("/check")
def health_check():
    return "server up and running!!"


if __name__ == "__main__":
    try:
        # Verify MongoDB connection once in the reloader child process.
        if is_running_from_reloader():
            mongo_client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")

        port = int(os.getenv("PORT", 3000))
        auto_reload = os.getenv("FLASK_RELOAD", "1") == "1"
        flask_app.run(
            host="0.0.0.0",
            port=port,
            debug=auto_reload,
            use_reloader=auto_reload,
        )
    except Exception as error:
        app.logger.error(str(error))
        raise