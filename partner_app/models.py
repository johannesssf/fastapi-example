from geojson import MultiPolygon, Point
from pydantic import BaseModel


class Partner(BaseModel):
    id: str
    tradingName: str
    ownerName: str
    document: str
    coverageArea: MultiPolygon
    address: Point

    def is_coverage_area_valid(self):
        coverage_area = MultiPolygon(self.coverageArea['coordinates'])
        return coverage_area.is_valid and self.coverageArea['type'] == "MultiPolygon"

    def is_address_valid(self):
        address = Point(self.address['coordinates'])
        return address.is_valid and self.address['type'] == "Point"
