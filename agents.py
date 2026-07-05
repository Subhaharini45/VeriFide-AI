"""
agents.py
---------
Core "forensic audit" logic.

NOTE: No real detection model, rules engine, or external API was specified
for this project, so `run_audit_agent` below is a self-contained heuristic
mock: it scans the input text for a handful of red-flag patterns (round
numbers, hedging language, missing dates, contradictory terms, etc.) and
turns them into a verdict + health score + anomaly list. It's meant as a
realistic stand-in you can later replace with a real LLM call, ML model,
or rules engine -- the function signature and return shape are the
contract the rest of the app (main.py / database.py) relies on.
"""

import re
from typing import Dict, Any, List


def _detect_anomalies(text: str) -> List[Dict[str, str]]:
    """Run a series of lightweight heuristic checks against the input text."""
    anomalies: List[Dict[str, str]] = []
    lower = text.lower()

    # 1. Round-number bias (common red flag in fabricated financial figures)
    if re.search(r"\b\d{1,3}(,000|0000)\b", text):
        anomalies.append({
            "type": "Suspicious Rounding",
            "description": "Financial figures contain unusually round numbers, "
                            "which can indicate estimation or fabrication rather than actuals.",
        })

    # 2. Hedging / evasive language
    hedge_terms = ["approximately", "roughly", "we believe", "to our knowledge", "as far as we know"]
    if any(term in lower for term in hedge_terms):
        anomalies.append({
            "type": "Evasive Language",
            "description": "Document contains hedging phrases that may signal uncertainty "
                            "or an attempt to obscure precise figures.",
        })

    # 3. Missing date references
    if not re.search(r"\b(20\d{2}|19\d{2})\b", text):
        anomalies.append({
            "type": "Missing Temporal Reference",
            "description": "No clear date or fiscal year could be identified in the submitted text.",
        })

    # 4. Contradictory terms in close proximity (e.g. "profit" and "loss")
    if "profit" in lower and "loss" in lower:
        anomalies.append({
            "type": "Contradictory Statement",
            "description": "Text references both profit and loss in a way that may indicate "
                            "inconsistent reporting.",
        })

    # 5. Excessive superlatives (marketing language creeping into compliance docs)
    superlatives = ["guaranteed", "risk-free", "unprecedented", "flawless"]
    if any(term in lower for term in superlatives):
        anomalies.append({
            "type": "Unsubstantiated Claim",
            "description": "Text uses absolute or promotional language atypical of "
                            "objective compliance reporting.",
        })

    # 6. Very short submissions carry inherent audit risk (not enough to verify)
    if len(text.strip()) < 40:
        anomalies.append({
            "type": "Insufficient Detail",
            "description": "Submitted text is too brief to perform a comprehensive audit; "
                            "key context may be missing.",
        })

    return anomalies


def _score_from_anomalies(anomalies: List[Dict[str, str]]) -> int:
    """Derive a 0-100 health index: fewer/less severe anomalies -> higher score."""
    base_score = 100
    penalty_per_anomaly = 14
    score = base_score - (len(anomalies) * penalty_per_anomaly)
    return max(0, min(100, score))


def _verdict_from_score(score: int) -> str:
    if score >= 85:
        return "CLEAN"
    elif score >= 60:
        return "REVIEW RECOMMENDED"
    else:
        return "NON-COMPLIANT"


def _summary_from_findings(verdict: str, score: int, anomalies: List[Dict[str, str]]) -> str:
    if not anomalies:
        return (
            "The submitted record shows no material red flags. Language, figures, "
            "and structure are consistent with standard compliant reporting practices."
        )

    anomaly_types = ", ".join(a["type"] for a in anomalies)
    return (
        f"Automated review flagged {len(anomalies)} issue(s) ({anomaly_types}) "
        f"resulting in a system health index of {score}/100. Verdict: {verdict}. "
        "Manual review by a compliance officer is advised before this record is finalized."
    )


def run_audit_agent(text: str) -> Dict[str, Any]:
    """
    Run the forensic audit heuristic against the given input text.

    Returns a dict with:
        - verdict: str
        - system_health_index: int (0-100)
        - summary: str
        - anomalies: List[Dict[str, str]]  # each has "type" and "description"
    """
    text = text or ""
    anomalies = _detect_anomalies(text)
    score = _score_from_anomalies(anomalies)
    verdict = _verdict_from_score(score)
    summary = _summary_from_findings(verdict, score, anomalies)

    return {
        "verdict": verdict,
        "system_health_index": score,
        "summary": summary,
        "anomalies": anomalies,
    }
