from pymongo import MongoClient
from .set_selected_db import make_set_selected_db

def get_tools(client: MongoClient):
    return [
        make_set_selected_db(client)
    ]