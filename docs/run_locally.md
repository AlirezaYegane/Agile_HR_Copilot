# Run Locally

## 1. Activate environment

```powershell
cd D:\Agile_HR_Copilot
.\.venv\Scripts\Activate.ps1
2. Verify data and ML artefacts
python scripts\verify_day1.py
python scripts\verify_day2.py
3. Start FastAPI
uvicorn apps.api.app.main:app --port 8001
4. Smoke-test API

Open a second terminal:

cd D:\Agile_HR_Copilot
.\.venv\Scripts\Activate.ps1
python scripts\smoke_day3_api.py

Expected result: health, narrative, ask, and explain-risk all return 200.

5. Start Streamlit

With FastAPI still running:

streamlit run apps\web\streamlit_app.py
6. Open Power BI

Open:

powerbi/AgileHRCopilot.pbix

Refresh after rebuilding the local lakehouse.
