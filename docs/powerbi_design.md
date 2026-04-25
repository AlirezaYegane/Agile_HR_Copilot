# Power BI Design Blueprint — Agile HR Copilot

This document is a build guide for the five-page CHRO report. It is the **source of truth** for visual style. Build it by hand in Power BI Desktop, save as `powerbi/AgileHRCopilot.pbix`, then export each page to PNG into `docs/images/`.

## Global visual standards

| Element | Spec |
|---|---|
| Page canvas | 1280 × 720 px, Type *Custom* |
| Background | `#FFFFFF` page · cards on `#F7F9FC` blocks |
| Page header band | Navy `#1F3A5F`, 64 px tall, white text, app title left, page title centre |
| Accent | Yellow `#F0B429` (selected state, KPI deltas, callouts only) |
| Risk red | `#D93025` — **only** for attrition / risk increases |
| Good green | `#2E7D32` — only for retention wins / positive movement |
| Neutral grey | `#546E7A` |
| Font | Segoe UI · Title 22 · KPI value 26 bold · KPI label 11 caps · Body 11 |
| KPI card | White fill, rounded 12 px corner, 1 px `#E5EAF2` border, 14 px padding |
| Visual title | Sentence case, navy, 14 pt, no all-caps |
| Gridlines | Light grey `#EEF1F6`, no axis lines |
| Data labels | Off by default; on for KPI cards and column tops only |
| Tooltips | Custom report-page tooltips on Pages 2 and 4 |
| Slicer style | Tile / horizontal where possible, navy selected, white unselected |
| Page navigation | Bottom strip · 5 buttons · selected state = navy fill, yellow underline |

### Forbidden

- Rainbow palettes
- 3D charts
- Pie charts (use 100% stacked bar for share)
- Gauges (use KPI card with sub-text)
- More than two colours in any single chart unless it is a categorical breakdown

### Privacy / governance overlay

Every page footer contains, in 9 pt grey:

> Synthetic / public data only. Risk scores are decision support — not decisions. Demographic visuals enforce a k-anonymity threshold of n ≥ 25.

## Shared measures (DAX)

Place these in a `[Measures]` table.

```DAX
Headcount = CALCULATE(DISTINCTCOUNT(FactEmployeeSnapshot[EmployeeID]), FactEmployeeSnapshot[IsActive] = 1)
Avg Headcount = AVERAGEX(VALUES(DimDate[DateKey]), [Headcount])

Attritions = CALCULATE(SUM(FactEmployeeSnapshot[AttritionThisMonth]))
Attrition Rate = DIVIDE([Attritions], [Avg Headcount])
Attrition Rate YoY = [Attrition Rate] - CALCULATE([Attrition Rate], SAMEPERIODLASTYEAR(DimDate[Date]))

High Risk Count = CALCULATE(COUNTROWS(FactAttritionRisk), FactAttritionRisk[RiskBand] = "High")
Medium Risk Count = CALCULATE(COUNTROWS(FactAttritionRisk), FactAttritionRisk[RiskBand] = "Medium")
Low Risk Count = CALCULATE(COUNTROWS(FactAttritionRisk), FactAttritionRisk[RiskBand] = "Low")
Avg Risk Score = AVERAGE(FactAttritionRisk[RiskScore])

Estimated Cost of Attrition = [Attritions] * 75000   -- placeholder loaded cost; document this assumption

Engagement Index = AVERAGEX(FactEngagementPulse, FactEngagementPulse[PulseScore]) * 20  -- 1-5 → 0-100
Response Rate = DIVIDE(DISTINCTCOUNT(FactEngagementPulse[EmployeeID]), [Headcount])

Hire Rate = DIVIDE(CALCULATE(COUNTROWS(FactRecruitment), FactRecruitment[FinalStage]="Hired"), [Avg Headcount])
Offer Acceptance = DIVIDE(
    CALCULATE(COUNTROWS(FactRecruitment), FactRecruitment[FinalStage]="Hired"),
    CALCULATE(COUNTROWS(FactRecruitment), FactRecruitment[FinalStage] IN {"Offered","Hired"})
)
Avg Time to Hire = AVERAGEX(FILTER(FactRecruitment, FactRecruitment[FinalStage]="Hired"), FactRecruitment[DaysInPipeline])

Diversity Index = 1 - SUMX(
    SUMMARIZE(DimEmployee, DimEmployee[Gender], "p", DIVIDE(COUNTROWS(DimEmployee), CALCULATE(COUNTROWS(DimEmployee), ALL(DimEmployee[Gender])))),
    [p]^2
)

-- k-anonymity guard: only display a demographic measure if the cohort has ≥ 25 members
K-Safe Headcount =
VAR n = [Headcount]
RETURN IF(n >= 25, n, BLANK())
```

---

## Page 1 — Executive Overview

**Story:** "How is our workforce doing this period, and where do leaders need to act?"

### Layout (12-col grid, 8 rows)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HEADER BAND   |   Agile HR Copilot · Executive Overview            [Q] │
├──────────────────────────────────────────────────────────────────────────┤
│  KPI 1 │ KPI 2 │ KPI 3 │ KPI 4 │ KPI 5                                   │
├──────────────────────────────────────────────────────────────────────────┤
│  Headcount trend (line)        │  Attrition rate trend (line + YoY ref)  │
├──────────────────────────────────────────────────────────────────────────┤
│  Risk band breakdown (donut    │  AI Insight callout (text box) +        │
│  REPLACED with stacked bar)    │  "View narrative" page-nav button       │
├──────────────────────────────────────────────────────────────────────────┤
│  Page nav buttons                                                        │
└──────────────────────────────────────────────────────────────────────────┘
```

### KPIs (top strip, five cards)

| Card | Measure | Sub-text |
|---|---|---|
| Headcount | `[Headcount]` | "active · current period" |
| Attrition rate | `[Attrition Rate]` (%) | YoY delta in green / red, sign-aware |
| High-risk count | `[High Risk Count]` | "% of workforce" sub-line |
| Engagement index | `[Engagement Index]` | "/ 100 · last pulse" |
| Open requisitions | `[Open Requisitions]` | "avg time to hire X days" |

Use **conditional formatting** on the YoY delta only. Yellow accent on the *current* metric of focus (selected via slicer).

### Visuals

1. **Headcount trend** — line chart on `DimDate[Date]` × `[Headcount]`. Single-line navy. No markers, smooth, axis labels every quarter.
2. **Attrition rate trend** — line chart, navy, with a subtle yellow reference line at the company target rate (e.g. 12%). Axis as percentage.
3. **Risk band breakdown** — 100% stacked horizontal bar with three categories (High = `#D93025`, Medium = `#F0B429`, Low = `#2E7D32`). Show data labels as `% of workforce`.
4. **AI Insight callout** — a text box framed like a quote. Pull dynamic text via a measure: e.g. `"High-risk count is " & [High Risk Count] & " — concentrated in " & [Top High-Risk Department]`. Add a button "Open Copilot" → bookmark to Page 2 with the high-risk slicer applied.

### Slicers (top right)

- Year (DimDate[Year])
- Department (DimDepartment[Department])

### Interactions

- KPI cards do **not** cross-filter the trend visuals.
- Risk band bar cross-filters the AI Insight callout text only.

### Notes / captions

Caption under "AI Insight": *"Generated by Agile HR Copilot · always reviewed by a person before action."*

### Save as

`docs/images/page1_executive.png` (export 1280 × 720 PNG, 96 DPI).

---

## Page 2 — Attrition & Retention (the strongest page)

**Story:** "Where is attrition concentrated, what's driving it, and which employees need a stay-interview now?"

### Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HEADER · Attrition & Retention                            [Year][Dept]  │
├──────────────────────────────────────────────────────────────────────────┤
│  KPI: Attrition rate │ KPI: Attrition YoY │ KPI: High-risk │ Avg risk    │
├──────────────────────────────────────────────────────────────────────────┤
│  Attrition heatmap                  │  Top SHAP drivers (bar, signed)    │
│  Department × TenureCohort          │                                    │
├──────────────────────────────────────────────────────────────────────────┤
│  High-risk employee table (top 25 by risk score, with explain button)    │
├──────────────────────────────────────────────────────────────────────────┤
│  Page nav                                                                │
└──────────────────────────────────────────────────────────────────────────┘
```

### KPIs

| Card | Measure |
|---|---|
| Attrition rate | `[Attrition Rate]` |
| YoY change | `[Attrition Rate YoY]` formatted with `+`/`-` and red/green |
| High-risk count | `[High Risk Count]` |
| Avg risk score | `[Avg Risk Score]` (0–1, format as %) |

### Visuals

1. **Attrition heatmap** — Matrix visual: rows `Department`, columns `TenureCohort`, values `[Attrition Rate]`. Background colour scale from white → `#D93025` for high. Show numeric values in cells. Tooltip = report-page tooltip with mini bar of risk band breakdown for that cell.
2. **Top SHAP drivers** — Diverging bar chart from `FactAttritionRisk` aggregated drivers. X-axis = `AVG([TopDriverImpact])` across all employees, signed. Positive bars red, negative green. Sort by `ABS()` descending. Title: "What pushes risk up vs. down (SHAP, averaged)".
3. **High-risk employee table** — Table or matrix, columns: `EmployeeID`, `Department`, `JobRole`, `TenureCohort`, `RiskScore` (data-bar, red), `RiskBand`, `TopDriver1`, `TopDriver2`, `TopDriver3`. Conditional format `RiskScore` as a horizontal red bar. Filter to `RiskBand = "High"`, top 25 by `RiskScore`.

### Slicers

- Year, Department, TenureCohort, RiskBand

### Interactions

- Heatmap **filters** the SHAP driver chart and the high-risk table.
- Selecting a row in the high-risk table navigates (via a button column) to a drillthrough page with the employee's snapshot — or, in the demo, opens the Streamlit Explain tab.

### Page-level governance note

Bottom-left, 9 pt grey: *"Risk scores are decision support, not termination criteria. Use stay-interviews and manager conversations before any formal action."*

### Save as

`docs/images/page2_attrition.png`

---

## Page 3 — Employee Engagement

**Story:** "Where is engagement strongest, where is it slipping, and what themes are people raising?"

### Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HEADER · Employee Engagement                    [Quarter][Department]   │
├──────────────────────────────────────────────────────────────────────────┤
│  KPI: Engagement idx │ Response rate │ #Pulses │ %Detractors             │
├──────────────────────────────────────────────────────────────────────────┤
│  Engagement trend by quarter (line)  │  Themes flagged (horizontal bar)  │
├──────────────────────────────────────────────────────────────────────────┤
│  Engagement vs attrition scatter (departments)                           │
├──────────────────────────────────────────────────────────────────────────┤
│  Page nav                                                                │
└──────────────────────────────────────────────────────────────────────────┘
```

### KPIs

| Card | Measure |
|---|---|
| Engagement index | `[Engagement Index]` (target line 70) |
| Response rate | `[Response Rate]` (%) |
| Pulses captured | `COUNTROWS(FactEngagementPulse)` |
| % detractors | `% of pulses with score ≤ 2` |

### Visuals

1. **Engagement trend** — line on `Quarter` × `[Engagement Index]`. Add yellow reference line at 70 ("healthy threshold"). Single navy series.
2. **Themes flagged** — horizontal bar from a calculated table that splits `ThemesFlagged` (comma-separated) into rows. Show count by theme. Single colour navy. Highlight the top theme in yellow.
3. **Engagement vs attrition scatter** — bubble chart: X = `[Engagement Index]`, Y = `[Attrition Rate]`, size = `[Headcount]`, dot per Department. Reference quadrant lines at company average. Quadrant labels: top-left ("Disengaged & leaving — act now"), bottom-right ("Engaged & retaining — protect").

### Slicers

- Quarter, Department, JobLevel

### Interactions

- Theme bar filters the trend chart by employees who flagged that theme (use cross-filter on a theme bridge table if you build one; otherwise leave it advisory).

### Save as

`docs/images/page3_engagement.png`

---

## Page 4 — Diversity & Inclusion (with privacy/k-anonymity note)

**Story:** "Are workforce composition and outcomes equitable across groups, while protecting individual privacy?"

### Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HEADER · Diversity & Inclusion              [Year][Department][Level]   │
├──────────────────────────────────────────────────────────────────────────┤
│  KPI: Diversity index │ Gender mix │ Median pay gap │ Promotion gap      │
├──────────────────────────────────────────────────────────────────────────┤
│  Composition by Gender × Level     │  Composition by AgeBand × Dept      │
├──────────────────────────────────────────────────────────────────────────┤
│  Disparate-impact ratio per group (bar with 0.8 / 1.25 reference lines)  │
├──────────────────────────────────────────────────────────────────────────┤
│  ⚠ Privacy note · Page nav                                               │
└──────────────────────────────────────────────────────────────────────────┘
```

### KPIs

| Card | Measure |
|---|---|
| Diversity index | `[Diversity Index]` |
| Gender mix | "57 / 43" (calculated text or two-bar mini visual) |
| Median pay gap | `(median pay men − median pay women) / median pay men` (use SalaryBand midpoints) |
| Promotion gap | YearsSincePromotion difference between top vs. bottom group |

### Visuals

1. **Composition Gender × Level** — 100% stacked horizontal bar, two segments only (Female `#1F3A5F`, Male `#F0B429`). Label only segments where `[K-Safe Headcount]` is not blank.
2. **Composition AgeBand × Dept** — heatmap matrix; cells suppress to `–` when count < 25.
3. **Disparate impact bar** — horizontal bar from `docs/fairness_audit_summary.csv` (load as a separate disconnected table). Two dashed reference lines at 0.8 and 1.25. Bars between the lines = `#2E7D32`, outside = `#D93025`.

### Privacy / governance note (mandatory, prominent)

Bottom of page, 11 pt grey/navy framed box:

> **Privacy guard.** Demographic cohorts smaller than n = 25 are suppressed. Group-level metrics on this page are diagnostic only — the model card lists fairness limitations and the recommended review process before any action.

### Slicers

- Year, Department, JobLevel

### Save as

`docs/images/page4_diversity.png`

---

## Page 5 — Workforce Planning

**Story:** "Are we hiring fast enough, in the right places, to land the workforce shape we need?"

### Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HEADER · Workforce Planning                   [Year][Department][Role]  │
├──────────────────────────────────────────────────────────────────────────┤
│  KPI: Open reqs │ Hires │ Avg time-to-hire │ Offer accept rate           │
├──────────────────────────────────────────────────────────────────────────┤
│  Headcount trend (12-month) │ Recruitment funnel (Sankey or stacked bar) │
├──────────────────────────────────────────────────────────────────────────┤
│  Time-to-hire by Department (clustered bar)                              │
├──────────────────────────────────────────────────────────────────────────┤
│  Page nav                                                                │
└──────────────────────────────────────────────────────────────────────────┘
```

### KPIs

| Card | Measure |
|---|---|
| Open requisitions | `DISTINCTCOUNT(FactRecruitment[RequisitionID])` filtered to non-Hired |
| Hires (period) | `CALCULATE(COUNTROWS(FactRecruitment), [FinalStage]="Hired")` |
| Avg time-to-hire | `[Avg Time to Hire]` days |
| Offer acceptance | `[Offer Acceptance]` % |

### Visuals

1. **Headcount trend (12-month)** — line on `DimDate[Date]` × `[Headcount]`, navy. Optional area fill at 5% opacity.
2. **Recruitment funnel** — funnel visual or stacked bar. Stages: Applied → Screened → Interviewed → Offered → Hired. Single navy gradient. Label conversion % between stages on the side.
3. **Time-to-hire by department** — horizontal bar, `Department` × `[Avg Time to Hire]`. Yellow reference line at company-wide average. Label values to one decimal.

### Slicers

- Year, Department, JobRole

### Interactions

- Funnel filters the time-to-hire bar.
- Headcount trend stays unfiltered by funnel.

### Save as

`docs/images/page5_workforce.png`

---

## Build sequence (recommended)

1. Build the data model: relate `DimDate`, `DimEmployee`, `DimDepartment`, `DimJobRole` to facts. Set DimDate as the Date table.
2. Add the Measures table from the DAX above.
3. Theme the report: *View → Themes → Browse for themes* and load a custom JSON theme using the palette (or set colours per visual the first time, then save as a new theme).
4. Build pages in this order: 1 (frame), then 2 (the headline), then 5, 3, 4.
5. Add page navigator and bookmarks last.
6. Export each page: *File → Export → PDF*, then crop, OR use the Power BI screenshot button to save 1280 × 720 PNGs into `docs/images/`.
7. Re-run `python scripts/verify_day4.py` and confirm the screenshot files are listed as present.
