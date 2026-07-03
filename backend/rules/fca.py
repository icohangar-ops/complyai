"""
FCA Compliance Rules for Fintech Marketing (Placeholder)

UK Financial Conduct Authority rules for financial promotions and marketing.
Rules will be expanded for MVP 2.

References:
- FCA COBS 4 (Communicating with clients)
- FCA PERG 8 (Financial promotions)
- FCA FG20/1 (Social media guidance)
"""

from .engine import ComplianceRule

# ──────────────────────────────────────────────
# Placeholder Rule: Financial Promotion Approval
# ──────────────────────────────────────────────
financial_promotion_approval = ComplianceRule(
    rule_id="fca-financial-promotion",
    name="Financial Promotion Approval (FCA)",
    severity="high",
    jurisdiction="UK",
    description="Financial promotions require FCA approval or approval by an "
                "FCA-authorised person. Placeholder rule.",
    score_penalty=20,
    patterns=[
        r"\b(invest|saving|pension|ISA|SIPP|fund)\b.{0,100}\b(return|growth|income|profit)\b",
    ],
    flags=[
        r"FCA[- ]?(?:registered|authorised|regulated)",
        r"authorised\s+(?:and\s+)?regulated",
        r"Financial\s+Conduct\s+Authority",
    ],
    message_template="Financial promotion detected - may require FCA approval: '{passage}'",
)
