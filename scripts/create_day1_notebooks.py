from pathlib import Path
import nbformat as nbf

NOTEBOOKS = Path("notebooks")
NOTEBOOKS.mkdir(exist_ok=True)

def write_nb(path, title, body):
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(f"# {title}\n\nThis notebook documents the Day 1 implementation for Agile HR Copilot."),
        nbf.v4.new_markdown_cell(body),
        nbf.v4.new_code_cell("from pathlib import Path\nimport pandas as pd\n\nprint('Project root ready')"),
    ]
    nbf.write(nb, path)

write_nb(
    NOTEBOOKS / "01_bronze_ingest.ipynb",
    "01 — Bronze Ingest",
    """Bronze layer ingests the raw IBM HR Attrition CSV, appends lineage metadata, and writes `lakehouse/bronze/employees_raw.parquet`.

Implemented reproducibly in `scripts/day1_build_lakehouse.py`."""
)

write_nb(
    NOTEBOOKS / "02_silver_transform.ipynb",
    "02 — Silver Transform",
    """Silver layer cleans the bronze table, anonymises employee numbers into stable `EmployeeID` values, adds age/salary/tenure bands, and writes `lakehouse/silver/employees.parquet`.

Implemented reproducibly in `scripts/day1_build_lakehouse.py`."""
)

write_nb(
    NOTEBOOKS / "03_gold_star_schema.ipynb",
    "03 — Gold Star Schema",
    """Gold layer builds the business-ready star schema: `dim_employee`, `dim_department`, `dim_jobrole`, `dim_date`, `fact_employee_snapshot`, `fact_recruitment`, and `fact_engagement_pulse`.

Implemented reproducibly in `scripts/day1_build_lakehouse.py`."""
)

print("Day 1 notebooks created.")
