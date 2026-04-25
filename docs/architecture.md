# Architecture

```mermaid
flowchart LR
    SRC["Public IBM HR dataset<br/>+ synthetic augmentation"] --> BR

    subgraph LH["Fabric-inspired Lakehouse"]
        BR["Bronze<br/>raw Parquet + lineage"] --> SI["Silver<br/>cleaned + anonymised"]
        SI --> GO["Gold<br/>star schema"]
    end

    GO --> PBI["Power BI<br/>semantic model + DAX"]
    GO --> ML["ML pipeline<br/>scikit-learn + SHAP"]
    ML --> RISK["Attrition risk fact table"]
    RISK --> GO

    PBI --> DASH["5 CHRO dashboard pages"]

    subgraph COP["AI Insights Copilot"]
        API["FastAPI backend"]
        UI["Streamlit UI"]
        RAG["Local policy retriever<br/>TF-IDF over HR PDFs"]
        LLM["Gemini generation<br/>with local fallback"]
        UI --> API
        API --> RAG
        API --> LLM
    end

    GO --> API
    POL["HR policy PDFs"] --> RAG
Notes

This local build mirrors the shape of a Microsoft Fabric implementation:

Bronze/Silver/Gold lakehouse layers map to OneLake/Delta patterns.
The Gold layer feeds the Power BI semantic model.
The ML model writes predictions back into Gold as a reusable fact table.
The Copilot layer grounds answers in HR policy documents and people analytics KPIs.
