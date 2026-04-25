import requests
import pandas as pd
from pathlib import Path

BASE = "http://127.0.0.1:8001/api"

print("Health:")
r = requests.get(f"{BASE}/health", timeout=20)
print(r.status_code, r.json())

print("\nNarrative:")
payload = {
    "period": "Q3 2026",
    "kpis": {
        "Headcount": 1420,
        "Attrition Rate": "18%",
        "High Risk Count": 87,
        "Engagement Index": "68/100",
    },
}
r = requests.post(f"{BASE}/narrative", json=payload, timeout=60)
print(r.status_code)
print(r.json())

print("\nAsk:")
r = requests.post(
    f"{BASE}/ask",
    json={"question": "What does our retention policy say about stay interviews?"},
    timeout=60,
)
print(r.status_code)
print(r.json())

print("\nExplain risk:")
risk = pd.read_parquet(Path("lakehouse/gold/fact_attrition_risk.parquet"))
employee_id = risk.sort_values("RiskScore", ascending=False).iloc[0]["EmployeeID"]

r = requests.post(
    f"{BASE}/explain-risk",
    json={"employee_id": employee_id},
    timeout=60,
)
print(r.status_code)
print(r.json())
