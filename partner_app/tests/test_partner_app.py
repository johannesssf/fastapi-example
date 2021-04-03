import json
from fastapi import status
from fastapi.testclient import TestClient

from partner_app import main


client = TestClient(main.app)


class TestPartnerCreation:
    partners_endpoint = "/api/v1/partners"

    def setup_class(self):
        with open("single_reg.json", "r") as f:
            self.partner = json.load(f)
        main.partners.drop()

    def teardown_class(self):
        main.partners.drop()

    def test_create_partner_successful(self):
        """Successful partner creation."""
        response = client.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_201_CREATED
        partner = json.loads(response.content)
        assert partner == self.partner

    def test_create_partner_invalid_fields(self):
        """Body different from the expected won't work."""
        data = {"field1": 1, "field2": "some information"}
        response = client.post(self.partners_endpoint, data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_partner_invalid_coverage_area(self):
        """Invalid coverage area is not accepted."""
        with open("invalid_coverage_area.json") as f:
            partner = json.load(f)
        response = client.post(self.partners_endpoint, json=partner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_partner_invalid_address(self):
        """Invalid address is not accepted."""
        with open("invalid_address.json") as f:
            partner = json.load(f)
        response = client.post(self.partners_endpoint, json=partner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicated_id(self):
        """Attempts to create a partner with a duplicated id will fail."""
        self.partner["id"] = 999
        self.partner["document"] = "1432132123891/0999"
        response = client.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_201_CREATED
        response = client.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicated_document(self):
        """Attempts to create a partner with a duplicated document will fail."""
        self.partner["id"] = 123
        self.partner["document"] = "1432132123891/0123"
        response = client.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_201_CREATED
        self.partner["id"] = 456
        response = client.post(self.partners_endpoint, json=self.partner)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPartnerLoad:
    partners_endpoint = "/api/v1/partners/"

    def setup_class(self):
        with open("pdvs.json", "r") as f:
            self.partner = json.load(f)
        main.partners.drop()
        main.partners.insert_many(self.partner['pdvs'][:3])

    def teardown_class(self):
        main.partners.drop()

    def test_load_partner(self):
        """When the partner id exists everything goes fine."""
        response = client.get(self.partners_endpoint + "1")
        assert response.status_code == status.HTTP_200_OK

    def test_load_partner_not_existent(self):
        """When a partner does not exist a proper code is returned."""
        response = client.get(self.partners_endpoint + "999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
