import json

from pymongo import MongoClient

from ..database import MongoDB, PartnerDB


class BaseDB:
    db_host = "mongodb://localhost:27017"
    db_name = "mariodelivery_test"
    collection = "partners"

    def insert_many(self, data):
        self._client[self.db_name][self.collection].insert_many(data)

    def setup_class(self):
        self._client = MongoClient(self.db_host)
        self._client[self.db_name][self.collection].drop()

    def teardown_class(self):
        self._client[self.db_name][self.collection].drop()


class TestDatabase(BaseDB):
    def setup_class(self):
        super().setup_class(self)

        self.db = MongoDB(self.db_name)
        self.db.insert(
            self.collection,
            {
                "id": "1",
                "tradingName": "Warm Beverages",
                "ownerName": "Jose Doe",
                "document": "25855575391",
            }
        )

    def test_find_existent_document(self):
        """A document is returned when the id exists."""
        doc = self.db.load(self.collection, {"id": "1"})
        assert doc is not None

    def test_find_none_existent_document(self):
        """No document is returned when the id does not exist."""
        doc = self.db.load(self.collection, {"id": "1234"})
        assert doc is None

    def test_insert_data(self):
        """A successful insert returns the document."""
        data = {
            "id": "2",
            "tradingName": "Cool Beverages",
            "ownerName": "John Doe",
            "document": "25845675391",
        }
        assert self.db.insert(self.collection, data)

    def test_search_data(self):
        """Documents are returned with the matching filter."""
        data = {
            "id": "3",
            "tradingName": "Hot Beverages",
            "ownerName": "Jane Doe",
            "document": "32165498791",
        }
        self.db.insert(self.collection, data)

        reg = self.db.search(self.collection, {"id": "3"})
        assert reg[0]['id'] == "3"


class TestPartnerDB(BaseDB):
    def setup_class(self):
        super().setup_class(self)

        self.db = PartnerDB(self.db_name, self.collection)

        with open('pdvs.json') as f:
            self.pdvs = json.load(f)['pdvs'][:5]

        for pdv in self.pdvs:
            self.db.insert(pdv)

    def test_find_by_id(self):
        """When id exists we can find it."""
        partner = self.db.find_by_id(self.pdvs[0]['id'])
        assert partner['id'] == self.pdvs[0]['id']

    def test_find_by_document(self):
        """When id exists we can find it."""
        partner = self.db.find_by_document(self.pdvs[0]['document'])
        assert partner['document'] == self.pdvs[0]['document']

    def test_search_nearest_one(self):
        """When a point is in a coverage area we find the partner."""
        partner = self.db.search_nearest(-43.24677, -22.99606)
        assert partner

    def test_search_nearest_none(self):
        """When a point is not in a coverage area partner is found."""
        partner = self.db.search_nearest(-46.64905, -23.55543)
        assert not partner
