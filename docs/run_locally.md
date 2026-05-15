# Run Locally

## 1. Activate environment

```powershell
cd D:\Agile_HR_Copilot
.\.venv\Scripts\Activate.ps1
```

## 2. Verify data and ML artefacts

```powershell
python scripts\verify_day1.py
python scripts\verify_day2.py
```

## 3. Start FastAPI

```powershell
uvicorn apps.api.app.main:app --port 8001
```

## 4. Smoke-test the API

Open a second PowerShell terminal:

```powershell
cd D:\Agile_HR_Copilot
.\.venv\Scripts\Activate.ps1
python scripts\smoke_day3_api.py
```

Expected result: `health`, `narrative`, `ask`, and `explain-risk` all return 200.

## 5. Start Streamlit

With FastAPI still running, in a third terminal:

```powershell
streamlit run apps\web\streamlit_app.py
```

The Copilot UI will open in your browser.

## 6. Verify governance artefacts

```powershell
python scripts\verify_day4.py
```

## 7. Validate the Gold layer for Power BI

Before opening Power BI Desktop:

```powershell
python powerbi\validate_gold_for_powerbi.py
```

Expected last line: `OK — all expected gold tables and columns are present.`

## 8. Open Power BI

Open:

```text
powerbi/AgileHRCopilot.pbix
```

Refresh after rebuilding the local lakehouse so the visuals reflect the latest Gold Parquet outputs. Build kit:

- `docs/powerbi_design.md` — visual spec
- `powerbi/AgileHRTheme.json` — load via *View → Themes → Browse for themes*
- `powerbi/dax_measures.md` — paste into a `_Measures` table
- `powerbi/power_query_import_guide.md` — relationships and types
- `powerbi/page_build_checklist.md` — execution checklist

## Notes on the AI fallback

- If `GOOGLE_API_KEY` is missing or invalid in `.env`, the Copilot still works. It will return a deterministic local narrative and grounded TF-IDF excerpts for Q&A.
- Audit logs are written to `apps/api/audit.log` and are git-ignored.
