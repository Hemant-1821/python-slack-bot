# Python Slack Bot (Socket Mode)

A minimal Slack Bolt app in Python using Socket Mode.

## What this bot does

- Replies with `Hello!` when it sees a message containing `hello`
- Handles the `/test` slash command

## Project files

- `app.py` - Slack Bolt app entrypoint (use this to run the bot)
- `requirements.txt` - Python dependencies
- `main.py` - Default IDE sample script (not used by the bot)

## Prerequisites

- Python 3.9+
- A Slack workspace where you can install apps

## 1) Create and configure the Slack app

1. Go to https://api.slack.com/apps and create a new app.
2. In **Socket Mode**, enable Socket Mode.
3. In **App-Level Tokens**, create a token with `connections:write` scope.
   - This is your `SLACK_APP_TOKEN` (starts with `xapp-...`).
4. In **OAuth & Permissions**, add bot token scopes:
   - `app_mentions:read`
   - `chat:write`
   - `commands`
5. Install/Reinstall the app to your workspace.
   - This gives you `SLACK_BOT_TOKEN` (starts with `xoxb-...`).
6. In **Slash Commands**, create `/test` and point Request URL to any placeholder URL (required by Slack UI for creation).
   - For Socket Mode, slash command events are delivered over the WebSocket connection.

## 2) Install dependencies

```zsh
cd /Users/hemantsingh/Desktop/FAI/python-slack-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Set environment variables

```zsh
export SLACK_BOT_TOKEN='xoxb-your-bot-token'
export SLACK_APP_TOKEN='xapp-your-app-level-token'
```

Optional (persist in zsh):

```zsh
echo "export SLACK_BOT_TOKEN='xoxb-your-bot-token'" >> ~/.zshrc
echo "export SLACK_APP_TOKEN='xapp-your-app-level-token'" >> ~/.zshrc
source ~/.zshrc
```

## 4) Run the bot

```zsh
python3 app.py
```

## 5) Quick verification

1. In any channel/DM where the bot is present, send: `hello`
   - Expected response: `Hello!`
2. Run slash command: `/test`
   - Expected response: `/test command received!`

## Troubleshooting

- `KeyError: 'SLACK_BOT_TOKEN'` or `KeyError: 'SLACK_APP_TOKEN'`
  - Ensure env vars are set in the same shell session where you run `python3 app.py`.
- Slash command not responding
  - Re-check `/test` exists in your Slack app and app has `commands` scope.
  - Reinstall the app after changing scopes.
- Bot not replying to `hello`
  - Confirm bot is invited to the channel.
  - Confirm app has `chat:write` scope and is installed.

## README maintenance

Keep `README.md` updated whenever any of these change:

- New commands/events/listeners in `app.py`
- Required scopes or Slack app setup steps
- Environment variables
- Run/start instructions

