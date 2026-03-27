# Slack Bot to query mongoDB

Simple Slack Bolt bot in Python with MCP-style placeholders.

## Current features

- `hello` -> replies `Hello!`
- Other messages -> posts `Thinking...`, runs `mcp_client.process_query(...)`, replies with result
- Slash commands: `/test`, `/clearbotchat [count]`, `/selectdb <db_name>`

## Quick setup

1. Create a Slack app at https://api.slack.com/apps
2. Enable Socket Mode and create an app token (`connections:write`) -> `SLACK_APP_TOKEN`
3. Add bot scopes: `chat:write`, `commands` (+ history scopes if using `/clearbotchat`)
4. Create slash commands: `/test`, `/clearbotchat`, `/selectdb`
5. Install the app and copy bot token -> `SLACK_BOT_TOKEN`

## Install and run

```zsh
cd /Users/hemantsingh/Desktop/FAI/python-slack-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## Environment variables

Use `.env` or shell exports:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-level-token
ANTHROPIC_API_KEY=your-anthropic-api-key
MONGODB_URI=your-mongodb-connection-string
MCP_SERVER_SCRIPT=./dist/mcp-server.js
```

## Notes

- `mcp_client.py` is still a scaffold (LLM/tool flow is placeholder).
- `mcp_server.py` uses MongoDB when `MONGODB_URI` is set; otherwise it falls back to in-memory storage.

