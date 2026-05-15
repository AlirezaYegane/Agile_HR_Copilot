from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

GOLD = Path("lakehouse/gold")

src = GOLD / "fact_recruitment.parquet"
out = GOLD / "fact_recruitment_stage.parquet"

if not src.exists():
    raise FileNotFoundError(f"Missing {src}")

df = pd.read_parquet(src)
df["AppliedDate"] = pd.to_datetime(df["AppliedDate"])

def stable_rng(text: str) -> np.random.Generator:
    seed = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
    return np.random.default_rng(seed)

stage_order = {
    "Applied": 1,
    "Screened": 2,
    "Interviewed": 3,
    "Offered": 4,
    "Hired": 5,
    "Rejected": 6,
}

rows = []

for _, r in df.iterrows():
    app_id = r["ApplicationID"]
    rng = stable_rng(app_id)

    final_stage = str(r["FinalStage"])
    days = max(int(r["DaysInPipeline"]), 1)

    if final_stage == "Hired":
        path = ["Applied", "Screened", "Interviewed", "Offered", "Hired"]
    elif final_stage == "Offered":
        path = ["Applied", "Screened", "Interviewed", "Offered"]
    elif final_stage == "Interviewed":
        path = ["Applied", "Screened", "Interviewed"]
    elif final_stage == "Screened":
        path = ["Applied", "Screened"]
    elif final_stage == "Applied":
        path = ["Applied"]
    else:
        reject_after = rng.choice(
            ["Applied", "Screened", "Interviewed", "Offered"],
            p=[0.35, 0.35, 0.22, 0.08],
        )

        if reject_after == "Applied":
            path = ["Applied", "Rejected"]
        elif reject_after == "Screened":
            path = ["Applied", "Screened", "Rejected"]
        elif reject_after == "Interviewed":
            path = ["Applied", "Screened", "Interviewed", "Rejected"]
        else:
            path = ["Applied", "Screened", "Interviewed", "Offered", "Rejected"]

    offsets = np.linspace(0, days, num=len(path)).round().astype(int)

    for stage, offset in zip(path, offsets):
        stage_date = r["AppliedDate"] + pd.Timedelta(days=int(offset))

        rows.append({
            "RequisitionID": r["RequisitionID"],
            "ApplicationID": app_id,
            "JobRoleID": r["JobRoleID"],
            "DepartmentID": r["DepartmentID"],
            "Stage": stage,
            "StageOrder": stage_order[stage],
            "StageDate": stage_date,
            "StageDateKey": int(stage_date.strftime("%Y%m")),
            "FinalStage": final_stage,
            "DaysInPipeline": int(r["DaysInPipeline"]),
        })

stage_df = pd.DataFrame(rows)
stage_df.to_parquet(out, index=False)

print(f"Created: {out}")
print(f"Rows: {len(stage_df):,}")
print()
print(stage_df["Stage"].value_counts().sort_index())
