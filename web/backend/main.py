import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from routers import games, players, teams

app = FastAPI(title="PitchFrame API")

app.include_router(games.router)
app.include_router(teams.router)
app.include_router(players.router)


@app.get("/")
def root():
    return {"status": "ok"}
