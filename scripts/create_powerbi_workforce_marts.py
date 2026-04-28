from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

GOLD = Path("lakehouse/gold")

dim_date = pd.read_parquet(GOLD / "dim_date.parquet")
dim_dept = pd.read_parquet(GOLD / "dim_department.parquet")
dim_role = pd.read_parquet(GOLD / "dim_jobrole.parquet")
fact_snapshot = pd.read_parquet(GOLD / "fact_employee_snapshot.parquet")
fact_recruitment = pd.read_parquet(GOLD / "fact_recruitment.parquet")

# Keep one clean lookup shape.
role_lookup_full = dim_role[["JobRoleID", "JobRole", "JobLevel"]].drop_duplicates("JobRoleID")
role_lookup_name = dim_role[["JobRoleID", "JobRole"]].drop_duplicates("JobRoleID")
dept_lookup = dim_dept[["DepartmentID", "Department"]].drop_duplicates("DepartmentID")

# ------------------------------------------------------------
# 0) Create recruitment stage table if missing
# ------------------------------------------------------------
stage_path = GOLD / "fact_recruitment_stage.parquet"

def stable_rng(text: str) -> np.random.Generator:
    seed = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
    return np.random.default_rng(seed)

if not stage_path.exists():
    print("fact_recruitment_stage.parquet not found. Creating it...")

    df = fact_recruitment.copy()
    df["AppliedDate"] = pd.to_datetime(df["AppliedDate"])

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
        final_stage = str(r["FinalStage"])
        days = max(int(r["DaysInPipeline"]), 1)
        rng = stable_rng(app_id)

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

    fact_stage = pd.DataFrame(rows)
    fact_stage.to_parquet(stage_path, index=False)
else:
    fact_stage = pd.read_parquet(stage_path)

# ------------------------------------------------------------
# 1) Label recruitment and stage tables
# ------------------------------------------------------------
recruit_labeled = (
    fact_recruitment
    .merge(dept_lookup, on="DepartmentID", how="left")
    .merge(role_lookup_full, on="JobRoleID", how="left")
    .merge(
        dim_date[["DateKey", "Date", "Year", "Quarter", "Month", "MonthName"]],
        on="DateKey",
        how="left",
    )
)

stage_labeled = (
    fact_stage
    .merge(dept_lookup, on="DepartmentID", how="left")
    .merge(role_lookup_full, on="JobRoleID", how="left")
    .merge(
        dim_date[["DateKey", "Date", "Year", "Quarter", "Month", "MonthName"]],
        left_on="StageDateKey",
        right_on="DateKey",
        how="left",
        suffixes=("", "_DimDate"),
    )
)

# ------------------------------------------------------------
# 2) Mart: workforce KPI card table
# ------------------------------------------------------------
total_reqs = recruit_labeled["RequisitionID"].nunique()
total_apps = recruit_labeled["ApplicationID"].nunique()
total_hires = recruit_labeled.loc[
    recruit_labeled["FinalStage"] == "Hired",
    "ApplicationID",
].nunique()

hire_rate = total_hires / total_apps if total_apps else 0.0

avg_time_to_hire = recruit_labeled.loc[
    recruit_labeled["FinalStage"] == "Hired",
    "DaysInPipeline",
].mean()

offered_apps = stage_labeled.loc[
    stage_labeled["Stage"] == "Offered",
    "ApplicationID",
].nunique()

hired_apps = stage_labeled.loc[
    stage_labeled["Stage"] == "Hired",
    "ApplicationID",
].nunique()

offer_acceptance = hired_apps / offered_apps if offered_apps else 0.0

mart_kpis = pd.DataFrame([{
    "TotalRequisitions": int(total_reqs),
    "TotalApplications": int(total_apps),
    "TotalHires": int(total_hires),
    "HireRate": float(hire_rate),
    "AvgTimeToHire": float(avg_time_to_hire) if pd.notna(avg_time_to_hire) else 0.0,
    "OfferAcceptanceRate": float(offer_acceptance),
}])

mart_kpis.to_parquet(GOLD / "mart_workforce_kpis.parquet", index=False)

# ------------------------------------------------------------
# 3) Mart: recruitment funnel, excluding Rejected from main conversion funnel
# ------------------------------------------------------------
funnel_order = ["Applied", "Screened", "Interviewed", "Offered", "Hired"]

mart_funnel = (
    stage_labeled[stage_labeled["Stage"].isin(funnel_order)]
    .groupby(["Stage", "StageOrder"], as_index=False)
    .agg(FunnelApplications=("ApplicationID", "nunique"))
    .sort_values("StageOrder")
)

applied_count = mart_funnel.loc[
    mart_funnel["Stage"] == "Applied",
    "FunnelApplications",
].iloc[0]

mart_funnel["ConversionFromApplied"] = mart_funnel["FunnelApplications"] / applied_count
mart_funnel.to_parquet(GOLD / "mart_recruitment_funnel.parquet", index=False)

# ------------------------------------------------------------
# 4) Mart: monthly workforce metrics
# ------------------------------------------------------------
monthly_headcount = (
    fact_snapshot[fact_snapshot["IsActive"] == 1]
    .groupby("DateKey", as_index=False)
    .agg(Headcount=("EmployeeID", "nunique"))
)

monthly_recruitment = (
    recruit_labeled
    .groupby("DateKey", as_index=False)
    .agg(
        Applications=("ApplicationID", "nunique"),
        Hires=("ApplicationID", lambda s: s[recruit_labeled.loc[s.index, "FinalStage"] == "Hired"].nunique()),
        AvgTimeToHire=("DaysInPipeline", lambda s: s[recruit_labeled.loc[s.index, "FinalStage"] == "Hired"].mean()),
    )
)

mart_monthly = (
    dim_date[["DateKey", "Date", "Year", "Quarter", "Month", "MonthName"]]
    .merge(monthly_headcount, on="DateKey", how="left")
    .merge(monthly_recruitment, on="DateKey", how="left")
)

mart_monthly["Headcount"] = mart_monthly["Headcount"].fillna(0).astype(int)
mart_monthly["Applications"] = mart_monthly["Applications"].fillna(0).astype(int)
mart_monthly["Hires"] = mart_monthly["Hires"].fillna(0).astype(int)
mart_monthly["AvgTimeToHire"] = mart_monthly["AvgTimeToHire"].astype(float)

mart_monthly.to_parquet(GOLD / "mart_workforce_monthly.parquet", index=False)

# ------------------------------------------------------------
# 5) Mart: role-level inventory
# ------------------------------------------------------------
latest_datekey = fact_snapshot["DateKey"].max()

current_snapshot = fact_snapshot[
    (fact_snapshot["DateKey"] == latest_datekey)
    & (fact_snapshot["IsActive"] == 1)
].copy()

# Important:
# fact_snapshot already has JobLevel. We only bring JobRole name from dim_role.
# This avoids JobLevel_x / JobLevel_y and the KeyError you hit.
mart_role_inventory_base = (
    current_snapshot
    .merge(dept_lookup, on="DepartmentID", how="left")
    .merge(role_lookup_name, on="JobRoleID", how="left")
)

if "JobLevel" not in mart_role_inventory_base.columns:
    raise RuntimeError(
        "JobLevel is missing from role inventory base. "
        f"Columns available: {mart_role_inventory_base.columns.tolist()}"
    )

mart_role_inventory = (
    mart_role_inventory_base
    .groupby(["Department", "JobRole", "JobLevel"], as_index=False)
    .agg(CurrentHeadcount=("EmployeeID", "nunique"))
    .sort_values(["Department", "JobRole", "JobLevel"])
)

mart_role_inventory.to_parquet(GOLD / "mart_role_level_inventory.parquet", index=False)

# ------------------------------------------------------------
# 6) Mart: requisition detail
# ------------------------------------------------------------
mart_req_detail = (
    recruit_labeled
    .groupby(["RequisitionID", "Department", "JobRole", "JobLevel"], as_index=False)
    .agg(
        ApplicationCount=("ApplicationID", "nunique"),
        Hires=("ApplicationID", lambda s: s[recruit_labeled.loc[s.index, "FinalStage"] == "Hired"].nunique()),
        AvgDaysInPipeline=("DaysInPipeline", "mean"),
    )
)

mart_req_detail["HireRate"] = mart_req_detail["Hires"] / mart_req_detail["ApplicationCount"]
mart_req_detail = mart_req_detail.sort_values(["Department", "JobRole", "RequisitionID"])

mart_req_detail.to_parquet(GOLD / "mart_requisition_detail.parquet", index=False)

print("Power BI-safe workforce marts created:")
for p in [
    "mart_workforce_kpis.parquet",
    "mart_recruitment_funnel.parquet",
    "mart_workforce_monthly.parquet",
    "mart_role_level_inventory.parquet",
    "mart_requisition_detail.parquet",
]:
    path = GOLD / p
    print(f" - {p}: {len(pd.read_parquet(path)):,} rows")

print("\nRole inventory preview:")
print(pd.read_parquet(GOLD / "mart_role_level_inventory.parquet").head(10).to_string(index=False))

print("\nRequisition detail preview:")
print(pd.read_parquet(GOLD / "mart_requisition_detail.parquet").head(10).to_string(index=False))
