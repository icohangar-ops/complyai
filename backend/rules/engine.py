"""
Compliance Rule Matching Engine

Deterministic, regex-based rule engine for fintech marketing compliance.
Works without LLM for the MVP — pure pattern matching + scoring.
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ComplianceFlag:
    """A single compliance violation flag."""

    def __init__(self, rule: str, severity: str, passage: str, message: str, jurisdiction: str = "US"):
        self.rule = rule
        self.severity = severity  # 'critical' | 'high' | 'medium' | 'low'
        self.passage = passage
        self.message = message
        self.jurisdiction = jurisdiction

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "passage": self.passage,
            "message": self.message,
            "jurisdiction": self.jurisdiction,
        }

    def __repr__(self):
        return f"[{self.severity.upper()}] {self.rule}: {self.message}"


class ComplianceRule:
    """A single compliance rule with patterns and scoring."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        severity: str,
        jurisdiction: str,
        description: str,
        score_penalty: int,
        patterns: List[str],
        flags: List[str],
        message_template: str,
    ):
        self.rule_id = rule_id
        self.name = name
        self.severity = severity
        self.jurisdiction = jurisdiction
        self.description = description
        self.score_penalty = score_penalty
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.flags = [re.compile(f, re.IGNORECASE) for f in flags]
        self.message_template = message_template

    def check(self, text: str) -> List[ComplianceFlag]:
        """Run this rule against text, return flags for matches."""
        flags = []
        for pattern in self.patterns:
            for match in pattern.finditer(text):
                passage = match.group().strip()
                # Check if any flagging pattern is absent when needed
                if self.flags:
                    has_flag = any(f.search(text) for f in self.flags)
                    if not has_flag:
                        flags.append(ComplianceFlag(
                            rule=self.rule_id,
                            severity=self.severity,
                            passage=passage,
                            message=self.message_template.format(passage=passage),
                            jurisdiction=self.jurisdiction,
                        ))
                else:
                    # Simple pattern match = violation
                    flags.append(ComplianceFlag(
                        rule=self.rule_id,
                        severity=self.severity,
                        passage=passage,
                        message=self.message_template.format(passage=passage),
                        jurisdiction=self.jurisdiction,
                    ))
        return flags


class RuleEngine:
    """Manages and executes compliance rules across jurisdictions."""

    def __init__(self):
        self.rules: Dict[str, List[ComplianceRule]] = {}  # jurisdiction -> rules
        self._load_rules()

    def _load_rules(self):
        """Load all default rules."""
        from . import sec
        self._register_rule(sec.missing_risk_disclaimer)
        self._register_rule(sec.unsubstantiated_claims)
        self._register_rule(sec.missing_fee_disclosure)
        self._register_rule(sec.testimonial_disclaimer)
        self._register_rule(sec.risk_warning_investment)
        self._register_rule(sec.ai_disclosure)

        # Load FCA placeholders if available
        try:
            from . import fca
            self._register_rule(fca.financial_promotion_approval)
        except (ImportError, AttributeError):
            logger.info("FCA rules not fully loaded (placeholder)")

    def _register_rule(self, rule: ComplianceRule):
        j = rule.jurisdiction
        if j not in self.rules:
            self.rules[j] = []
        self.rules[j].append(rule)

    def check(self, text: str, jurisdiction: str = "US") -> dict:
        """
        Run compliance check on text for a given jurisdiction.
        Returns score + list of flags.
        """
        if not text or not text.strip():
            return {"score": 100, "flags": [], "summary": {"critical": 0, "high": 0, "medium": 0, "low": 0}}

        all_flags = []
        # Check requested jurisdiction
        if jurisdiction in self.rules:
            for rule in self.rules[jurisdiction]:
                all_flags.extend(rule.check(text))

        # Also always check generic rules (jurisdiction=None or all)
        if "ALL" in self.rules:
            for rule in self.rules["ALL"]:
                all_flags.extend(rule.check(text))

        # Calculate score
        score = self._calculate_score(text, all_flags)
        summary = self._summarize(all_flags)

        return {
            "score": score,
            "flags": [f.to_dict() for f in all_flags],
            "summary": summary,
        }

    def _calculate_score(self, text: str, flags: List[ComplianceFlag]) -> int:
        """Calculate compliance score 0-100."""
        # Severity penalties
        severity_penalties = {
            "critical": 30,
            "high": 20,
            "medium": 10,
            "low": 5,
        }

        total_penalty = 0
        seen_rules = set()

        for flag in flags:
            # Deduplicate by rule type for penalty stacking (multiple instances stack)
            penalty = severity_penalties.get(flag.severity, 10)
            total_penalty += penalty

        score = max(0, min(100, 100 - total_penalty))
        return score

    def _summarize(self, flags: List[ComplianceFlag]) -> dict:
        """Summarize flags by severity."""
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in flags:
            sev = f.severity.lower()
            if sev in summary:
                summary[sev] += 1
        return summary

    def list_rules(self, jurisdiction: Optional[str] = None) -> List[dict]:
        """List all registered rules."""
        result = []
        for j, rules in self.rules.items():
            if jurisdiction and j != jurisdiction:
                continue
            for r in rules:
                result.append({
                    "rule_id": r.rule_id,
                    "name": r.name,
                    "severity": r.severity,
                    "jurisdiction": r.jurisdiction,
                    "description": r.description,
                    "score_penalty": r.score_penalty,
                    "patterns": [p.pattern for p in r.patterns],
                })
        return result
