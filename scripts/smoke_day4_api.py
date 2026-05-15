import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "artifacts" / "day4"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "http://127.0.0.1:8001/api"
STDOUT = REPORT_DIR / "api_smoke_stdout.log"
STDERR = REPORT_DIR / "api_smoke_stderr.log"
REPORT = REPORT_DIR / "day4_api_smoke_report.json"


def wait_for_api(timeout_seconds: int = 30) -> dict:
    last_error = None
    for _ in range(timeout_seconds):
        try:
            r = requests.get(f"{API_URL}/health", timeout=3)
            if r.ok:
                return r.json()
            last_error = f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as exc:
            last_error = str(exc)
        time.sleep(1)
    raise RuntimeError(f"API did not become ready. Last error: {last_error}")


def post_json(path: str, payload: dict) -> dict:
    r = requests.post(f"{API_URL}{path}", json=payload, timeout=60)
    content_type = r.headers.get("content-type", "")
    response = r.json() if content_type.startswith("application/json") else r.text
    return {
        "ok": r.ok,
        "status_code": r.status_code,
        "response": response,
    }


def main() -> None:
    risk = pd.read_parquet(ROOT / "lakehouse" / "gold" / "fact_attrition_risk.parquet")
    emp_id = str(risk.sort_values("RiskScore", ascending=False).iloc[0]["EmployeeID"])

    with STDOUT.open("w", encoding="utf-8") as out, STDERR.open("w", encoding="utf-8") as err:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
            cwd=ROOT / "apps" / "api",
            stdout=out,
            stderr=err,
            text=True,
        )

        try:
            health = wait_for_api()

            narrative = post_json(
                "/narrative",
                {
                    "period": "Q3 2026",
                    "kpis": {
                        "Headcount": 1420,
                        "Attrition Rate": "18%",
                        "Attrition Rate YoY": "+4pp",
                        "Engagement Index": "3.4 / 5",
                        "High Risk Employees": 87,
                    },
                },
            )

            ask = post_json(
                "/ask",
                {
                    "question": "What does our retention policy say about employees with elevated flight risk?"
                },
            )

            explain = post_json(
                "/explain-risk",
                {
                    "employee_id": emp_id
                },
            )

            report = {
                "health": health,
                "selected_employee_id": emp_id,
                "narrative": narrative,
                "ask": ask,
                "explain_risk": explain,
            }

            REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

            failures = []
            if not narrative["ok"]:
                failures.append("narrative")
            if not ask["ok"]:
                failures.append("ask")
            if not explain["ok"]:
                failures.append("explain-risk")

            print("DAY 4 API SMOKE REPORT")
            print(f"health: {health}")
            print(f"selected_employee_id: {emp_id}")
            print(f"narrative ok: {narrative['ok']}")
            print(f"ask ok: {ask['ok']}")
            print(f"explain-risk ok: {explain['ok']}")
            print(f"report: {REPORT}")

            if failures:
                raise SystemExit(f"Failed endpoints: {failures}")

            print("DAY 4 API SMOKE PASSED")

        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()
