from langchain_core.tools import tool
from pymongo import MongoClient
import json

def make_table_join_tool(client: MongoClient):
    @tool
    async def table_join(
        db_name: str,
        table_name: str,
        local_field: str,
        foreign_table_name: str,
        foreign_column_name: str,
        new_field_name: str,
        limit: int,
    ) -> str:
        """Tool to get data from join of two tables.
        Params:
            - db_name: Database name.
            - table_name: Main table/collection name.
            - local_field: Field from main table.
            - foreign_table_name: Table to join from.
            - foreign_column_name: Field in foreign table.
            - new_field_name: Name for joined array field.
            - limit: Limit on results.
        Returns joined data.
        """
        try:
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

            result = list(
                client[db_name][table_name].aggregate(pipeline)
            )

            # Convert ObjectId and other non-serializable types to string
            return f"Aggregated data: {json.dumps(result, default=str)}"
        except Exception:
            return "Failed to retrieve collections from the database."

    return table_join