from pathlib import Path
import pandas as pd
import duckdb

required = [
    "lakehouse/bronze/employees_raw.parquet",
    "lakehouse/silver/employees.parquet",
    "lakehouse/gold/dim_employee.parquet",
    "lakehouse/gold/dim_department.parquet",
    "lakehouse/gold/dim_jobrole.parquet",
    "lakehouse/gold/dim_date.parquet",
    "lakehouse/gold/fact_employee_snapshot.parquet",
    "lakehouse/gold/fact_recruitment.parquet",
    "lakehouse/gold/fact_engagement_pulse.parquet",
    "data/policies/retention_career_growth.pdf",
    "data/policies/compensation_pay_equity.pdf",
    "data/policies/diversity_inclusion_wellbeing.pdf",
    "docs/product_alignment.md",
]

missing = [p for p in required if not Path(p).exists()]
if missing:
    print("Missing files:")
    for p in missing:
        print(" -", p)
    raise SystemExit(1)

bronze_rows = len(pd.read_parquet("lakehouse/bronze/employees_raw.parquet"))
silver_rows = len(pd.read_parquet("lakehouse/silver/employees.parquet"))

snapshot_rows = duckdb.sql(
    "SELECT COUNT(*) FROM 'lakehouse/gold/fact_employee_snapshot.parquet'"
).fetchone()[0]

print("DAY 1 VERIFY PASSED")
print(f"bronze rows: {bronze_rows:,}")
print(f"silver rows: {silver_rows:,}")
print(f"snapshot rows: {snapshot_rows:,}")
print("gold files:")
for p in sorted(Path("lakehouse/gold").glob("*.parquet")):
    print(" -", p.name)
