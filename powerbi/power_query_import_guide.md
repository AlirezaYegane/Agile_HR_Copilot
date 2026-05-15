# Power Query / Import Guide — Agile HR Copilot

> The report connects to local Parquet files in `lakehouse/gold/`. Because Parquet files are git-ignored, you must run Day 1 (and Day 2 for the risk fact) before Power BI can refresh.

## 0. Prerequisites

```powershell
cd D:\Agile_HR_Copilot
.\.venv\Scripts\Activate.ps1
python scripts\day1_build_lakehouse.py
python scripts\day2_train_attrition_model.py
python powerbi\validate_gold_for_powerbi.py
```

The validator (PART B.5) will tell you immediately if any required Parquet file or column is missing — fix that before you open the .pbix.

## 1. Create the data sources

In Power BI Desktop:

1. *Home → Get data → More… → File → Parquet* → click **Connect**.
2. Select the file. Use the **path** parameter pointing to the absolute location, e.g. `D:\Agile_HR_Copilot\lakehouse\gold\dim_date.parquet`.
3. Click **OK**, then **Transform Data**.

Repeat for every file in the table below.

| Parquet file | Power BI table name |
|---|---|
| `lakehouse/gold/dim_date.parquet` | `DimDate` |
| `lakehouse/gold/dim_department.parquet` | `DimDepartment` |
| `lakehouse/gold/dim_employee.parquet` | `DimEmployee` |
| `lakehouse/gold/dim_jobrole.parquet` | `DimJobRole` |
| `lakehouse/gold/fact_employee_snapshot.parquet` | `FactEmployeeSnapshot` |
| `lakehouse/gold/fact_engagement_pulse.parquet` | `FactEngagementPulse` |
| `lakehouse/gold/fact_recruitment.parquet` | `FactRecruitment` |
| `lakehouse/gold/fact_attrition_risk.parquet` | `FactAttritionRisk` |

### Optional: parameterise the lakehouse path

In **Power Query → Manage Parameters → New Parameter** create:

- **Name:** `LakehousePath`
- **Type:** Text
- **Default:** `D:\Agile_HR_Copilot\lakehouse\gold`

Then rewrite each query (Advanced Editor) using a helper. Drop the file-specific path and replace with:

```m
let
    Source = Parquet.Document(File.Contents(LakehousePath & "\dim_date.parquet"))
in
    Source
```

This makes it portable — anyone cloning the repo can change `LakehousePath` once.

## 2. Required types and fixes

For every query, click *Detect Data Types*. Then make these explicit corrections:

### `DimDate`

- `DateKey` → Whole Number
- `Date` → Date
- `Year`, `Quarter`, `Month` → Whole Number
- `MonthName`, `FYLabel` → Text
- *Mark as date table*: **Modeling → Mark as date table** → choose `Date`.

### `DimEmployee`

- `EmployeeID` → Text (it is already, but confirm)
- `Education`, `JobLevel`, `DistanceFromHome` → Whole Number
- All other text fields → Text

### `DimDepartment`, `DimJobRole`

- ID columns → Text
- Numeric ID-like columns (none expected) — leave alone

### `FactEmployeeSnapshot`

- `EmployeeID`, `JobRoleID`, `DepartmentID` → Text
- `DateKey` → Whole Number
- `IsActive`, `AttritionThisMonth`, `OvertimeFlag` → Whole Number
- `MonthlyIncome`, `JobLevel`, `JobSatisfaction`, `EnvSatisfaction`, `WorkLifeBalance`, `JobInvolvement`, `PerformanceRating` → Whole Number
- `TenureYears`, `YearsInRole`, `YearsSincePromotion`, `YearsWithManager` → Decimal Number

### `FactEngagementPulse`

- `EmployeeID` → Text
- `QuarterKey` → Whole Number
- `Quarter` → Date
- `PulseScore` → Whole Number
- `ThemesFlagged` → Text (it stays comma-separated; you can split it for the Engagement page)

### `FactRecruitment`

- `RequisitionID`, `JobRoleID`, `DepartmentID`, `ApplicationID`, `FinalStage` → Text
- `AppliedDate` → Date
- `DaysInPipeline` → Whole Number
- `DateKey` → Whole Number

### `FactAttritionRisk`

- `EmployeeID`, `RiskBand`, `TopDriver1`, `TopDriver2`, `TopDriver3` → Text
- `RiskScore`, `TopDriver1Impact`, `TopDriver2Impact`, `TopDriver3Impact` → Decimal Number

## 3. Themes split (one helper table)

Create a new query, **Themes** (right-click `FactEngagementPulse` → *Reference*), then:

1. Filter `ThemesFlagged ≠ null`.
2. *Add column → Custom column*: `Text.Split([ThemesFlagged], ",")`.
3. *Expand* the new column to rows.
4. Trim and lowercase the result.
5. Keep `[EmployeeID, QuarterKey, Theme]`.

This unlocks the **Themes flagged** bar chart on Page 3 without complex DAX.

## 4. Relationships (model view)

Create these relationships exactly. Cardinality and direction:

| From | To | Cardinality | Direction |
|---|---|---|---|
| `FactEmployeeSnapshot[EmployeeID]` | `DimEmployee[EmployeeID]` | Many-to-one | Single |
| `FactEmployeeSnapshot[JobRoleID]` | `DimJobRole[JobRoleID]` | Many-to-one | Single |
| `FactEmployeeSnapshot[DepartmentID]` | `DimDepartment[DepartmentID]` | Many-to-one | Single |
| `FactEmployeeSnapshot[DateKey]` | `DimDate[DateKey]` | Many-to-one | Single |
| `DimJobRole[DepartmentID]` | `DimDepartment[DepartmentID]` | Many-to-one | Single |
| `FactRecruitment[JobRoleID]` | `DimJobRole[JobRoleID]` | Many-to-one | Single |
| `FactRecruitment[DateKey]` | `DimDate[DateKey]` | Many-to-one | Single |
| `FactEngagementPulse[EmployeeID]` | `DimEmployee[EmployeeID]` | Many-to-one | Single |
| `FactAttritionRisk[EmployeeID]` | `DimEmployee[EmployeeID]` | One-to-one (or Many-to-one) | Single |

> If Power BI complains about ambiguous paths between `DimDepartment` and `FactEmployeeSnapshot` (because `DimJobRole` also relates to `DimDepartment`), keep the **direct** `FactEmployeeSnapshot[DepartmentID] → DimDepartment[DepartmentID]` relationship **active** and the indirect path inactive.

## 5. Apply the theme

*View → Themes → Browse for themes* → load `powerbi/AgileHRTheme.json`.

## 6. Build the pages

Follow `docs/powerbi_design.md` page-by-page. Use the `_Measures` table from `powerbi/dax_measures.md`.

## 7. Save

Save to `powerbi/AgileHRCopilot.pbix`. Do not commit — the file is fine to commit if you wish, but check first that no real-data caches are embedded (use *Transform data → Data source settings* and ensure only the local Parquet files are listed).
