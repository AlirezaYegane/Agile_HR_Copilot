"""
Validate the Gold layer Parquet files against the Power BI semantic model contract.

Run this BEFORE opening Power BI Desktop. It catches missing files, missing
columns, and obviously bad row counts so you don't waste time inside Power BI.

Usage (from the repo root):

    python powerbi\validate_gold_for_powerbi.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLD = REPO_ROOT / "lakehouse" / "gold"


# Each entry: (filename, required columns, friendly Power BI table name, optional hard min row count)
EXPECTED: list[tuple[str, set[str], str, int]] = [
    (
        "dim_date.parquet",
        {"DateKey", "Date", "Year", "Quarter", "Month", "MonthName", "FYLabel"},
        "DimDate",
        12,
    ),
    (
        "dim_department.parquet",
        {"DepartmentID", "Department"},
        "DimDepartment",
        1,
    ),
    (
        "dim_jobrole.parquet",
        {"JobRoleID", "JobRole", "JobLevel", "DepartmentID"},
        "DimJobRole",
        1,
    ),
    (
        "dim_employee.parquet",
        {
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
        },
        "DimEmployee",
        1000,
    ),
    (
        "fact_employee_snapshot.parquet",
        {
            "EmployeeID",
            "DateKey",
            "IsActive",
            "AttritionThisMonth",
            "JobSatisfaction",
            "EnvSatisfaction",
            "WorkLifeBalance",
            "JobInvolvement",
            "PerformanceRating",
            "OvertimeFlag",
            "MonthlyIncome",
            "SalaryBand",
            "TenureYears",
            "TenureCohort",
            "YearsInRole",
            "YearsSincePromotion",
            "YearsWithManager",
            "JobLevel",
            "DepartmentID",
            "JobRoleID",
        },
        "FactEmployeeSnapshot",
        20000,
    ),
    (
        "fact_engagement_pulse.parquet",
        {"EmployeeID", "QuarterKey", "Quarter", "PulseScore", "ThemesFlagged"},
        "FactEngagementPulse",
        500,
    ),
    (
        "fact_recruitment.parquet",
        {
            "RequisitionID",
            "JobRoleID",
            "DepartmentID",
            "ApplicationID",
            "AppliedDate",
            "FinalStage",
            "DaysInPipeline",
            "DateKey",
        },
        "FactRecruitment",
        1000,
    ),
    (
        "fact_attrition_risk.parquet",
        {
            "EmployeeID",
            "RiskScore",
            "RiskBand",
            "TopDriver1",
            "TopDriver1Impact",
            "TopDriver2",
            "TopDriver2Impact",
            "TopDriver3",
            "TopDriver3Impact",
        },
        "FactAttritionRisk",
        1470,
    ),
]


def main() -> int:
    print(f"Validating gold layer at: {GOLD}\n")

    if not GOLD.exists():
        print(f"FAIL — gold directory not found: {GOLD}")
        print("Run scripts\\day1_build_lakehouse.py first.")
        return 1

    failures: list[str] = []

    for filename, required_cols, table, min_rows in EXPECTED:
        path = GOLD / filename
        print(f"[{table:<22}] {filename:<35}", end="")

        if not path.exists():
            print("MISSING")
            failures.append(f"{filename} is missing")
            continue

        try:
            df = pd.read_parquet(path)
        except Exception as e:
            print(f"UNREADABLE ({e})")
            failures.append(f"{filename} could not be read")
            continue

        missing = required_cols - set(df.columns)
        if missing:
            print("MISSING COLUMNS")
            failures.append(f"{filename} is missing columns: {sorted(missing)}")
            continue

        if len(df) < min_rows:
            print(f"LOW ROW COUNT ({len(df):,} < {min_rows:,})")
            failures.append(
                f"{filename} only has {len(df):,} rows — expected at least {min_rows:,}"
            )
            continue

        print(f"OK   ({len(df):>7,} rows · {len(df.columns):>2} cols)")

    print()

    if failures:
        print("VALIDATION FAILED:")
        for msg in failures:
            print(f"  - {msg}")
        return 1

    print("OK — all expected gold tables and columns are present.")
    print("Open powerbi/AgileHRCopilot.pbix and refresh.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
