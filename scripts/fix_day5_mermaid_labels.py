from pathlib import Path

for p in [Path("README.md"), Path("docs/architecture.md")]:
    if not p.exists():
        continue

    s = p.read_text(encoding="utf-8")

    replacements = {
        r"Bronze Layer\\nRaw + lineage metadata": "Bronze Layer<br/>Raw + lineage metadata",
        r"Silver Layer\\nCleaned + anonymised + bucketed": "Silver Layer<br/>Cleaned + anonymised + bucketed",
        r"Gold Star Schema\\nFacts + Dimensions": "Gold Star Schema<br/>Facts + Dimensions",
        r"CHRO Dashboards\\nExecutive, Attrition, Engagement, Diversity, Workforce": "CHRO Dashboards<br/>Executive, Attrition, Engagement, Diversity, Workforce",
        r"Attrition Risk Model\\nRandom Forest + SHAP": "Attrition Risk Model<br/>Random Forest + SHAP",
        r"Risk Fact Table\\nfact_attrition_risk": "Risk Fact Table<br/>fact_attrition_risk",
    }

    for old, new in replacements.items():
        s = s.replace(old, new)

    p.write_text(s, encoding="utf-8")
    print(f"cleaned mermaid labels in {p}")
