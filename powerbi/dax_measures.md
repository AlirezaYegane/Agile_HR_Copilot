# DAX Measures — Agile HR Copilot

> Paste these into a dedicated `_Measures` table in Power BI Desktop.
>
> Workflow: *Home → Enter data → Create*. Name the table `_Measures`. Add a single throwaway column (it can be deleted later). Then create each measure below via *Modeling → New measure*.
>
> The leading underscore keeps the measures table at the top of the field list.

## 1 — Headcount and workforce shape

```DAX
Headcount =
CALCULATE(
    DISTINCTCOUNT( FactEmployeeSnapshot[EmployeeID] ),
    FactEmployeeSnapshot[IsActive] = 1
)
```

```DAX
Average Headcount =
AVERAGEX(
    VALUES( DimDate[DateKey] ),
    [Headcount]
)
```

```DAX
Headcount (k-safe) =
VAR n = [Headcount]
RETURN IF( n >= 25, n, BLANK() )
```

## 2 — Attrition

```DAX
Attrition Count =
CALCULATE( SUM( FactEmployeeSnapshot[AttritionThisMonth] ) )
```

```DAX
Attrition Rate =
DIVIDE( [Attrition Count], [Average Headcount] )
```

```DAX
Attrition Rate YoY =
CALCULATE( [Attrition Rate], SAMEPERIODLASTYEAR( DimDate[Date] ) )
```

```DAX
Attrition Rate YoY (pp delta) =
[Attrition Rate] - [Attrition Rate YoY]
```

```DAX
Attrition Rate (k-safe) =
VAR n = [Headcount]
RETURN IF( n >= 25, [Attrition Rate], BLANK() )
```

## 3 — Risk model surface

```DAX
High Risk Count =
CALCULATE( COUNTROWS( FactAttritionRisk ), FactAttritionRisk[RiskBand] = "High" )
```

```DAX
Medium Risk Count =
CALCULATE( COUNTROWS( FactAttritionRisk ), FactAttritionRisk[RiskBand] = "Medium" )
```

```DAX
Low Risk Count =
CALCULATE( COUNTROWS( FactAttritionRisk ), FactAttritionRisk[RiskBand] = "Low" )
```

```DAX
Average Risk Score =
AVERAGE( FactAttritionRisk[RiskScore] )
```

```DAX
Estimated Cost of Attrition =
-- Placeholder loaded cost per departure. Document this assumption in the model card.
VAR LoadedCostPerLeaver = 75000
RETURN [Attrition Count] * LoadedCostPerLeaver
```

## 4 — Engagement

```DAX
Avg Pulse Score =
AVERAGE( FactEngagementPulse[PulseScore] )
```

```DAX
Engagement Index =
[Avg Pulse Score] * 20    -- maps a 1-5 pulse to a 0-100 index
```

```DAX
Response Rate =
DIVIDE(
    DISTINCTCOUNT( FactEngagementPulse[EmployeeID] ),
    [Headcount]
)
```

```DAX
Avg Job Satisfaction =
AVERAGE( FactEmployeeSnapshot[JobSatisfaction] )
```

```DAX
Avg Work-Life Balance =
AVERAGE( FactEmployeeSnapshot[WorkLifeBalance] )
```

## 5 — Diversity

```DAX
Gender Ratio F =
DIVIDE(
    CALCULATE( DISTINCTCOUNT( DimEmployee[EmployeeID] ), DimEmployee[Gender] = "Female" ),
    DISTINCTCOUNT( DimEmployee[EmployeeID] )
)
```

```DAX
Diversity Index =
1
- SUMX(
    SUMMARIZE(
        DimEmployee,
        DimEmployee[Gender],
        "p",
        DIVIDE(
            CALCULATE( DISTINCTCOUNT( DimEmployee[EmployeeID] ) ),
            CALCULATE( DISTINCTCOUNT( DimEmployee[EmployeeID] ), ALL( DimEmployee[Gender] ) )
        )
    ),
    [p] ^ 2
)
```

## 6 — Workforce planning / recruitment

```DAX
Open Requisitions =
CALCULATE(
    DISTINCTCOUNT( FactRecruitment[RequisitionID] ),
    FactRecruitment[FinalStage] <> "Hired"
)
```

```DAX
Total Applications =
COUNTROWS( FactRecruitment )
```

```DAX
Hires =
CALCULATE( COUNTROWS( FactRecruitment ), FactRecruitment[FinalStage] = "Hired" )
```

```DAX
Hire Rate =
DIVIDE( [Hires], [Average Headcount] )
```

```DAX
Avg Time to Hire =
AVERAGEX(
    FILTER( FactRecruitment, FactRecruitment[FinalStage] = "Hired" ),
    FactRecruitment[DaysInPipeline]
)
```

```DAX
Offer Acceptance Rate =
DIVIDE(
    [Hires],
    CALCULATE(
        COUNTROWS( FactRecruitment ),
        FactRecruitment[FinalStage] IN { "Offered", "Hired" }
    )
)
```

```DAX
Funnel Conversion Applied to Hired =
DIVIDE( [Hires], [Total Applications] )
```

```DAX
Promotion Proxy Rate =
-- Proxy: share of employees with YearsSincePromotion <= 1 in the latest snapshot.
VAR LatestKey = MAX( DimDate[DateKey] )
VAR Recent =
    CALCULATETABLE(
        FactEmployeeSnapshot,
        FactEmployeeSnapshot[DateKey] = LatestKey,
        FactEmployeeSnapshot[IsActive] = 1
    )
RETURN
    DIVIDE(
        COUNTROWS( FILTER( Recent, FactEmployeeSnapshot[YearsSincePromotion] <= 1 ) ),
        COUNTROWS( Recent )
    )
```

## 7 — Formatting standards

| Measure | Format |
|---|---|
| Headcount, Headcount (k-safe), High/Medium/Low Risk Count, Attrition Count, Hires, Open Requisitions, Total Applications | Whole number with thousands separator |
| Attrition Rate, Attrition Rate YoY, Hire Rate, Offer Acceptance Rate, Funnel Conversion Applied to Hired, Response Rate, Promotion Proxy Rate, Gender Ratio F | Percentage, 1 decimal |
| Attrition Rate YoY (pp delta) | Percentage, 1 decimal, with `+`/`-` sign (use a custom format `+0.0%;-0.0%;0.0%`) |
| Average Risk Score | Percentage, 1 decimal |
| Estimated Cost of Attrition | Currency (no decimals) |
| Avg Pulse Score, Engagement Index, Avg Job Satisfaction, Avg Work-Life Balance, Diversity Index | Decimal, 2 places |
| Avg Time to Hire | Decimal, 1 place — append `" days"` via *Modeling → Format → Custom* if desired |

## 8 — Suggested home tables and folders

In the field list, set the *Home table* to `_Measures` for every measure. Group them into display folders:

- `1. Workforce`
- `2. Attrition`
- `3. Risk`
- `4. Engagement`
- `5. Diversity`
- `6. Recruitment`
