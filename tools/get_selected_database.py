from langchain_core.tools import tool
from pymongo import MongoClient

def make_get_selected_database_tool(client: MongoClient):
    @tool
    async def get_selected_database(user_id: str) -> str:
        """Tool to get the name of the DB selected by the user.
        Params:
            - user_id: The user's ID.
        Returns the selected database name or a message if not set.
        """
        if not user_id:
            return "Please provide userId"

        user_settings = client["chat"]["settings"].find_one({"userId": user_id})
        db_name = user_settings.get("selectedDb") if user_settings else None

        if db_name:
            return f"Name of the db selected by user: {db_name}"
        return "User doesn't have any db selected, ask user for the db name if it's not provided in the user query. Do not assume it or use default as it might not generate expected results for the user"

    return get_selected_database