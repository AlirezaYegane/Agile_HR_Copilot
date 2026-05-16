# Fabric Assets

This folder tracks Microsoft Fabric implementation artefacts for Agile HR Copilot.

The local project remains the source of truth. Fabric is used as the enterprise deployment proof.

## Planned Fabric Layers

| Day | Fabric output |
|---|---|
| Day 6 | Workspace and Lakehouse setup documentation |
| Day 7 | Bronze and Silver port to Fabric Lakehouse |
| Day 8 | Gold star schema as Fabric Delta tables |
| Day 9 | Power BI connected to Fabric |
| Day 10 | Fabric foundation proof package |

## Planned Notebook Files

| Notebook | Purpose |
|---|---|
| `01_bronze_ingest.ipynb` | Load raw/bronze data into OneLake |
| `02_silver_transform.ipynb` | Clean and anonymise employee data |
| `03_gold_star_schema.ipynb` | Build gold facts and dimensions |
| `04_validate_fabric_counts.ipynb` | Compare Fabric row counts with local outputs |

## Rule

Do not make the project dependent on Fabric-only assets. Reviewers must still be able to run the local repo without Fabric access.
