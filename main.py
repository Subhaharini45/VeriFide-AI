"""
main.py
-------
FastAPI entry point for VeriFied-AI.

Routes:
    GET  /       -> Render the dashboard (form + most recent audit result, if any)
    POST /audit  -> Run the audit agent on submitted text, persist it, redirect to "/"

Run with:
    uvicorn app.main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import database
from app.agents import run_audit_agent

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="VeriFied-AI Forensic Auditor")

# Static assets (CSS)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
def on_startup() -> None:
    """Ensure the database and table exist before serving requests."""
    database.init_db()


@app.get("/")
def dashboard(request: Request):
    """Render the dashboard with the form and the latest audit result (if any)."""
    latest_audit = database.get_latest_audit()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "audit": latest_audit,
        },
    )


@app.post("/audit")
def audit(input_text: str = Form(...)):
    """
    Run the forensic audit agent on the submitted text, persist the result,
    then redirect back to the dashboard so the result renders via GET /.
    """
    result = run_audit_agent(input_text)

    database.save_audit(
        verdict=result["verdict"],
        system_health_index=result["system_health_index"],
        summary_notes=result["summary"],
        anomalies_detected=result["anomalies"],
    )

    # Redirect (303) so the browser issues a GET after the POST, avoiding
    # duplicate form resubmission on refresh.
    return RedirectResponse(url="/", status_code=303)
