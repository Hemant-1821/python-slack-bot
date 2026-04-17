# Slack Bot to query MongoDB

Simple Slack Bolt bot in Python with Flask, ngrok, and local auto-reload.

## Features

- `hello` -> replies `Hello!`
- Other messages -> posts `Thinking...`, runs `mcp_client.process_query(...)`, replies with result
- Slash commands: `/test`, `/clearbotchat [count]`, `/selectdb <db_name>`

## Quick setup

1. Create a Slack app at https://api.slack.com/apps
2. Add bot token scopes: `chat:write`, `commands`, `channels:history`, `groups:history`, `im:history`, `mpim:history`
3. Install the app and copy bot token -> `SLACK_BOT_TOKEN`
4. Go to **Event Subscriptions** and enable events
5. Set Request URL to `https://your-ngrok-url.ngrok.io/slack/events` (see run steps)
6. Subscribe to bot events: `message.channels`, `message.groups`, `message.im`, `message.mpim`
7. Create slash commands: `/test`, `/clearbotchat`, `/selectdb`

## Install and run

**Terminal 1: Start ngrok**
```zsh
ngrok http 3000
# Copy the HTTPS URL and add to Slack: https://your-url.ngrok.io/slack/events
```

**Terminal 2: Start the bot**
```zsh
cd /Users/hemantsingh/Desktop/FAI/python-slack-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 dev.py
```

## Environment variables

Use `.env` or shell exports:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
GOOGLE_API_KEY=your-google-api-key
MONGODB_URI=your-mongodb-connection-string
PORT=3000

# LangSmith tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key
```

## Notes

- `mcp_client.py` is still a scaffold (LLM/tool flow is placeholder).
- `mcp_server.py` uses MongoDB when `MONGODB_URI` is set; otherwise it falls back to in-memory storage.
- App requires ngrok to expose local port to Slack webhook verification.
- `dev.py` restarts the server automatically when Python files change.
- Slack user IDs are normalized into deterministic UUID thread IDs before LangGraph calls (fixes `thread id should be uuid` in LangSmith/LangGraph UI).

## LangGraph Studio (local)

```zsh
cd /Users/hemantsingh/Desktop/FAI/python-slack-bot
source .venv/bin/activate
langgraph dev --config langgraph.json
```

- Studio config is in `langgraph.json`
- Graph entrypoint is `agent/studio_graph.py`
- Studio run disables the custom MongoDB checkpointer and uses LangGraph's built-in persistence
- Slack app and Studio use the same graph-building code path, but they still run in separate processes
- Traces appear in LangSmith when `LANGSMITH_TRACING=true`

