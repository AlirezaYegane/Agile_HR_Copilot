# Microsoft Fabric Setup Notes — Agile HR Copilot

## Purpose

Day 6 starts the Fabric foundation phase of Agile HR Copilot.

The goal is not to replace the local project. The goal is to prove that the existing local medallion architecture can be mapped cleanly into Microsoft Fabric / OneLake while keeping the GitHub repo fully reproducible.

## Day 6 Outcome

By the end of Day 6, the project should have:

- A Microsoft Fabric workspace, if access is available
- A planned Lakehouse name
- A clear naming convention
- A local-to-Fabric mapping table
- Screenshots of the Fabric workspace and/or documented blocker
- Local verification still passing

## Access Status

| Item | Status | Notes |
|---|---|---|
| Microsoft Fabric access | Blocked | Access/trial not available yet; local project remains runnable |
| Workspace created | Blocked | Waiting for Fabric access |
| Lakehouse created | Blocked | Waiting for Fabric access |
| Local repo still runnable | Done | Local baseline remains reproducible |

If Fabric access is blocked, this is not a project failure. The blocker must be documented clearly and the local reproducible project remains the source of truth.

## Planned Fabric Workspace

| Setting | Value |
|---|---|
| Workspace name | Agile HR Copilot Dev |
| Workspace purpose | Fabric proof environment for Agile HR Copilot |
| Project source of truth | Local GitHub repo |
| Main local directory | `D:\Agile_HR_Copilot` |
| Target Fabric layer | Fabric Lakehouse + OneLake |
| Power BI target | Fabric-backed semantic model / DirectLake or Lakehouse SQL endpoint in later days |

## Planned Lakehouse

| Setting | Value |
|---|---|
| Lakehouse name | `agile_hr_lakehouse` |
| Storage pattern | OneLake Files + Delta Tables |
| Bronze location | `Files/bronze/` |
| Silver location | `Tables/silver_*` or `Tables/employees_silver` |
| Gold location | Delta tables in Lakehouse Tables area |
| Power BI connection target | Lakehouse SQL endpoint or DirectLake semantic model |

## Naming Convention

| Asset type | Naming pattern | Example |
|---|---|---|
| Workspace | Human readable project + environment | `Agile HR Copilot Dev` |
| Lakehouse | snake_case | `agile_hr_lakehouse` |
| Fabric notebooks | numbered pipeline stage | `01_bronze_ingest`, `02_silver_transform`, `03_gold_star_schema` |
| Bronze files | raw/source aligned | `employees_raw` |
| Silver tables | cleaned business entity | `employees_silver` |
| Gold dimensions | `dim_*` | `dim_employee`, `dim_department` |
| Gold facts | `fact_*` | `fact_employee_snapshot`, `fact_attrition_risk` |
| Screenshots | day + asset + short label | `day6_workspace_home.png` |

## Local-to-Fabric Mapping

| Local project layer | Local path | Fabric target | Notes |
|---|---|---|---|
| Raw HR CSV | `data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv` | `Files/bronze/raw/` | Raw source remains excluded from Git |
| Bronze Parquet | `lakehouse/bronze/employees_raw.parquet` | `Files/bronze/employees_raw/` | Day 7 port |
| Silver Parquet | `lakehouse/silver/employees.parquet` | `Tables/employees_silver` | Day 7 port, preferably Delta |
| Gold dimensions | `lakehouse/gold/dim_*.parquet` | Lakehouse Delta tables | Day 8 port |
| Gold facts | `lakehouse/gold/fact_*.parquet` | Lakehouse Delta tables | Day 8 port |
| Power BI local report | `powerbi/AgileHRCopilot.pbix` | Fabric-connected copy | Day 9 port |
| Local verification | `scripts/verify_day*.py` | Fabric validation notebooks | Local remains canonical |

## Local Gold Tables Expected

These are the tables that must eventually exist in Fabric as Delta tables:

- `dim_date`
- `dim_department`
- `dim_employee`
- `dim_jobrole`
- `fact_employee_snapshot`
- `fact_engagement_pulse`
- `fact_recruitment`
- `fact_attrition_risk`

## Day 6 Manual Fabric Steps

1. Open Microsoft Fabric in the browser.
2. Confirm that Fabric access or trial access is available.
3. Create a new workspace named `Agile HR Copilot Dev`.
4. Inside the workspace, create a Lakehouse named `agile_hr_lakehouse`.
5. Open the Lakehouse and confirm that Files and Tables areas are visible.
6. Capture screenshots and save them under `docs/fabric/screenshots/`.
7. Do not migrate data yet. Data migration starts on Day 7.

## Screenshot Checklist

Save screenshots with these names where possible:

| Screenshot | Target path |
|---|---|
| Fabric home or workspace list | `docs/fabric/screenshots/day6_fabric_home.png` |
| Workspace created | `docs/fabric/screenshots/day6_workspace_created.png` |
| Lakehouse created | `docs/fabric/screenshots/day6_lakehouse_created.png` |
| Lakehouse Files/Tables view | `docs/fabric/screenshots/day6_lakehouse_files_tables.png` |

## Blocker Log

Use this section if access is blocked.

| Date | Blocker | Evidence | Next action |
|---|---|---|---|
| 2026-05-16 | Fabric access/trial unavailable | Screenshot saved if possible | Retry with eligible account or continue local reproducible path |

## Day 6 Done Condition

Day 6 is done when one of these is true:

### Path A — Fabric access available

- Workspace exists
- Lakehouse exists
- Screenshots are saved
- `docs/fabric/setup.md` is updated
- Local verify scripts still pass

### Path B — Fabric access blocked

- Blocker is documented clearly
- Screenshot or note of access issue is saved
- Local project still runs
- Day 7 is paused until access returns, but the repo remains clean

## Why this matters

This step turns the project from a local-only analytics demo into a Microsoft-stack-aligned implementation path. The local repo remains reproducible, while Fabric becomes the enterprise deployment proof.

