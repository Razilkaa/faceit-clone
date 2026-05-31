from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import httpx
from fastapi import FastAPI, HTTPException
from datetime import datetime
load_dotenv()
FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")

app = FastAPI()

class MatchSummary(BaseModel):
    match_id: str
    result: str
    score: str
    competition_type: str
    finished_at: str
class PlayerProfile(BaseModel):
    nickname: str
    country: str
    level: int
    elo: int
    matches: list[MatchSummary]

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
    player_id = data["player_id"]
    url2 = f"https://open.faceit.com/data/v4/players/{player_id}/history"
    params2 = {"game":"cs2", "limit":10}
    response2 = httpx.get(url2, headers=headers,params=params2)
    if response2.status_code == 404:
        raise HTTPException(status_code=404, detail="Player not found") 
    if response2.status_code != 200:
        raise HTTPException(status_code=502, detail="Faceit API Error")
    history = response2.json()
    matches = []
    for item in history["items"]:
        my_faction = "faction2"
        for player in item["teams"]["faction1"]["players"]:
            if player["player_id"] == player_id:
                my_faction = "faction1"
                break
        winner = item["results"]["winner"]
        if my_faction == winner:
            result = "win" 
        else:
            result = "loss"    
        score_dict = item["results"]["score"]
        score = f'{score_dict["faction1"]}:{score_dict["faction2"]}'
        finished = datetime.fromtimestamp(item["finished_at"]).strftime("%Y-%m-%d %H:%M")
        matches.append(MatchSummary(
            match_id=item["match_id"],
            result=result,
            score=score,
            competition_type=item["competition_type"],
            finished_at=finished
        ))
    return PlayerProfile(
        nickname=data["nickname"],
        country=data["country"],
        level=data["games"]["cs2"]["skill_level"],
        elo=data["games"]["cs2"]["faceit_elo"],
        matches=matches
)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")