from fastapi import FastAPI, HTTPException
from geojson import MultiPolygon, Point
from pydantic import BaseModel


class Partner(BaseModel):
    id: str
    tradingName: str
    ownerName: str
    document: str
    coverageArea: MultiPolygon
    address: Point


app = FastAPI()


@app.post("/api/v1/partners", status_code=201)
async def create_partner(partner: Partner):
    return partner
