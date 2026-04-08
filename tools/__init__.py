from pymongo import MongoClient
from .default_tool import default_tool
from .get_selected_database import make_get_selected_database_tool
from .read_from_db import make_read_from_db_tool
from .table_join import make_table_join_tool
from .table_schema import make_table_schema_tool

def get_tools(client: MongoClient):
    return [
        default_tool,
        make_get_selected_database_tool(client),
        make_read_from_db_tool(client),
        make_table_join_tool(client),
        make_table_schema_tool(client),
    ]