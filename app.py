import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.message("hello")
def handle_hello_message(message, say):
    say("Hello!")


@app.command("/test")
def handle_test_command(ack, respond, command):
    ack()
    respond("/test command received!")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

