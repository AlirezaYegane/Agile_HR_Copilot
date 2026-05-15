"""
Regenerate the Day 1 notebooks (01 / 02 / 03) from the polished source-of-truth content.

The notebooks are also tracked in the repo, so this script is only needed if they
get out of sync or you want to regenerate them after editing the content below.
"""
from pathlib import Path

import nbformat as nbf

NOTEBOOKS = Path("notebooks")
NOTEBOOKS.mkdir(exist_ok=True)


def _md(text: str):
    return nbf.v4.new_markdown_cell(text)


def _code(text: str):
    return nbf.v4.new_code_cell(text)


def write_nb(path: Path, cells: list) -> None:
    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nbf.write(nb, path)


# ---- 01 — Bronze Ingest --------------------------------------------------
write_nb(
    NOTEBOOKS / "01_bronze_ingest.ipynb",
    [
        _md(
            "# 01 — Bronze Ingest\n\n"
            "**Layer:** Bronze · **Day:** 1 · "
            "**Authoritative script:** `scripts/day1_build_lakehouse.py` (function `build_bronze`)\n\n"
            "## Objective\n\n"
            "Ingest the public IBM HR Attrition CSV into a Parquet bronze table with provenance metadata so "
            "downstream layers always have a reproducible, queryable starting point.\n\n"
            "## Inputs\n\n"
            "- `data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv` — public IBM HR dataset (1,470 rows)\n\n"
            "## Outputs\n\n"
            "- `lakehouse/bronze/employees_raw.parquet`\n"
            "  - All raw columns preserved\n"
            "  - Adds `_ingest_ts` (UTC ISO timestamp)\n"
            "  - Adds `_source` (lineage tag `ibm_hr_attrition_kaggle_v1`)\n"
            "  - Adds `_row_hash` (12-char MD5 over the row, for change detection)\n\n"
            "## Business value\n\n"
            "Bronze freezes the source contract. If anyone asks *\"what did the data look like on day X?\"* — bronze is the answer. "
            "Lineage columns make audit and debugging cheap and stop downstream code from silently re-shaping the source."
        ),
        _md(
            "## Reproduce\n\n"
            "```powershell\n"
            "cd D:\\Agile_HR_Copilot\n"
            ".\\.venv\\Scripts\\Activate.ps1\n"
            "python scripts\\day1_build_lakehouse.py\n"
            "```"
        ),
        _code(
            "from pathlib import Path\n"
            "import pandas as pd\n\n"
            "BRONZE = Path('../lakehouse/bronze/employees_raw.parquet')\n"
            "print('exists:', BRONZE.exists())"
        ),
        _code(
            "if BRONZE.exists():\n"
            "    df = pd.read_parquet(BRONZE)\n"
            "    print(f'rows: {len(df):,}  cols: {df.shape[1]}')\n"
            "    print('lineage columns:', [c for c in df.columns if c.startswith(\"_\")])\n"
            "    df.head(3)"
        ),
        _md(
            "## Interview talking points\n\n"
            "- Bronze is intentionally **dumb** — no cleaning, no business logic. That is why downstream issues can always be traced.\n"
            "- The `_row_hash` is a cheap idempotency check: re-running the script produces the same hashes, so a CI pipeline can detect upstream drift.\n"
            "- In Microsoft Fabric this would be a Delta table in OneLake; the columns and contract are unchanged."
        ),
    ],
)

# ---- 02 — Silver Transform -----------------------------------------------
write_nb(
    NOTEBOOKS / "02_silver_transform.ipynb",
    [
        _md(
            "# 02 — Silver Transform\n\n"
            "**Layer:** Silver · **Day:** 1 · "
            "**Authoritative script:** `scripts/day1_build_lakehouse.py` (function `build_silver`)\n\n"
            "## Objective\n\n"
            "Turn the bronze raw table into a cleaned, typed, and anonymised employee table that is safe to use for analytics and model training.\n\n"
            "## Inputs\n\n"
            "- `lakehouse/bronze/employees_raw.parquet`\n\n"
            "## Outputs\n\n"
            "- `lakehouse/silver/employees.parquet`\n"
            "  - **Anonymised `EmployeeID`** — SHA-256 of `EmployeeNumber` salted with the project key, truncated to 10 chars (`EMP_3F9A21BC74`).\n"
            "  - **Bucketed demographics**: `AgeBand`, `SalaryBand`, `TenureCohort`.\n"
            "  - **Renames**: `EnvSatisfaction`, `LastRaisePct`, `TotalExperienceYears`, `TenureYears`, `YearsInRole`, `YearsSincePromotion`, `YearsWithManager`, etc.\n"
            "  - **Dropped constants**: `EmployeeCount`, `Over18`, `StandardHours`.\n"
            "  - **`AttritionFlag`** (0/1 target derived from the Yes/No `Attrition` column).\n\n"
            "## Business value\n\n"
            "Silver is the layer everyone (analytics, Power BI, ML) actually consumes. Cleaning is done **once** and the contract is documented, "
            "so the model and the dashboards are always looking at the same world."
        ),
        _md("## Reproduce\n\n```powershell\npython scripts\\day1_build_lakehouse.py\n```"),
        _code(
            "from pathlib import Path\n"
            "import pandas as pd\n\n"
            "SILVER = Path('../lakehouse/silver/employees.parquet')\n"
            "print('exists:', SILVER.exists())"
        ),
        _code(
            "if SILVER.exists():\n"
            "    df = pd.read_parquet(SILVER)\n"
            "    print(f'rows: {len(df):,}  cols: {df.shape[1]}')\n"
            "    print('attrition rate:', round(df[\"AttritionFlag\"].mean(), 3))\n"
            "    df[['EmployeeID','AgeBand','SalaryBand','TenureCohort','AttritionFlag']].head(5)"
        ),
        _md(
            "## Privacy notes\n\n"
            "- `EmployeeID` is a stable but **non-reversible** label. The salt lives in code so the mapping cannot be reproduced from the parquet alone.\n"
            "- Bucketed fields make group-level reporting safer.\n"
            "- Power BI dashboards layer a k-anonymity threshold on top (cohorts < 25 are suppressed)."
        ),
        _md(
            "## Interview talking points\n\n"
            "- Silver-vs-bronze separation lets us replay the cleaning step independently of ingest.\n"
            "- The dropped constants are a small but real example of *governance through data shape* — they cannot be misused if they don't exist downstream.\n"
            "- All renames are conservative (semantic, not behavioural)."
        ),
    ],
)

# ---- 03 — Gold Star Schema -----------------------------------------------
write_nb(
    NOTEBOOKS / "03_gold_star_schema.ipynb",
    [
        _md(
            "# 03 — Gold Star Schema\n\n"
            "**Layer:** Gold · **Day:** 1 · "
            "**Authoritative script:** `scripts/day1_build_lakehouse.py` (function `build_gold`)\n\n"
            "## Objective\n\n"
            "Turn the silver employee table into a **star schema** that the Power BI semantic model and the FastAPI Copilot can both consume. "
            "Gold is the contract presented to consumers — once they integrate against it, the upstream layers can change without breaking them.\n\n"
            "## Outputs (under `lakehouse/gold/`)\n\n"
            "**Dimensions** — `dim_date`, `dim_department`, `dim_jobrole`, `dim_employee`.\n\n"
            "**Facts** — `fact_employee_snapshot` (employee × month), `fact_recruitment` (per application), "
            "`fact_engagement_pulse` (employee × quarter), and `fact_attrition_risk` (per employee, written by Day 2).\n\n"
            "## Business value\n\n"
            "A star schema is the right shape for both Power BI and ad-hoc SQL via DuckDB. Synthetic monthly snapshots are what make the time-series story possible — "
            "without them, a single static IBM dataset cannot answer \"how did attrition trend by quarter?\""
        ),
        _md("## Reproduce\n\n```powershell\npython scripts\\day1_build_lakehouse.py\n```"),
        _code(
            "from pathlib import Path\n"
            "import pandas as pd\n\n"
            "GOLD = Path('../lakehouse/gold')\n"
            "files = sorted(GOLD.glob('*.parquet')) if GOLD.exists() else []\n"
            "for f in files:\n"
            "    print(f'{f.name:<35}  {len(pd.read_parquet(f)):>7,} rows')"
        ),
        _code(
            "if (GOLD / 'fact_employee_snapshot.parquet').exists():\n"
            "    snap = pd.read_parquet(GOLD / 'fact_employee_snapshot.parquet')\n"
            "    print('rows:', len(snap))\n"
            "    print('unique employees:', snap['EmployeeID'].nunique())\n"
            "    print('months:', snap['DateKey'].nunique())\n"
            "    print(snap.groupby('DateKey')['IsActive'].mean().round(3).head())"
        ),
        _md(
            "## Power BI relationships\n\n"
            "Full list in `powerbi/power_query_import_guide.md` §4. Headline ones:\n\n"
            "- `FactEmployeeSnapshot[EmployeeID]` → `DimEmployee[EmployeeID]`\n"
            "- `FactEmployeeSnapshot[DateKey]` → `DimDate[DateKey]`\n"
            "- `FactEmployeeSnapshot[DepartmentID]` → `DimDepartment[DepartmentID]`\n"
            "- `FactEmployeeSnapshot[JobRoleID]` → `DimJobRole[JobRoleID]`\n"
            "- `FactAttritionRisk[EmployeeID]` → `DimEmployee[EmployeeID]`"
        ),
        _md(
            "## Interview talking points\n\n"
            "- The risk fact is written **into** Gold by the ML pipeline. That keeps the model output reusable and avoids tight coupling between the model and the dashboard.\n"
            "- A star schema is what makes incremental moves to Fabric/OneLake painless.\n"
            "- Synthetic snapshots are flagged honestly in the model card."
        ),
    ],
)

print("Day 1 notebooks regenerated.")
