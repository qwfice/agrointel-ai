"""Chat assistant backed by the Gemini API, grounded in AGROINTEL AI's own
real computed data.

This does NOT train anything - it calls Google's already-trained Gemini
model with the real indicators/scores/evidence for the current location
as context, and instructs it to answer only from that data. See PLAN.md
for why this approach (not a trained/fine-tuned model) was chosen.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.5-flash-lite"

SYSTEM_INSTRUCTION = """You are the AGROINTEL AI assistant, helping a farmer or agricultural \
expert understand the real NASA-data-driven crop-rotation analysis shown on this page.

Rules:
- Answer ONLY using the real data provided in the context below. Do not invent NASA \
observations, scores, or recommendations that aren't in the context.
- If the user asks something the provided data doesn't cover, say so plainly - for example, \
"That's not something this location's data shows" - and suggest they consult a local \
agronomist rather than guessing.
- Keep answers short and in plain language a farmer without a technical background can follow.
- Remind the user when relevant that this is decision support, not a guarantee of outcomes.
"""


def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Copy .env.example to .env and add your key "
            "from https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


def build_context(location_name: str, indicators: dict, comparisons: list[dict]) -> str:
    """Turn the real computed data for a location into a text block to ground the model."""
    lines = [f"Location: {location_name}", "", "Computed environmental indicators:"]
    for key, value in indicators.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Rotation strategy comparison (ranked):")
    for rank, comp in enumerate(comparisons, start=1):
        lines.append(f"\n{rank}. {comp['label']} - overall score {comp['overall_score']:.1f}/100")
        for criterion, score in comp["criteria_scores"].items():
            lines.append(f"   - {criterion}: {score:.1f}/100")
        lines.append("   Evidence: " + " | ".join(comp["evidence"]))
        lines.append("   Benefits: " + " | ".join(comp["benefits"]))
        lines.append("   Information gaps: " + " | ".join(comp["information_gaps"]))
        lines.append("   Risks: " + " | ".join(comp["risks"]))

    return "\n".join(lines)


def ask(question: str, context: str) -> str:
    """Ask the assistant a question, grounded in the given real-data context."""
    client = get_client()
    prompt = f"Context (real computed data for this location):\n{context}\n\nUser question: {question}"
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"system_instruction": SYSTEM_INSTRUCTION},
    )
    return response.text
