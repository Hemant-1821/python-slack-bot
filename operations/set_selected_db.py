def make_set_selected_db(client):
    def set_selected_db(user_id: str, db_name: str):
        """Set the selected DB for a user in MongoDB.
        Params:
            - user_id: The user's ID.
            - db_name: The name of the database to set as selected.
        """
        if not user_id:
            return "Please provide userId"
        if not db_name:
            return "Please provide db name"

        client["chat"]["settings"].update_one(
            {"userId": user_id},
            {"$set": {"selectedDb": db_name}},
            upsert=True
        )
        return f"Selected DB for user {user_id} has been set to {db_name}"

    return set_selected_db