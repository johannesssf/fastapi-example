import haversine as hs
from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from pymongo import errors

from .models import Partner


def db_connect(db_name):
    mongo = MongoClient("mongodb://localhost:27017")
    return mongo[db_name]


app = FastAPI()
db = db_connect("mariodelivery")
partners = db.partners


@app.post("/api/v1/partners", status_code=status.HTTP_201_CREATED)
async def create_partner(partner: Partner):
    """Handles create partner endpoint."""
    if not partner.is_coverage_area_valid():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'coverageArea' invalid data")

    if not partner.is_address_valid():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'address' invalid data")

    if partners.find_one({"id": partner.id}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'id' already exists")

    if partners.find_one({"document": partner.document}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'document' already exists")

    partners.insert_one(dict(partner))
    return partner


@app.get("/api/v1/partners/{partner_id}", status_code=200)
async def load_partner(partner_id: str):
    """Handles load partner endpoint."""
    partner = partners.find_one({"id": partner_id})

    if partner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "partner not found")

    del partner['_id']
    return partner


@app.get("/api/v1/partners", status_code=200)
async def search_partner(long: float, lat: float):
    """Handles search partner endpoint."""
    try:
        near_partners = list(partners.find({
            'coverageArea': {
                '$geoIntersects': {
                    '$geometry' : {
                        'type': 'Point',
                        'coordinates': [long, lat]
                    }
                }
            }}))
    except errors.OperationFailure as ex:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, ex.details['errmsg'])

    if near_partners:
        nearest = {'partner': None, 'distance': 9999}
        for partner in near_partners:
            distance = hs.haversine((long, lat), partner['address']['coordinates'])
            if distance < nearest['distance']:
                nearest['partner'] = partner
                nearest['distance'] = distance
        del nearest['partner']['_id']
        return nearest['partner']

    raise HTTPException(status.HTTP_404_NOT_FOUND, "partner not found")
