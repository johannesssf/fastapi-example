import json
from fastapi.testclient import TestClient

from partner_app import main


client = TestClient(main.app)


class TestPartnerCreation:

    def setup_class(self):
        with open("single_reg.json", 'r') as f:
            self.partner = json.load(f)

    def test_create_partner_201(self):
        """Successful partner creation.
        """
        response = client.post("/api/v1/partners", json=self.partner)
        assert response.status_code == 201
        partner = json.loads(response.content)
        assert partner == self.partner


    def test_create_partner_422(self):
        """Body different from the expected won't work.
        """
        data = {"id": 1, "name": "Joao da Silva"}
        response = client.post("/api/v1/partners", data=data)
        assert response.status_code == 422
