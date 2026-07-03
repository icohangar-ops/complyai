# ComplyAI — Compliance Review for Fintech Marketing

AI-powered compliance review tool. Checks fintech landing pages, marketing materials, and communications for regulatory red flags before they go live.

## Problem

> "In fintech, wrong words can cost you."

Manual compliance review of marketing materials, disclosures, and communications is painfully slow. Regulatory tightening worldwide means fintech companies need automated compliance checks.

## MVP

Chrome extension + FastAPI backend with deterministic rule engine.

### What it checks

- Missing risk disclaimers on performance claims
- Unsubstantiated claims ("best", "guaranteed", "risk-free")
- Missing fee disclosures
- Testimonials without required disclaimers
- Missing risk warnings on investment products
- Required disclosures for AI-powered financial tools

## Architecture

```
complyai/
├── README.md
├── backend/
│   ├── app.py               # FastAPI server
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── sec.py           # SEC rules
│   │   ├── fca.py           # FCA rules (placeholder)
│   │   └── engine.py        # Rule matching engine
│   └── llm_check.py         # Optional LLM enhancement
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   └── content.js
└── examples/
    └── sample_page.html
```

## Quick Start

```bash
# Install backend deps
cd backend
pip install fastapi uvicorn

# Run server
uvicorn app:app --reload --port 8787

# Load extension in Chrome
# chrome://extensions → Load unpacked → select extension/
```

## API

### POST /check

Analyze text for compliance violations.

```json
{
  "text": "Our fund returned 25% last year. It's the best investment available.",
  "jurisdiction": "US"
}
```

Response:
```json
{
  "score": 45,
  "flags": [
    {
      "rule": "unsubstantiated-claims",
      "severity": "high",
      "passage": "best investment available",
      "message": "Avoid superlative unsubstantiated claims"
    },
    {
      "rule": "missing-risk-disclaimer",
      "severity": "high",
      "passage": "returned 25% last year",
      "message": "Performance claims need risk disclaimer"
    }
  ]
}
```

### GET /health

Health check endpoint.

## Jurisdictions

- **US** (SEC) — Full rule set
- **UK** (FCA) — Placeholder, rules coming
- **EU** — Coming soon

## License

MIT
