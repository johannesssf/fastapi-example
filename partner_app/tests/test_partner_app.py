import json
from fastapi import status
from fastapi.testclient import TestClient
from pymongo import MongoClient

from partner_app import main

DB_HOST = "mongodb://localhost:27017"
DB_NAME = "mariodelivery"
COLLECTION = "partners"
CLIENT = TestClient(main.app)
TEST_DB = MongoClient(DB_HOST)[DB_NAME]


class TestPartnerCreation:
    partners_endpoint = "/api/v1/partners"

    def setup_class(self):
        TEST_DB[COLLECTION].drop()
        with open("single_reg.json", "r") as f:
            self.partner = json.load(f)

    def teardown_class(self):
        TEST_DB[COLLECTION].drop()

    def test_create_partner_successful(self):
        """Successful partner creation."""
        response = CLIENT.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_201_CREATED
        partner = json.loads(response.content)
        assert partner == self.partner

    def test_create_partner_invalid_fields(self):
        """Body different from the expected won't work."""
        data = {"field1": 1, "field2": "some information"}
        response = CLIENT.post(self.partners_endpoint, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_partner_invalid_coverage_area(self):
        """Invalid coverage area is not accepted."""
        with open("invalid_coverage_area.json") as f:
            partner = json.load(f)
        response = CLIENT.post(self.partners_endpoint, json=partner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_partner_invalid_address(self):
        """Invalid address is not accepted."""
        with open("invalid_address.json") as f:
            partner = json.load(f)
        response = CLIENT.post(self.partners_endpoint, json=partner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicated_id(self):
        """Attempts to create a partner with a duplicated id will fail."""
        self.partner["id"] = 999
        self.partner["document"] = "1432132123891/0999"
        response = CLIENT.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_201_CREATED
        response = CLIENT.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicated_document(self):
        """Attempts to create a partner with a duplicated document will fail."""
        self.partner["id"] = 123
        self.partner["document"] = "1432132123891/0123"
        response = CLIENT.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_201_CREATED
        self.partner["id"] = 456
        response = CLIENT.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPartnerLoad:
    partners_endpoint = "/api/v1/partners/"

    def setup_class(self):
        with open("pdvs.json", "r") as f:
            self.partner = json.load(f)

        TEST_DB[COLLECTION].drop()
        TEST_DB[COLLECTION].insert_many(self.partner['pdvs'][:3])

    def teardown_class(self):
        TEST_DB[COLLECTION].drop()

    def test_load_partner(self):
        """When the partner id exists everything goes fine."""
        response = CLIENT.get(self.partners_endpoint + "1")
        assert response.status_code == status.HTTP_200_OK

    def test_load_partner_not_existent(self):
        """When a partner does not exist a proper code is returned."""
        response = CLIENT.get(self.partners_endpoint + "999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPartnerSearch:
    partners_endpoint = "/api/v1/partners?long={}&lat={}"

    def setup_class(self):
        with open("pdvs.json", "r") as f:
            self.partner = json.load(f)

        TEST_DB[COLLECTION].drop()
        TEST_DB[COLLECTION].insert_many(self.partner['pdvs'])

    def teardown_class(self):
        TEST_DB[COLLECTION].drop()

    def test_search_partner_find_invalid_coordinates(self):
        """An invalid coordinate is not accepted."""
        long_lat = (-181.3073990, -91.9964813)

        response = CLIENT.get(self.partners_endpoint.format(*long_lat))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_partner_find_one(self):
        """A coordinate with a single result."""
        # Coordnate within partner id=1 coverage area
        long_lat = (-43.3073990, -22.9964813)

        response = CLIENT.get(self.partners_endpoint.format(*long_lat))
        assert response.status_code == status.HTTP_200_OK

        partner_found = json.loads(response.content)
        assert partner_found['id'] == '1'

    def test_search_partner_find_none(self):
        # Coordnate without all partners coverage area
        long_lat = (-70.3540372, -8.1750448)

        response = CLIENT.get(self.partners_endpoint.format(*long_lat))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_search_partner_find_many(self):
        # With a coordinate within the coverage areas of three partners, we get
        #  the nearest based on its address. (id=29)
        long_lat = (-46.6990754, -23.6206199)

        response = CLIENT.get(self.partners_endpoint.format(*long_lat))
        partner_found = json.loads(response.content)
        assert partner_found['id'] == '29'
