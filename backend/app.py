"""
ComplyAI Backend — FastAPI Server

Endpoints:
- POST /check — Run compliance check on text
- GET  /rules — List available compliance rules
- GET  /health — Health check
"""

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rules.engine import RuleEngine

# ─── Logging ────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("complyai")

# ─── App Setup ──────────────────────────────────
app = FastAPI(
    title="ComplyAI",
    description="AI-powered compliance review for fintech marketing",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Chrome extension needs this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Rule Engine ────────────────────────────────
engine = RuleEngine()
logger.info(f"Loaded {sum(len(v) for v in engine.rules.values())} rules across {len(engine.rules)} jurisdictions")


# ─── Models ─────────────────────────────────────
class CheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000, description="Text to analyze for compliance")
    jurisdiction: str = Field(default="US", description="Jurisdiction: US, UK, or ALL")


class FlagItem(BaseModel):
    rule: str
    severity: str
    passage: str
    message: str
    jurisdiction: str


class CheckResponse(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Compliance score 0-100")
    flags: list[FlagItem] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)


# ─── Endpoints ──────────────────────────────────

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "rules_loaded": sum(len(v) for v in engine.rules.values()),
        "jurisdictions": list(engine.rules.keys()),
    }


@app.post("/check", response_model=CheckResponse)
async def check_compliance(req: CheckRequest):
    """
    Analyze text for compliance violations.

    Returns compliance score (0-100) and list of flagged items.
    Lower score = more violations found.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Validate jurisdiction
    valid_jurisdictions = list(engine.rules.keys())
    if req.jurisdiction not in valid_jurisdictions and req.jurisdiction != "ALL":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid jurisdiction '{req.jurisdiction}'. Valid: {valid_jurisdictions + ['ALL']}",
        )

    result = engine.check(req.text, jurisdiction=req.jurisdiction)
    return result


@app.get("/rules")
async def list_rules(jurisdiction: Optional[str] = None):
    """List all registered compliance rules."""
    rules = engine.list_rules(jurisdiction=jurisdiction)
    return {
        "rules": rules,
        "count": len(rules),
    }


# ─── Main ───────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8787)
