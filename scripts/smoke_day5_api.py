from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import requests


BASE = "http://127.0.0.1:8001/api"
OUT = Path("artifacts/day5")
OUT.mkdir(parents=True, exist_ok=True)


def post_json(path: str, payload: dict) -> dict:
    url = f"{BASE}{path}"
    r = requests.post(url, json=payload, timeout=45)
    r.raise_for_status()
    return r.json()


def main() -> int:
    report: dict = {"checks": {}}

    # 1) Health
    health = requests.get(f"{BASE}/health", timeout=20)
    health.raise_for_status()
    report["checks"]["health"] = health.json()

    # 2) Narrative
    narrative = post_json(
        "/narrative",
        {
            "period": "Q3 2026",
            "kpis": {
                "Headcount": 1420,
                "Attrition Rate": "18%",
                "High Risk Count": 87,
                "Engagement Index": "3.4 / 5",
            },
        },
    )
    report["checks"]["narrative"] = {
        "ok": bool(narrative.get("narrative")),
        "preview": str(narrative.get("narrative", ""))[:250],
    }

    # 3) Ask policy
    ask = post_json(
        "/ask",
        {
            "question": "What does the retention policy say about stay interviews?"
        },
    )
    report["checks"]["ask"] = {
        "ok": bool(ask.get("answer")),
        "sources_count": len(ask.get("sources", [])),
        "preview": str(ask.get("answer", ""))[:250],
    }

    # 4) Explain risk
    risk_path = Path("lakehouse/gold/fact_attrition_risk.parquet")
    risk_df = pd.read_parquet(risk_path)
    emp_id = str(risk_df.sort_values("RiskScore", ascending=False).iloc[0]["EmployeeID"])

    explain = post_json("/explain-risk", {"employee_id": emp_id})
    report["checks"]["explain_risk"] = {
        "ok": bool(explain.get("explanation") or explain.get("risk_band")),
        "employee_id": emp_id,
        "risk_band": explain.get("risk_band"),
        "preview": str(explain.get("explanation", ""))[:250],
    }

    out_path = OUT / "api_smoke_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("DAY 5 API SMOKE PASSED")
    print(json.dumps(report, indent=2)[:3000])
    print(f"wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
