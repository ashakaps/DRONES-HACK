import json
from fastapi import APIRouter
from app.services.db import ensure_pool

router = APIRouter(prefix="/geo", tags=["geo"])

@router.get("/regions")
async def get_regions():
    pool = await ensure_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, ST_AsGeoJSON(geom) AS geometry
            FROM region
            WHERE geom IS NOT NULL
        """)
        features = []
        for row in rows:
            try:
                geom = json.loads(row["geometry"]) if row["geometry"] else None
            except Exception:
                geom = None
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {"id": row["id"], "name": row["name"]},
            })
        return {"type": "FeatureCollection", "features": features}

@router.get("/cities")
async def get_cities():
    pool = await ensure_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, name, ST_AsGeoJSON(ST_PointOnSurface(geom)) AS geometry
            FROM region
            WHERE geom IS NOT NULL
        """)
        features = []
        for row in rows:
            try:
                geom = json.loads(row["geometry"]) if row["geometry"] else None
            except Exception:
                geom = None
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {"id": row["id"], "name": row["name"]},
            })
        return {"type": "FeatureCollection", "features": features}
