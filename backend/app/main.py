from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import httpx
from fastapi import FastAPI, HTTPException
load_dotenv()
FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")

app = FastAPI()

class PlayerProfile(BaseModel):
    nickname: str
    country: str
    level: int
    elo: int

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/players/{nickname}", response_model=PlayerProfile)
def get_player(nickname: str):
    headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}
    url = "https://open.faceit.com/data/v4/players"
    params = {"nickname":nickname,"game":"cs2"}
    response = httpx.get(url, headers=headers,
    params=params)
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Player not found") 
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Faceit API Error")
   
    data = response.json()
    if "cs2" not in data["games"]:
        raise HTTPException(status_code=404, detail="CS2 not installed on this player")
    return PlayerProfile(
        nickname=data["nickname"],
        country=data["country"],
        level=data["games"]["cs2"]["skill_level"],
        elo=data["games"]["cs2"]["faceit_elo"],
)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")