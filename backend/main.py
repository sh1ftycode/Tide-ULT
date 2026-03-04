from fastapi import FastAPI
from dotenv import load_dotenv
import os
import httpx
from pydantic import BaseModel
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TideULT",
    description="The all-in-one media server that brings everything to shore.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/ui")
async def serve_frontend():
    return FileResponse("../frontend/index.html")
    
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

@app.get("/poster/{item_id}")
async def get_poster(item_id: str):
    from fastapi.responses import RedirectResponse
    url = f"{JELLYFIN_URL}/Items/{item_id}/Images/Primary?api_key={JELLYFIN_KEY}"
    return RedirectResponse(url)
