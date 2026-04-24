import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


RAW_PATH = Path("data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv")
BRONZE_DIR = Path("lakehouse/bronze")
SILVER_DIR = Path("lakehouse/silver")
GOLD_DIR = Path("lakehouse/gold")

BRONZE_DIR.mkdir(parents=True, exist_ok=True)
SILVER_DIR.mkdir(parents=True, exist_ok=True)
GOLD_DIR.mkdir(parents=True, exist_ok=True)


def age_band(age: int) -> str:
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 55:
        return "45-54"
    return "55+"


def salary_band(income: int) -> str:
    if income < 3000:
        return "Band 1 (<3k)"
    if income < 6000:
        return "Band 2 (3-6k)"
    if income < 10000:
        return "Band 3 (6-10k)"
    if income < 15000:
        return "Band 4 (10-15k)"
    return "Band 5 (15k+)"


def tenure_cohort(years: int) -> str:
    if years < 1:
        return "0-1y (new)"
    if years < 3:
        return "1-3y"
    if years < 5:
        return "3-5y"
    if years < 10:
        return "5-10y"
    return "10y+"


def build_bronze() -> pd.DataFrame:
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Missing dataset: {RAW_PATH}. Put the Kaggle CSV there before running this script."
        )

    df_raw = pd.read_csv(RAW_PATH)
    ingest_ts = datetime.utcnow().isoformat()
    source_tag = "ibm_hr_attrition_kaggle_v1"

    df_bronze = df_raw.copy()
    df_bronze["_ingest_ts"] = ingest_ts
    df_bronze["_source"] = source_tag
    df_bronze["_row_hash"] = (
        df_raw.astype(str)
        .agg("|".join, axis=1)
        .apply(lambda s: hashlib.md5(s.encode()).hexdigest()[:12])
    )

    out = BRONZE_DIR / "employees_raw.parquet"
    df_bronze.to_parquet(out, engine="pyarrow", compression="snappy", index=False)

    print("BRONZE")
    print(f"  wrote: {out}")
    print(f"  rows: {len(df_bronze):,}")
    print(f"  cols: {df_bronze.shape[1]:,}")
    print(f"  attrition distribution:\n{df_bronze['Attrition'].value_counts(normalize=True).round(3)}")

    return df_bronze


def build_silver() -> pd.DataFrame:
    bronze_path = BRONZE_DIR / "employees_raw.parquet"
    df = pd.read_parquet(bronze_path)

    silver = df.copy()

    salt = "agile-hr-copilot-2026"
    silver["EmployeeID"] = silver["EmployeeNumber"].astype(str).apply(
        lambda x: "EMP_" + hashlib.sha256((salt + x).encode()).hexdigest()[:10].upper()
    )
    silver = silver.drop(columns=["EmployeeNumber"])

    silver["AgeBand"] = silver["Age"].apply(age_band)
    silver["SalaryBand"] = silver["MonthlyIncome"].apply(salary_band)
    silver["TenureCohort"] = silver["YearsAtCompany"].apply(tenure_cohort)
    silver["AttritionFlag"] = (silver["Attrition"] == "Yes").astype(int)

    silver = silver.rename(
        columns={
            "EnvironmentSatisfaction": "EnvSatisfaction",
            "NumCompaniesWorked": "PriorCompanies",
            "PercentSalaryHike": "LastRaisePct",
            "RelationshipSatisfaction": "RelationSatisfaction",
            "TotalWorkingYears": "TotalExperienceYears",
            "TrainingTimesLastYear": "TrainingCount",
            "YearsAtCompany": "TenureYears",
            "YearsInCurrentRole": "YearsInRole",
            "YearsSinceLastPromotion": "YearsSincePromotion",
            "YearsWithCurrManager": "YearsWithManager",
        }
    )

    drop_cols = [c for c in ["EmployeeCount", "Over18", "StandardHours"] if c in silver.columns]
    silver = silver.drop(columns=drop_cols)

    out = SILVER_DIR / "employees.parquet"
    silver.to_parquet(out, engine="pyarrow", compression="snappy", index=False)

    print("\nSILVER")
    print(f"  wrote: {out}")
    print(f"  rows: {len(silver):,}")
    print(f"  cols: {silver.shape[1]:,}")
    print(f"  dropped constants: {drop_cols}")

    return silver


def build_gold() -> None:
    df = pd.read_parquet(SILVER_DIR / "employees.parquet")
    rng = np.random.default_rng(42)
    fake = Faker()

    dim_employee = df[
        [
            "EmployeeID",
            "Gender",
            "AgeBand",
            "MaritalStatus",
            "Education",
            "EducationField",
            "DistanceFromHome",
            "BusinessTravel",
            "TotalExperienceYears",
            "PriorCompanies",
        ]
    ].drop_duplicates("EmployeeID").reset_index(drop=True)

    dim_department = (
        df[["Department"]]
        .drop_duplicates()
        .assign(DepartmentID=lambda d: ["DEPT_" + str(i + 1).zfill(2) for i in range(len(d))])
        [["DepartmentID", "Department"]]
        .reset_index(drop=True)
    )

    dim_jobrole = (
        df[["JobRole", "Department", "JobLevel"]]
        .drop_duplicates()
        .merge(dim_department, on="Department")
        .assign(JobRoleID=lambda d: ["ROLE_" + str(i + 1).zfill(3) for i in range(len(d))])
        [["JobRoleID", "JobRole", "JobLevel", "DepartmentID"]]
        .reset_index(drop=True)
    )

    today = datetime(2026, 4, 1)
    dates = pd.date_range(end=today, periods=24, freq="MS")

    dim_date = pd.DataFrame(
        {
            "DateKey": dates.strftime("%Y%m").astype(int),
            "Date": dates,
            "Year": dates.year,
            "Quarter": dates.quarter,
            "Month": dates.month,
            "MonthName": dates.strftime("%b"),
            "FYLabel": dates.strftime("%Y"),
        }
    )

    dim_employee.to_parquet(GOLD_DIR / "dim_employee.parquet", index=False)
    dim_department.to_parquet(GOLD_DIR / "dim_department.parquet", index=False)
    dim_jobrole.to_parquet(GOLD_DIR / "dim_jobrole.parquet", index=False)
    dim_date.to_parquet(GOLD_DIR / "dim_date.parquet", index=False)

    snapshots = []
    for _, emp in df.iterrows():
        attrition_month_idx = rng.integers(0, 24) if emp["AttritionFlag"] == 1 else None

        for i, d in enumerate(dates):
            if attrition_month_idx is not None and i > attrition_month_idx:
                break

            snapshots.append(
                {
                    "EmployeeID": emp["EmployeeID"],
                    "DateKey": int(d.strftime("%Y%m")),
                    "IsActive": 1 if (attrition_month_idx is None or i < attrition_month_idx) else 0,
                    "AttritionThisMonth": 1 if (attrition_month_idx is not None and i == attrition_month_idx) else 0,
                    "JobSatisfaction": int(np.clip(emp["JobSatisfaction"] + rng.normal(0, 0.25), 1, 4)),
                    "EnvSatisfaction": int(np.clip(emp["EnvSatisfaction"] + rng.normal(0, 0.25), 1, 4)),
                    "WorkLifeBalance": int(np.clip(emp["WorkLifeBalance"] + rng.normal(0, 0.2), 1, 4)),
                    "JobInvolvement": int(emp["JobInvolvement"]),
                    "PerformanceRating": int(emp["PerformanceRating"]),
                    "OvertimeFlag": 1 if emp["OverTime"] == "Yes" else 0,
                    "MonthlyIncome": int(emp["MonthlyIncome"] * (1 + 0.003 * i)),
                    "SalaryBand": emp["SalaryBand"],
                    "TenureYears": float(emp["TenureYears"] + (i / 12)),
                    "TenureCohort": emp["TenureCohort"],
                    "YearsInRole": float(emp["YearsInRole"] + (i / 12)),
                    "YearsSincePromotion": float(emp["YearsSincePromotion"] + (i / 12)),
                    "YearsWithManager": float(emp["YearsWithManager"] + (i / 12)),
                    "Department": emp["Department"],
                    "JobRole": emp["JobRole"],
                    "JobLevel": int(emp["JobLevel"]),
                }
            )

    fact_snapshot = pd.DataFrame(snapshots)
    fact_snapshot = (
        fact_snapshot.merge(dim_department, on="Department")
        .merge(dim_jobrole[["JobRoleID", "JobRole", "JobLevel", "DepartmentID"]], on=["JobRole", "JobLevel", "DepartmentID"])
        .drop(columns=["Department", "JobRole"])
    )
    fact_snapshot.to_parquet(GOLD_DIR / "fact_employee_snapshot.parquet", index=False)

    funnel = []
    n_reqs = 120

    for req_i in range(n_reqs):
        req_id = f"REQ_{req_i + 1:04d}"
        role = dim_jobrole.sample(1, random_state=req_i).iloc[0]
        n_apps = int(rng.integers(15, 80))
        open_date = dates[rng.integers(0, 20)]

        for app_i in range(n_apps):
            applied = open_date + timedelta(days=int(rng.integers(0, 30)))
            stage_path = ["Applied"]

            if rng.random() < 0.55:
                stage_path.append("Screened")
            if "Screened" in stage_path and rng.random() < 0.45:
                stage_path.append("Interviewed")
            if "Interviewed" in stage_path and rng.random() < 0.30:
                stage_path.append("Offered")
            if "Offered" in stage_path and rng.random() < 0.70:
                stage_path.append("Hired")
            if "Hired" not in stage_path:
                stage_path.append("Rejected")

            final_stage = stage_path[-1]

            funnel.append(
                {
                    "RequisitionID": req_id,
                    "JobRoleID": role["JobRoleID"],
                    "DepartmentID": role["DepartmentID"],
                    "ApplicationID": f"APP_{req_i:04d}_{app_i:03d}",
                    "AppliedDate": applied,
                    "FinalStage": final_stage,
                    "DaysInPipeline": int(
                        (final_stage == "Hired") * rng.integers(20, 70)
                        + (final_stage != "Hired") * rng.integers(5, 35)
                    ),
                    "DateKey": int(applied.strftime("%Y%m")),
                }
            )

    fact_recruitment = pd.DataFrame(funnel)
    fact_recruitment.to_parquet(GOLD_DIR / "fact_recruitment.parquet", index=False)

    themes = ["workload", "manager_trust", "career_growth", "compensation", "culture"]
    pulse_rows = []
    active_emps = dim_employee["EmployeeID"].tolist()
    quarters = pd.date_range(end=today, periods=8, freq="QS")

    for q in quarters:
        responders = rng.choice(active_emps, size=int(len(active_emps) * 0.6), replace=False)
        for eid in responders:
            score_base = int(rng.integers(2, 6))
            themes_flagged = rng.choice(themes, size=int(rng.integers(0, 3)), replace=False)
            pulse_rows.append(
                {
                    "EmployeeID": eid,
                    "QuarterKey": int(q.strftime("%Y%m")),
                    "Quarter": q,
                    "PulseScore": score_base,
                    "ThemesFlagged": ",".join(themes_flagged) if len(themes_flagged) else None,
                }
            )

    fact_pulse = pd.DataFrame(pulse_rows)
    fact_pulse.to_parquet(GOLD_DIR / "fact_engagement_pulse.parquet", index=False)

    print("\nGOLD")
    print(f"  dim_employee rows: {len(dim_employee):,}")
    print(f"  dim_department rows: {len(dim_department):,}")
    print(f"  dim_jobrole rows: {len(dim_jobrole):,}")
    print(f"  dim_date rows: {len(dim_date):,}")
    print(f"  fact_employee_snapshot rows: {len(fact_snapshot):,}")
    print(f"  fact_recruitment rows: {len(fact_recruitment):,}")
    print(f"  fact_engagement_pulse rows: {len(fact_pulse):,}")


def main() -> None:
    build_bronze()
    build_silver()
    build_gold()
    print("\nDay 1 lakehouse build complete.")


if __name__ == "__main__":
    main()


