# Page Build Checklist — Agile HR Copilot Power BI

Use this checklist while you build, in order. Tick each item before moving to the next page. Detailed visual specs live in `docs/powerbi_design.md` — this file is only the executable checklist.

## 0 · Pre-flight

- [ ] Ran `python scripts/day1_build_lakehouse.py` (Parquet files exist in `lakehouse/gold/`)
- [ ] Ran `python scripts/day2_train_attrition_model.py` (`fact_attrition_risk.parquet` exists)
- [ ] Ran `python powerbi/validate_gold_for_powerbi.py` and it printed `OK`
- [ ] Imported all eight Parquet files per `power_query_import_guide.md`
- [ ] All required types set (Whole Number / Decimal / Date / Text)
- [ ] `DimDate` marked as date table on the `Date` column
- [ ] Created the nine relationships listed in `power_query_import_guide.md` §4
- [ ] Loaded `powerbi/AgileHRTheme.json` via View → Themes → Browse for themes
- [ ] Created `_Measures` table and pasted every measure from `powerbi/dax_measures.md`
- [ ] Page canvas size set to 1280 × 720 px (Type *Custom*) for every page

## Page 1 · Executive Overview

- [ ] Header band (navy) with title "Executive Overview"
- [ ] KPI strip: Headcount · Attrition Rate · High Risk Count · Engagement Index · Open Requisitions
- [ ] YoY delta on Attrition Rate (uses `Attrition Rate YoY (pp delta)`, sign-aware colour)
- [ ] Line chart: Headcount trend (DimDate[Date] × Headcount), navy
- [ ] Line chart: Attrition Rate trend with yellow reference line at 12%
- [ ] 100% stacked horizontal bar: High / Medium / Low risk band breakdown (red / yellow / green)
- [ ] AI Insight callout text (with bookmark button to Page 2)
- [ ] Slicers: Year, Department
- [ ] KPI cards do not cross-filter trend visuals
- [ ] Footer line: "Synthetic / public data only — decision support, not decisions"

## Page 2 · Attrition & Retention (the headline page)

- [ ] Header band navy with title "Attrition & Retention"
- [ ] KPI strip: Attrition Rate · YoY (pp delta) · High Risk Count · Average Risk Score
- [ ] Heatmap matrix: Department × TenureCohort, value = Attrition Rate, conditional formatting white → red
- [ ] Diverging bar: Top SHAP drivers (averaged from FactAttritionRisk) — positive red, negative green
- [ ] Top-25 high-risk employee table with: EmployeeID, Department, JobRole, TenureCohort, RiskScore (data bar red), RiskBand, TopDriver1/2/3
- [ ] Slicers: Year, Department, TenureCohort, RiskBand
- [ ] Heatmap cross-filters SHAP driver bar and high-risk table
- [ ] Tooltip page configured (mini risk-band breakdown)
- [ ] Page-level governance note bottom-left

## Page 3 · Employee Engagement

- [ ] Header band navy with title "Employee Engagement"
- [ ] KPI strip: Engagement Index · Response Rate · Pulses captured · % detractors
- [ ] Line chart: Engagement Index by quarter, yellow reference line at 70
- [ ] Bar chart: Themes flagged (using the Themes helper query)
- [ ] Bubble chart: Engagement Index (X) vs. Attrition Rate (Y), bubble size = Headcount, dot per Department
- [ ] Quadrant labels on the bubble chart
- [ ] Slicers: Quarter, Department, JobLevel

## Page 4 · Diversity & Inclusion (privacy-first)

- [ ] Header band navy with title "Diversity & Inclusion"
- [ ] KPI strip: Diversity Index · Gender mix · Median pay gap · Promotion gap
- [ ] 100% stacked bar: Gender × Job Level (use `Headcount (k-safe)` so cohorts < 25 disappear)
- [ ] Heatmap matrix: AgeBand × Department, value suppressed to "–" when n < 25
- [ ] Disparate-impact bar (loaded from `docs/fairness_audit_summary.csv` as a separate query)
- [ ] Reference lines on the disparate-impact bar at 0.8 and 1.25
- [ ] **Mandatory privacy callout box** on the page bottom: "Privacy guard — cohorts smaller than n = 25 are suppressed. Group-level metrics are diagnostic only."
- [ ] Slicers: Year, Department, Job Level

## Page 5 · Workforce Planning

- [ ] Header band navy with title "Workforce Planning"
- [ ] KPI strip: Open Requisitions · Hires · Avg Time to Hire · Offer Acceptance Rate
- [ ] Line chart: 12-month headcount trend
- [ ] Funnel visual: Applied → Screened → Interviewed → Offered → Hired
- [ ] Bar chart: Avg Time to Hire by Department, yellow reference line at company average
- [ ] Slicers: Year, Department, JobRole

## Polish pass (do this AFTER every page is built)

- [ ] All pages 1280 × 720 px
- [ ] No visual title is in ALL CAPS
- [ ] No 3D, no pies, no gauges
- [ ] No colour outside the eight in `AgileHRTheme.json`
- [ ] Red used only for risk / increases in attrition
- [ ] Green used only for retention wins / decreases in attrition
- [ ] Every visual has a sensible title (sentence case)
- [ ] Every page has the footer governance line
- [ ] Page navigator at the bottom of every page

## Export screenshots

For each page, after polish:

- [ ] *File → Export → PowerPoint* OR *Print Screen* the canvas
- [ ] Crop to canvas in any image editor
- [ ] Save as PNG at the exact filenames below into `D:\Agile_HR_Copilot\docs\images\`

| Page | Filename |
|---|---|
| 1 | `page1_executive.png` |
| 2 | `page2_attrition.png` |
| 3 | `page3_engagement.png` |
| 4 | `page4_diversity.png` |
| 5 | `page5_workforce.png` |

## Final verify

- [ ] `python scripts/verify_day4.py` reports `DAY 4 VERIFY PASSED` and lists all 5 Power BI screenshots as present
- [ ] Saved `powerbi/AgileHRCopilot.pbix`
