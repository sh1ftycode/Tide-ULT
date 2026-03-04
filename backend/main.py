from fastapi import FastAPI
from dotenv import load_dotenv
import os
import httpx
from pydantic import BaseModel
from typing import Optional, List

#formatting for the api
class MediaItem(BaseModel):
    id: str
    name: str
    type: str
    year: Optional[int] = None
    rating: Optional[float] = None
    official_rating: Optional[str] = None

class LibraryResponse(BaseModel):
    items: List[MediaItem]
    total: int

load_dotenv()

JELLYFIN_URL = os.getenv("JELLYFIN_URL")
JELLYFIN_KEY = os.getenv("JELLYFIN_API_KEY")

app = FastAPI(
    title="TideULT",
    description="The all-in-one media server that brings everything to shore.",
    version="0.1.0"
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "TideULT",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to TideULT 🌊",
        "docs": "/docs"
    }

@app.get("/library", response_model=LibraryResponse)
async def get_library():
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{JELLYFIN_URL}/Items",
            params={
                "api_key": JELLYFIN_KEY,
                "IncludeItemTypes": "Movie,Series",
                "Recursive": True
            }
        )
        data = r.json()
        items = [
            MediaItem(
                id=item["Id"],
                name=item["Name"],
                type=item["Type"],
                year=item.get("ProductionYear"),
                rating=item.get("CommunityRating"),
                official_rating=item.get("OfficialRating")
            )
            for item in data.get("Items", [])
        ]
        return LibraryResponse(items=items, total=data.get("TotalRecordCount", 0))
