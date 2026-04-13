from langchain_core.tools import tool
from pymongo import MongoClient
from typing import Optional
import json


def make_read_from_db_tool(client: MongoClient):
    @tool
    async def read_from_db(
        db_name: str,
        collection_name: str,
        query_object: Optional[dict] = None,
        limit: Optional[int] = None,
        sort: Optional[dict] = None,
        project: Optional[dict] = None,
    ) -> str:
        """If user asks to fetch data from a collection or table, use this tool to fetch them. Do not answer from memory.
        Params:
            - db_name(type - string): The name of the database to query (default: "sample_mflix")
            - collection_name(type - string): The name of the collection to query (default: "movies")
            - query_object(type - dict): An optional query object to filter the results. example -> { "title": "The Room" }
            - limit(type - int): An optional limit on the number of results to return (default: 5)
            - sort(type - dict): An optional sort object to sort the results. example - { "rating": -1 }
            - project(type - dict): An optional projection object to specify which fields to return. example - { "_id": 0, "title": 1, "imdb": 1 }
        Returns a list of documents from the specified collection.
        """
        print("read from db", {
            "db_name": db_name,
            "collection_name": collection_name,
            "query_object": query_object,
            "limit": limit,
            "sort": sort,
            "project": project,
        })

        try:
            result = list(
                client[db_name or "sample_mflix"][collection_name or "movies"].find(
                    filter=query_object or {},
                    projection=project,
                    limit=limit or 5,
                    sort=list(sort.items()) if sort else None
                )
            )

            result = list(result)

            return (
                json.dumps(result, indent=2, default=str)
                or "No result found. Try again with a more specific query."
            )
        except Exception as e:
            print(e)
            return "Failed to retrieve data from the database."

    return read_from_db