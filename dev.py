import os

from app import app as slack_app
from app import flask_app, mongo_client


def main() -> None:
    """Local development entrypoint with auto-reload enabled."""
    try:
        mongo_client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")

        port = int(os.getenv("PORT", 3000))
        flask_app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)
    except Exception as error:
        slack_app.logger.error(str(error))
        raise


if __name__ == "__main__":
    main()

