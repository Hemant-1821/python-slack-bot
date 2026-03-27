from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv

from utils import get_schema_structure


try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except Exception:  # pragma: no cover - optional dependency at import time
    MongoClient = None
    PyMongoError = Exception


load_dotenv()


MONGODB_URI = os.getenv("MONGODB_URI")


def _create_mongo_client() -> Any:
    if not MONGODB_URI or MongoClient is None:
        return None
    return MongoClient(MONGODB_URI)


mongo_client = _create_mongo_client()


USER_DB_SELECTIONS: dict[str, str] = {}
USER_CONVERSATION_HISTORY: dict[str, list[dict[str, Any]]] = {}


def select_db(db_name: str, user_id: str) -> None:
    """Persist selected DB in-memory as a placeholder.

    Replace this with real storage integration once the server layer is ported.
    """
    cleaned_db_name = db_name.strip()
    if not cleaned_db_name:
        raise ValueError("db name cannot be empty")

    if mongo_client is None:
        USER_DB_SELECTIONS[user_id] = cleaned_db_name
        return

    admin_db = mongo_client["admin"]
    result = admin_db.command({"listDatabases": 1, "nameOnly": True})
    db_names = [db_info["name"] for db_info in result.get("databases", [])]

    if cleaned_db_name in db_names:
        mongo_client["chat"]["settings"].update_one(
            {"userId": user_id},
            {
                "$set": {
                    "userId": user_id,
                    "selectedDb": cleaned_db_name,
                    "timestamp": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )
        return

    raise ValueError(f"Invalid DB name. Available DBs: {', '.join(db_names)}")


def fetch_conversation_history(user_id: str) -> list[dict[str, Any]]:
    """Return previously stored conversation history for a user.

    Placeholder in-memory store matching JS-side behavior for now.
    """
    if mongo_client is None:
        return list(USER_CONVERSATION_HISTORY.get(user_id, []))

    try:
        history = (
            mongo_client["chat"]["conversation_history"]
            .find({"userId": user_id})
            .sort("timestamp", -1)
            .limit(1)
        )
        latest = next(iter(history), None)
        if not latest:
            return []
        chat = latest.get("chat", [])
        return chat if isinstance(chat, list) else []
    except PyMongoError:
        return []


def update_conversation_history(user_id: str, chat: list[dict[str, Any]]) -> None:
    """Persist user chat history in-memory as a temporary implementation."""
    if mongo_client is None:
        USER_CONVERSATION_HISTORY[user_id] = list(chat)
        return

    try:
        mongo_client["chat"]["conversation_history"].update_one(
            {"userId": user_id},
            {
                "$set": {
                    "userId": user_id,
                    "chat": list(chat),
                    "timestamp": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )
    except PyMongoError:
        USER_CONVERSATION_HISTORY[user_id] = list(chat)


def get_selected_database(user_id: str) -> str | None:
    """Return selected DB name for a user.

    Keeps parity with JS helper behavior used by MCP tools.
    """
    if mongo_client is None:
        return USER_DB_SELECTIONS.get(user_id)

    settings = mongo_client["chat"]["settings"].find_one({"userId": user_id})
    if not settings:
        return None
    selected_db = settings.get("selectedDb")
    return selected_db if isinstance(selected_db, str) else None


def list_collections_from_database(db_name: str) -> list[str]:
    """List collection names in a DB."""
    if mongo_client is None:
        return []
    return mongo_client[db_name].list_collection_names()


def read_from_database(
    db_name: str,
    collection_name: str,
    query_object: dict[str, Any] | None = None,
    limit: int = 5,
    sort: dict[str, Any] | None = None,
    project: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Fetch rows/documents from a collection."""
    if mongo_client is None:
        return []

    cursor = mongo_client[db_name][collection_name].find(query_object or {}, project)
    cursor = cursor.limit(limit or 5).sort(list((sort or {}).items()))
    return list(cursor)


def table_join(
    db_name: str,
    table_name: str,
    local_field: str,
    foreign_table_name: str,
    foreign_column_name: str,
    new_field_name: str,
    limit: int = 2,
) -> list[dict[str, Any]]:
    """Execute a basic lookup aggregation similar to JS tableJoin tool."""
    if mongo_client is None:
        return []

    pipeline = [
        {"$limit": limit or 2},
        {
            "$lookup": {
                "localField": local_field,
                "from": foreign_table_name,
                "foreignField": foreign_column_name,
                "as": new_field_name,
            }
        },
    ]
    return list(mongo_client[db_name][table_name].aggregate(pipeline))


def table_schema(db_name: str, table_name: str) -> dict[str, Any]:
    """Return derived schema for a collection based on one sample document."""
    if mongo_client is None:
        return {}

    sample = list(mongo_client[db_name][table_name].find({}).limit(1))
    if not sample:
        return {}
    return get_schema_structure(sample[0])


