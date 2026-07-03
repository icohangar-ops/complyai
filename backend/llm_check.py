"""
LLM-Based Compliance Review (Optional Enhancement)

For MVP 2 or when API key is configured. Used to catch nuanced compliance
issues that regex rules miss — sarcasm, implied claims, context-dependent risks.

Set OPENAI_API_KEY or ANTHROPIC_API_KEY in environment to enable.
"""

import os
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# Built-in flag (not required for MVP) — returns empty when no API key
ENABLED = bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))


async def llm_review(text: str, jurisdiction: str = "US") -> List[Dict]:
    """
    Run LLM-based compliance review on text.
    Returns list of potential issues with higher-level reasoning.

    Currently a stub — returns empty list until API key is configured.
    """
    if not ENABLED:
        logger.info("LLM review disabled — no API key configured")
        return []

    # TODO: Implement LLM review for MVP 2
    # - Ask LLM to identify compliance issues the rule engine might miss
    # - Look for: misleading context, buried disclosures, implied guarantees
    # - Compare claims against known regulatory guidance
    return []
