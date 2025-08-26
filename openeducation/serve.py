from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from .utils.io import read_json
from .dashboard.routes import router as dashboard_router

app = FastAPI(title="OpenEducation API")

# Mount static files
app.mount("/static", StaticFiles(directory="openeducation/dashboard/static"), name="static")

# Include routers
app.include_router(dashboard_router, tags=["Dashboard"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/deck/summary")
def deck_summary(run_dir: str = "data/runs/latest"):
    cards_path = os.path.join(run_dir, "cards.json")
    if not os.path.exists(cards_path):
        raise HTTPException(404, f"No cards.json found in {run_dir}")
    cards = read_json(cards_path)
    return {"count": len(cards), "tags": sorted({t for c in cards for t in c.get("tags", [])})}


@app.get("/deck/card/{card_id}")
def deck_card(card_id: str, run_dir: str = "data/runs/latest"):
    cards_path = os.path.join(run_dir, "cards.json")
    if not os.path.exists(cards_path):
        raise HTTPException(404, "No cards.json found")
    cards = read_json(cards_path)
    for c in cards:
        if c["id"] == card_id:
            return c
    raise HTTPException(404, f"Card {card_id} not found")
