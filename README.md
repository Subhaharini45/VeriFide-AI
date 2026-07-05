# VeriFied-AI

An automated forensic auditor dashboard built with **FastAPI**, **Jinja2**, and **SQLite**. Paste in a financial record or statement, run an automated audit, and get back a verdict, health integrity score, executive summary, and a list of detected anomalies.

> ⚠️ **Note:** The audit logic in `agents.py` is a heuristic mock (keyword/pattern based), not a real compliance engine or ML model. It's meant as a realistic placeholder to build on top of — see [Audit Logic](#audit-logic) below.

## Features

- Submit any text (invoice, statement, transaction log, etc.) via a simple web form
- Automated heuristic audit flags common red flags: round numbers, hedging language, missing dates, contradictory statements, unsubstantiated claims, and insufficient detail
- Results are scored 0–100 and bucketed into a verdict: `CLEAN`, `REVIEW RECOMMENDED`, or `NON-COMPLIANT`
- All audits are persisted to a local SQLite database
- Dark-themed dashboard UI with a red result card highlighting anomalies

## Project Structure

```
VeriFied-AI/
└── app/
    ├── __init__.py
    ├── main.py            # FastAPI app, routes, template rendering
    ├── agents.py           # run_audit_agent() — the audit heuristic
    ├── database.py         # SQLite setup, save/get audit records
    ├── templates/
    │   └── dashboard.html  # Jinja2 dashboard template
    ├── static/
    │   └── style.css       # Dashboard styling
    └── verifed_ai.db        # SQLite database (created automatically on first run)
```

## Requirements

- Python 3.9+
- FastAPI
- Uvicorn
- Jinja2
- python-multipart (required for form submissions)

## Installation

```bash
pip install fastapi uvicorn jinja2 python-multipart
```

## Running the App

From the project root (the folder **containing** `app/`, not inside it):

```bash
python -m uvicorn app.main:app --reload
```

Then open your browser to:

```
http://127.0.0.1:8000
```

> If the `uvicorn` command isn't recognized directly, use `python -m uvicorn ...` instead — this avoids PATH issues with pip-installed console scripts.

## Usage

1. Paste a record, statement, or transaction text into the textarea.
2. Click **Run Automated Forensic Audit**.
3. The app analyzes the text, saves the result, and redirects back to the dashboard showing:
   - **Verdict** — `CLEAN`, `REVIEW RECOMMENDED`, or `NON-COMPLIANT`
   - **Health Integrity Score** — 0–100
   - **Executive Summary** — a plain-language recap of the findings
   - **Detected Anomalies** — individual flagged issues with type and description

## Audit Logic

`run_audit_agent(text)` in `agents.py` currently checks for:

| Anomaly Type | Trigger |
|---|---|
| Suspicious Rounding | Round numbers (e.g. `500,000`) in the text |
| Evasive Language | Hedging phrases like "approximately", "we believe" |
| Missing Temporal Reference | No 4-digit year found in the text |
| Contradictory Statement | Both "profit" and "loss" mentioned |
| Unsubstantiated Claim | Superlatives like "guaranteed", "risk-free" |
| Insufficient Detail | Submitted text is under 40 characters |

Each detected anomaly deducts 14 points from a base score of 100. The final score maps to a verdict:

- **≥ 85** → `CLEAN`
- **60–84** → `REVIEW RECOMMENDED`
- **< 60** → `NON-COMPLIANT`

To customize this logic (e.g. connect a real ML model, LLM call, or rules engine), replace the internals of `run_audit_agent` — just keep the same return shape:

```python
{
    "verdict": str,
    "system_health_index": int,   # 0-100
    "summary": str,
    "anomalies": [
        {"type": str, "description": str},
        ...
    ]
}
```

## Database Schema

Table: `compliance_audits`

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key, autoincrement |
| `timestamp` | TEXT | ISO 8601 UTC timestamp of the audit |
| `verdict` | TEXT | `CLEAN`, `REVIEW RECOMMENDED`, or `NON-COMPLIANT` |
| `system_health_index` | INTEGER | Score from 0–100 |
| `summary_notes` | TEXT | Executive summary text |
| `anomalies_detected` | TEXT | JSON-encoded list of anomaly objects |

The database file (`verifed_ai.db`) is created automatically on first run inside the `app/` directory.

## Roadmap Ideas

- Replace the heuristic mock in `agents.py` with a real LLM-based or rules-based audit engine
- Add an audit history view listing all past audits, not just the latest
- Add authentication for multi-user access
- Export audit results as PDF reports
- Configurable scoring weights and verdict thresholds

## License

Internal project — add your license of choice here.
