"""Public API wrapping AGROINTEL AI's real logic for other frontends
(e.g. the team's FieldCycle app on Bubble.io) to call - no logic is
duplicated here, every endpoint reuses the same src/ modules the
Streamlit app uses.

Run locally with:
    uvicorn api.main:app --reload --port 8000

Not deployed publicly yet - see PLAN.md for the deployment step.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.chat.assistant import ask, build_context
from src.explanations.narrative import build_comparison
from src.indicators.live import fetch_and_compute_indicators
from src.scoring.model import DEFAULT_WEIGHTS, rank_strategies

app = FastAPI(title="AGROINTEL AI API", version="0.1.0")

# Permissive for now (any origin can call this) since it's not deployed
# publicly yet. Tighten this to FieldCycle's actual domain before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class IndicatorsRequest(BaseModel):
    lat: float
    lon: float
    include_soil_moisture: bool = True


class ScoreRequest(BaseModel):
    indicators: dict
    weights: dict[str, float] | None = None


class ChatRequest(BaseModel):
    question: str
    location_label: str
    indicators: dict
    weights: dict[str, float] | None = None


def _comparisons_for(indicators: dict, weights: dict[str, float] | None) -> list[dict]:
    ranked = rank_strategies(indicators, weights)
    return [build_comparison(r["strategy"], r["criteria"], r["overall_score"], indicators) for r in ranked]


@app.get("/")
def root() -> dict:
    return {"service": "AGROINTEL AI API", "status": "ok"}


@app.post("/indicators")
def get_indicators(req: IndicatorsRequest) -> dict:
    """Real, live-fetched NASA-data-driven indicators for a location."""
    try:
        return fetch_and_compute_indicators(req.lat, req.lon, include_soil_moisture=req.include_soil_moisture)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not fetch NASA data for this location: {e}")


@app.post("/score")
def get_score(req: ScoreRequest) -> dict:
    """Ranked rotation-strategy comparisons (scores + evidence + benefits + gaps + risks)."""
    weights = req.weights or DEFAULT_WEIGHTS
    comparisons = _comparisons_for(req.indicators, weights)
    return {"comparisons": comparisons}


@app.post("/chat")
def post_chat(req: ChatRequest) -> dict:
    """Ask the assistant a question, grounded in the given real indicators."""
    comparisons = _comparisons_for(req.indicators, req.weights or DEFAULT_WEIGHTS)
    context = build_context(req.location_label, req.indicators, comparisons)
    try:
        answer = ask(req.question, context)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat assistant unavailable: {e}")
    return {"answer": answer}
