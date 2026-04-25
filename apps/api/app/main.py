from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .narrative import generate_narrative
from .rag import PolicyRAG
from .explain import explain_risk


ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agile-hr-copilot")

app = FastAPI(title="Agile HR Copilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_audit_path() -> Path:
    raw = os.getenv("AUDIT_LOG_PATH", "apps/api/audit.log")
    p = Path(raw)
    if not p.is_absolute():
        p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


AUDIT_LOG = _resolve_audit_path()
rag = PolicyRAG(root=ROOT)


def audit(event: dict) -> None:
    event["_ts"] = datetime.now(timezone.utc).isoformat()
    try:
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError as e:
        # Never let audit logging crash a request.
        log.warning("audit log write failed: %s", e)


class NarrativeRequest(BaseModel):
    period: str
    kpis: dict


class AskRequest(BaseModel):
    question: str


class ExplainRequest(BaseModel):
    employee_id: str


@app.get("/")
def root():
    return {
        "name": "Agile HR Copilot API",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "rag_ready": rag.is_ready(),
        "policy_chunks": rag.count(),
    }


@app.post("/api/narrative")
def narrative(req: NarrativeRequest):
    try:
        text = generate_narrative(req.period, req.kpis, root=ROOT)
        audit({"endpoint": "narrative", "period": req.period, "ok": True})
        return {"narrative": text, "period": req.period}
    except Exception as e:
        audit({"endpoint": "narrative", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask")
def ask(req: AskRequest):
    try:
        result = rag.ask(req.question)
        audit({"endpoint": "ask", "question": req.question, "ok": True})
        return result
    except Exception as e:
        audit({"endpoint": "ask", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain-risk")
def explain(req: ExplainRequest):
    try:
        result = explain_risk(req.employee_id, root=ROOT)
        audit({"endpoint": "explain-risk", "employee_id": req.employee_id, "ok": True})
        return result
    except Exception as e:
        audit({"endpoint": "explain-risk", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
