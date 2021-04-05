import haversine as hs

from typing import Dict, List
from pymongo import MongoClient


DB_LOCAL = "mongodb://localhost:27017"


class MongoDB:
    def __init__(self, db_name: str, db_host: str = DB_LOCAL):
        self._db_name = db_name
        self._db_host = db_host
        self._client = None

    def __del__(self):
        if self._client:
            self._client.close()

    def _get_database(self):
        """Get a new database connection."""
        if self._client is None:
            self._client = MongoClient(self._db_host)

        return self._client[self._db_name]

    def insert(self, collection: str, data: dict) -> Dict:
        """Insert data into collection.

        Args:
            collection (str): Mongo collection name
            data (dict): Data to be inserted

        Returns:
            bool: True if OK False otherwise
        """
        db = self._get_database()
        res = db[collection].insert_one(data)
        return res.acknowledged

    def load(self, collection: str, query: dict) -> Dict:
        """Load a single document from the collection based on the query.

        Args:
            collection (str): Mongo collection name
            query (dict): Query parameters

        Returns:
            Dict: Document data or None
        """
        db = self._get_database()
        res = db[collection].find_one(query)
        if res:
            del res["_id"]
        return res

    def search(self, collection: str, query: dict) -> List:
        """Search in collection the data especified.

        Args:
            collection (str): Mongo collection name
            query (dict): Query parameters

        Returns:
            List: List of query matches
        """
        db = self._get_database()
        return list(db[collection].find(query, {"_id": 0}))


class PartnerDB:
    """Wrapps MongoDB to handle the application business logic."""
    def __init__(self, db_name: str, collection: str):
        self._db = MongoDB(db_name)
        self._collection = collection

    def insert(self, data: dict) -> Dict:
        return self._db.insert(self._collection, data)

    def find_by_id(self, id: str) -> Dict:
        return self._db.load(self._collection, {"id": id})

    def find_by_document(self, document: str) -> Dict:
        return self._db.load(self._collection, {"document": document})

    def search_nearest(self, long: float, lat: float) -> Dict:
        near_partners = self._db.search(
            self._collection,
            {
                "coverageArea": {
                    "$geoIntersects": {
                        "$geometry": {"type": "Point", "coordinates": [long, lat]}
                    }
                }
            },
        )
        if near_partners:
            nearest = {"partner": None, "distance": 9999}
            for partner in near_partners:
                distance = hs.haversine((long, lat), partner["address"]["coordinates"])
                if distance < nearest["distance"]:
                    nearest["partner"] = partner
                    nearest["distance"] = distance

            return nearest["partner"]
