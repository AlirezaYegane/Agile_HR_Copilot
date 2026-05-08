# Gap Log — Agile HR Copilot

Date: 2026-05-08  
Project path: `D:\Agile_HR_Copilot`

## Must-fix

These block a clean v1-polished release.

| ID | Gap | Area | Why it matters | Target day |
|---|---|---|---|---|
| M1 | Final Power BI page screenshots are missing. | Power BI / README | README and final project proof need clean screenshots for all 5 dashboard pages. | Day 2-3 |
| M2 | `powerbi/AgileHRCopilot.pbix` has uncommitted local changes. | Power BI / Git | Need to know whether current PBIX is the real final state or accidental local change. | Day 2 |
| M3 | Several Power BI helper files are untracked. | Power BI / Git | Useful files should either be committed or deliberately removed before release. | Day 2 |
| M4 | API narrative endpoint uses fallback because Gemini is unavailable. | Copilot / LLM | Demo works, but real LLM path should be checked before public demo. | Day 4 |
| M5 | Repo has many modified notebooks/scripts/docs. | Git hygiene | Need clean, reviewable commits before release tag. | Day 5 |

## Should-fix

These improve quality but do not block basic functionality.

| ID | Gap | Area | Why it matters | Target day |
|---|---|---|---|---|
| S1 | Streamlit UI was smoke-tested but not visually reviewed. | Copilot UI | App starts, but visual quality still needs product-level review. | Day 4 |
| S2 | Power BI report needs manual page-by-page structure review. | Power BI | Need to confirm every visual has correct fields, relationships, slicers, and business purpose. | Day 2 |
| S3 | Power BI cross-filter and navigation behavior not yet audited. | Power BI UX | Drill-through/buttons and filter behavior are part of professional dashboard delivery. | Day 3 |
| S4 | README should be checked against actual current screenshots and artefacts. | Documentation | README should not claim screenshots or features that are not present. | Day 5 |
| S5 | `verify_day4.py` passes despite missing Power BI screenshots. | QA scripts | This is acceptable for governance, but release readiness should include screenshot checks. | Day 5 |

## Nice-to-have

Only do these after must-fix and should-fix items are done.

| ID | Gap | Area | Why it matters | Target day |
|---|---|---|---|---|
| N1 | Add a cleaner Copilot hero screenshot after UI polish. | Documentation | Makes README more attractive. | Day 4-5 |
| N2 | Add a short demo question list for the Copilot. | Demo prep | Makes interview demo safer and repeatable. | Day 4 |
| N3 | Add a short “current limitations” section to README. | Governance | Shows honesty and senior judgement. | Day 5 |
| N4 | Add a release tag after cleanup. | GitHub release | Makes the polished baseline easy to reference. | Day 5 |

## Day 2 starting point

The first thing to do on Day 2 is to open `powerbi/AgileHRCopilot.pbix` and audit every page:

1. Confirm all five pages exist.
2. Confirm every visual has a real field binding.
3. Confirm titles, slicers, and page names are clear.
4. Confirm no blank placeholder visuals remain except a planned AI narrative panel.
5. Save rough screenshots for review.

## Day 1 conclusion

The project is functional and ahead of a basic baseline. The core data, ML, API, RAG, governance, and UI smoke tests pass. The main recovery focus is now Power BI completeness and presentation quality.
