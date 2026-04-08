from langchain_core.tools import tool
from pymongo import MongoClient
import json

def make_table_schema_tool(client: MongoClient):
    @tool
    async def table_schema(db_name: str, table_name: str) -> str:
        """Fetches schema structure of a particular table.
        Params:
            - db_name: The name of the database.
            - table_name: The name of the table/collection.
        Returns the schema definition inferred from the first document in the collection.
        """
        print(f"Schema tool called: {db_name}, {table_name}")
        try:
            if not db_name or not table_name:
                return "Error! Both db_name and table_name must be provided."

            result = list(
                client[db_name][table_name].find({}).limit(1)
            )

            if not result:
                return f"No documents found in table {table_name}."

            schema = get_schema_structure(result[0])
            return f"Schema definition for the table {table_name}: {json.dumps(schema, indent=2, default=str)}"
        except Exception:
            return "Something went wrong! Failed to retrieve schema from the database."

    return table_schema


def get_schema_structure(document: dict) -> dict:
    """Infers schema structure from a MongoDB document."""
    schema = {}
    for key, value in document.items():
        if isinstance(value, dict):
            schema[key] = get_schema_structure(value)
        elif isinstance(value, list):
            schema[key] = f"array({type(value[0]).__name__ if value else 'unknown'})"
        else:
            schema[key] = type(value).__name__
    return schema