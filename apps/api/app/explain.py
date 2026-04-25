from pathlib import Path
import os

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv


EXPLAIN_PROMPT = """Rewrite the following attrition risk explanation in plain English for a non-technical manager.

Use this format:
"This employee's attrition risk is <LOW|MEDIUM|HIGH> ({score}%). The main drivers are:
1. [plain English description of driver 1 and its direction]
2. [plain English description of driver 2 and its direction]
3. [plain English description of driver 3 and its direction]

Suggested manager action: [one concrete, supportive step]."

Do NOT invent data.
Only use what is provided.
Positive SHAP values push risk up. Negative SHAP values push risk down.

RISK SCORE: {score}
RISK BAND: {band}

DRIVERS:
1. {d1_name} ({d1_val:+.3f})
2. {d2_name} ({d2_val:+.3f})
3. {d3_name} ({d3_val:+.3f})
"""


def _driver_direction(value: float) -> str:
    return "increases risk" if value > 0 else "reduces risk"


def _fallback_explanation(r) -> str:
    score = round(float(r["RiskScore"]) * 100, 1)
    return (
        f"This employee's attrition risk is {str(r['RiskBand']).upper()} ({score}%). The main drivers are:\n"
        f"1. {r['TopDriver1']} ({_driver_direction(float(r['TopDriver1Impact']))}).\n"
        f"2. {r['TopDriver2']} ({_driver_direction(float(r['TopDriver2Impact']))}).\n"
        f"3. {r['TopDriver3']} ({_driver_direction(float(r['TopDriver3Impact']))}).\n\n"
        "Suggested manager action: schedule a supportive stay-interview and review workload, progression, and manager-support factors before taking any formal action."
    )


def explain_risk(employee_id: str, root: Path) -> dict:
    load_dotenv(root / ".env")

    gold = Path(os.getenv("GOLD_LAKEHOUSE_PATH", str(root / "lakehouse/gold")))
    if not gold.is_absolute():
        gold = root / gold

    risk_path = gold / "fact_attrition_risk.parquet"

    if not risk_path.exists():
        raise FileNotFoundError(f"Missing risk table: {risk_path}")

    df = pd.read_parquet(risk_path)
    row = df[df["EmployeeID"] == employee_id]

    if row.empty:
        return {"error": f"Employee {employee_id} not found"}

    r = row.iloc[0]

    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    explanation = _fallback_explanation(r)

    if api_key and not api_key.startswith("YOUR_"):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)

            prompt = EXPLAIN_PROMPT.format(
                score=round(float(r["RiskScore"]) * 100, 1),
                band=r["RiskBand"],
                d1_name=r["TopDriver1"],
                d1_val=float(r["TopDriver1Impact"]),
                d2_name=r["TopDriver2"],
                d2_val=float(r["TopDriver2Impact"]),
                d3_name=r["TopDriver3"],
                d3_val=float(r["TopDriver3Impact"]),
            )

            response = model.generate_content(prompt)
            explanation = response.text
        except Exception:
            explanation = _fallback_explanation(r)

    return {
        "employee_id": employee_id,
        "risk_score": float(r["RiskScore"]),
        "risk_band": r["RiskBand"],
        "top_drivers": [
            {"driver": r["TopDriver1"], "impact": float(r["TopDriver1Impact"])},
            {"driver": r["TopDriver2"], "impact": float(r["TopDriver2Impact"])},
            {"driver": r["TopDriver3"], "impact": float(r["TopDriver3Impact"])},
        ],
        "explanation": explanation,
    }
