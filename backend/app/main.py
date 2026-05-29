from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI()

class PlayerProfile(BaseModel):
    nickname: str
    country: str
    level: int
    elo: int
    matches: int

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/players/{nickname}", response_model=PlayerProfile)
def get_player(nickname:str):
    return PlayerProfile(
        nickname=nickname,
        country="Russia",
        level=10,
        elo=2001,
        matches=724,
)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")