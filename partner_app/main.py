from fastapi import FastAPI, HTTPException, status
from pymongo import errors

from .database import PartnerDB, PartnerNotFoundException
from .models import Partner


app = FastAPI()
DB = PartnerDB("mariodelivery_test", "partners")


@app.post("/api/v1/partners", status_code=status.HTTP_201_CREATED)
async def create_partner(partner: Partner):
    """Handles create partner endpoint."""
    if not partner.is_coverage_area_valid():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'coverageArea' invalid data")

    if not partner.is_address_valid():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'address' invalid data")

    if DB.find_by_id(partner.id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'id' already exists")

    if DB.find_by_document(partner.document):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'document' already exists")

    DB.insert(dict(partner))
    return partner


@app.get("/api/v1/partners/{partner_id}", status_code=200)
async def load_partner(partner_id: str):
    """Handles load partner endpoint."""
    partner = DB.find_by_id(partner_id)

    if partner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "partner not found")

    return partner


@app.get("/api/v1/partners", status_code=200)
async def search_partner(long: float, lat: float):
    """Handles search partner endpoint."""
    try:
        nearest = DB.search_nearest(long, lat)
        if nearest:
            return nearest
    except errors.OperationFailure as ex:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, ex.details['errmsg'])
    except PartnerNotFoundException:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "partner not found")
