<div dir="ltr">

# Release Notes — v1-polished

## Summary

`v1-polished` is the clean baseline release of Agile HR Copilot. It packages the current data pipeline, ML risk model, Power BI dashboard, governance artefacts, and local Copilot demo into an interview-ready version.

## Included

- Medallion-style local lakehouse
- Gold star schema for Power BI
- Attrition risk model with SHAP outputs
- Power BI dashboard screenshots
- FastAPI Copilot backend
- Streamlit Copilot UI
- Policy-grounded RAG over HR PDFs
- Governance docs, model card, and architecture doc
- Local smoke-test artefacts

## Verified in this release

- Day 1 lakehouse verification passed
- Day 2 ML verification passed
- Day 4 governance and demo verification passed
- Day 5 API smoke test passed
- Day 5 Streamlit smoke test passed

## Known limitations

- This is not a production HR system.
- Data is public and synthetic, not real employee data.
- LLM output may fall back when provider keys are unavailable.
- Fabric deployment is planned for the next phase.

## Next phase

Day 6 begins the Microsoft Fabric foundation: workspace setup, local-to-Fabric mapping, and OneLake/Lakehouse documentation.

</div>
