"""
SEC Compliance Rules for Fintech Marketing

Rule set focused on US SEC and FINRA regulations for financial product marketing,
advertising, and communications.

References:
- SEC Rule 206(4)-1 (Marketing Rule)
- FINRA Rule 2210 (Communications with the Public)
- SEC Guidance on AI Washing
"""

from .engine import ComplianceRule


# ──────────────────────────────────────────────
# Rule 1: Missing Risk Disclaimer on Performance
# ──────────────────────────────────────────────
missing_risk_disclaimer = ComplianceRule(
    rule_id="missing-risk-disclaimer",
    name="Missing Risk Disclaimer on Performance Claims",
    severity="high",
    jurisdiction="US",
    description="Performance claims must include risk disclaimer: "
                "'Past performance does not guarantee future results'",
    score_penalty=20,
    patterns=[
        r"(return(?:ed|s|ing)?\s+(?:\d+[\.\d]?%|[a-z]+))\s+",
        r"(performance\s+(?:of|was|is|has)\s+\d+[\.\d]?%)",
        r"(yield(?:ed|s|ing)?\s+\d+[\.\d]?%)",
        r"(grew\s+\d+[\.\d]?%)",
        r"(annualized\s+return)",
        r"(total\s+return)",
    ],
    flags=[
        r"past\s+performance\s+(?:does\s+not|is\s+not|may\s+not)",
        r"does\s+not\s+guarantee\s+(?:future\s+)?results",
        r"no\s+assurance",
        r"not\s+a\s+guarantee",
    ],
    message_template="Performance claim detected without risk disclaimer: '{passage}'",
)


# ──────────────────────────────────────────────
# Rule 2: Unsubstantiated Claims (Superlatives)
# ──────────────────────────────────────────────
unsubstantiated_claims = ComplianceRule(
    rule_id="unsubstantiated-claims",
    name="Unsubstantiated Claims / Superlatives",
    severity="high",
    jurisdiction="US",
    description="Claims using superlatives without substantiation require "
                "reasonable basis and disclosure",
    score_penalty=20,
    patterns=[
        r"\b(best(?:\s+\w+){0,3}(?:investment|fund|product|service|app|platform|rate|return))\b",
        r"\b(best\s+(?:in|on|at|for)\s+(?:the\s+)?(?:world|market|industry|class|category))\b",
        r"\b(greatest(?:\s+\w+){0,3}(?:investment|fund|product|service|app))\b",
        r"\b(top[- ]?rated|#1|number\s+one|leading)\b",
        r"\b(guaranteed(?:\s+\w+){0,4}(?:return|profit|income|growth))\b",
        r"\b(risk[- ]?free|no[- ]?risk|zero[- ]?risk|without\s+risk)\b",
        r"\b(guaranteed\s+(?:results|returns?|profits?))\b",
        r"\b(no\s+downside|no\s+loss|can'?t\s+lose|never\s+lose)\b",
        r"\b(the\s+)?(?:best|greatest|easiest|fastest|safest)\s",
        r"\b(perfect\s+(?:for|way|solution))\b",
    ],
    flags=[
        r"past\s+performance",
        r"based\s+on",
        r"according\s+to",
        r"disclaimer",
        r"may\s+not\s+be",
        r"hypothetical",
    ],
    message_template="Unsubstantiated superlative claim detected: '{passage}'",
)


# ──────────────────────────────────────────────
# Rule 3: Missing Fee Disclosure
# ──────────────────────────────────────────────
missing_fee_disclosure = ComplianceRule(
    rule_id="missing-fee-disclosure",
    name="Missing Fee Disclosure",
    severity="medium",
    jurisdiction="US",
    description="Fee-related terms must include clear fee disclosure",
    score_penalty=15,
    patterns=[
        r"\b(no\s+fe(?:e|es)|free|zero\s+fe(?:e|es)|no\s+charg(?:e|es)|no\s+cost)\b",
        r"\b(low\s+(?:fee|fees|cost|expense))\b",
        r"\b(management\s+fee|advisory\s+fee|platform\s+fee)\b",
    ],
    flags=[
        r"fee(?:s)?\s+(?:may\s+)?(?:apply|vary|incur)",
        r"(?:see|read|review)\s+(?:fee\s+)?(?:schedule|disclosure)",
        r"for\s+(?:more\s+)?(?:details|info)",
        r"may\s+be\s+subject\s+to",
    ],
    message_template="Fee claim without disclosure: '{passage}'",
)


# ──────────────────────────────────────────────
# Rule 4: Testimonials Without Disclaimer
# ──────────────────────────────────────────────
testimonial_disclaimer = ComplianceRule(
    rule_id="testimonial-disclaimer",
    name="Testimonial Without Required Disclaimer",
    severity="high",
    jurisdiction="US",
    description="Testimonials must include disclaimer that results are not typical "
                "and that compensation may have been provided",
    score_penalty=20,
    patterns=[
        r"\b(testimonial|review|rating|star[s]?)\b",
        r"\"[^\"]{30,}\"\s*[-–—]?\s*[\w\s]+",
        r"\b(our\s+client[s]?\s+(?:say|love|swear|rave))\b",
        r"\b(results?\s+(?:from|of)\s+(?:our\s+)?client)",
        r"\b(see\s+what\s+(?:our\s+)?(?:users|customers|clients))\b",
    ],
    flags=[
        r"(?:results|experience)\s+(?:are\s+)?(?:not\s+)?(?:typical|guaranteed)",
        r"(?:not\s+)?(?:everyone|all)\s+(?:gets?|experiences?)",
        r"(?:may\s+have\s+been\s+)?(?:compensated|paid)",
    ],
    message_template="Testimonial detected without required disclaimer: '{passage}'",
)


# ──────────────────────────────────────────────
# Rule 5: Missing Risk Warning on Investment Products
# ──────────────────────────────────────────────
risk_warning_investment = ComplianceRule(
    rule_id="risk-warning-investment",
    name="Missing Risk Warning on Investment Products",
    severity="critical",
    jurisdiction="US",
    description="Investment product marketing must include appropriate risk warnings",
    score_penalty=30,
    patterns=[
        r"\b(invest(?:ment|ing)?\s+(?:in|with|through))\b.{0,100}\b(grow|earn|return|profit|income)\b",
        r"\b(trade|trading)\b.{0,100}\b(profit|income|earnings|returns)\b",
        r"\b(crypto|digital\s+asset|token)\b.{0,100}\b(invest|grow|return|profit)\b",
        r"\b(high[- ]?yield|high[- ]?return)\b",
        r"\b(passive\s+income|monthly\s+income|steady\s+income)\b",
    ],
    flags=[
        r"risk(?:s|y)?\s+(?:of\s+)?(?:loss|volatility)",
        r"may\s+(?:lose|lost|result\s+in\s+loss)",
        r"not\s+(?:fdic|insured|guaranteed)",
        r"can\s+(?:go\s+)?(?:down|lose)",
        r"investment\s+involves?\s+risk",
    ],
    message_template="Investment product promotion missing risk warning: '{passage}'",
)


# ──────────────────────────────────────────────
# Rule 6: AI Disclosure for AI-Powered Tools
# ──────────────────────────────────────────────
ai_disclosure = ComplianceRule(
    rule_id="ai-disclosure",
    name="Missing AI/Algorithm Disclosure",
    severity="medium",
    jurisdiction="US",
    description="AI-powered financial tools must disclose limitations, "
                "biases, and that AI is not a financial advisor",
    score_penalty=15,
    patterns=[
        r"\b(AI|A\.I\.|artificial\s+intelligence|ML|machine\s+learning)\b.{0,50}\b(advis\w*|recommend\w*|predict\w*|forecast\w*|optimiz\w*)\b",
        r"\b(robo[- ]?advisor|robo[- ]?adviser|automated\s+advisor)\b",
        r"\b(AI|A\.I\.|artificial\s+intelligence)\b.{0,50}\b(trad\w*|invest\w*|portfolio)\b",
        r"\b(AI|A\.I\.|artificial\s+intelligence|ML|machine\s+learning)\b.{0,50}\b(analyz\w*|strateg\w*|manag\w*)\b",
        r"\b(AI|ML|algorithmic?)\b.{0,30}\b(trad\w*|investments?)\b",
    ],
    flags=[
        r"not\s+(?:a\s+)?(?:financial\s+)?(?:advisor|adviser)",
        r"for\s+(?:informational|educational)\s+purposes\s+only",
        r"may\s+(?:not\s+)?(?:be\s+)?(?:accurate|complete|reliable)",
        r"consult\s+(?:a\s+)?(?:professional|advisor|planner)",
    ],
    message_template="AI-powered financial tool missing AI limitations disclosure: '{passage}'",
)
