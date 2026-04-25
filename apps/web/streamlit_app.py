from pathlib import Path

import pandas as pd
import requests
import streamlit as st


API_BASE = "http://127.0.0.1:8001/api"
ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "lakehouse/gold"


st.set_page_config(
    page_title="Agile HR Copilot",
    page_icon="🤖",
    layout="wide",
)


def api_get(path: str):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=20)
        return r.status_code, r.json()
    except Exception as e:
        return 0, {"error": str(e)}


def api_post(path: str, payload: dict, timeout: int = 60):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=timeout)
        return r.status_code, r.json()
    except Exception as e:
        return 0, {"error": str(e)}


st.markdown(
    """
    <div style="padding: 1.2rem 1.4rem; border-radius: 18px; background: #F7F9FC; border: 1px solid #E5EAF2;">
        <h1 style="margin: 0; color: #1F3A5F;">Agile HR Copilot</h1>
        <p style="margin: .35rem 0 0 0; color: #546E7A;">
            AI-powered people analytics over a Fabric-inspired HR lakehouse.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

status_code, health = api_get("/health")
if status_code == 200:
    st.success(f"Backend connected · RAG ready: {health.get('rag_ready')} · Policy chunks: {health.get('policy_chunks')}")
else:
    st.error("Backend is not reachable. Start FastAPI on port 8001 before using this app.")
    st.code("uvicorn apps.api.app.main:app --port 8001", language="powershell")

tab1, tab2, tab3 = st.tabs(
    [
        "📝 Board Narrative",
        "💬 Policy Q&A",
        "🔍 Explain Attrition Risk",
    ]
)


with tab1:
    st.subheader("Generate a board-ready people analytics narrative")

    col1, col2, col3 = st.columns(3)

    with col1:
        period = st.text_input("Reporting period", value="Q3 2026")
        headcount = st.number_input("Headcount", value=1420, step=10)

    with col2:
        attrition_rate = st.text_input("Attrition Rate", value="18%")
        high_risk = st.number_input("High-risk employees", value=87, step=1)

    with col3:
        engagement = st.text_input("Engagement Index", value="68/100")
        open_reqs = st.number_input("Open requisitions", value=24, step=1)

    if st.button("Generate narrative", type="primary"):
        payload = {
            "period": period,
            "kpis": {
                "Headcount": headcount,
                "Attrition Rate": attrition_rate,
                "High Risk Count": high_risk,
                "Engagement Index": engagement,
                "Open Requisitions": open_reqs,
            },
        }

        with st.spinner("Generating executive narrative..."):
            code, data = api_post("/narrative", payload)

        if code == 200:
            st.markdown("### Narrative")
            st.info(data["narrative"])
        else:
            st.error(data)


with tab2:
    st.subheader("Ask a policy-grounded question")

    question = st.text_area(
        "Question",
        value="What does our retention policy say about stay interviews?",
        height=100,
    )

    if st.button("Ask Copilot", type="primary"):
        with st.spinner("Retrieving policy context..."):
            code, data = api_post("/ask", {"question": question})

        if code == 200:
            st.markdown("### Answer")
            st.write(data["answer"])

            with st.expander("Sources"):
                for source in data.get("sources", []):
                    st.markdown(f"**{source['source']}** — chunk `{source['chunk']}`")
                    if "score" in source:
                        st.caption(f"retrieval score: {source['score']:.3f}")
                    st.write(source["preview"])
                    st.divider()
        else:
            st.error(data)


with tab3:
    st.subheader("Explain attrition risk in plain English")

    try:
        risk = pd.read_parquet(GOLD / "fact_attrition_risk.parquet")
        top = risk.sort_values("RiskScore", ascending=False).head(30)

        employee_id = st.selectbox(
            "Select a high-risk employee",
            options=top["EmployeeID"].tolist(),
            format_func=lambda eid: f"{eid} · risk {risk.loc[risk.EmployeeID == eid, 'RiskScore'].iloc[0]:.0%}",
        )
    except Exception as e:
        st.warning(f"Could not load risk table: {e}")
        employee_id = st.text_input("Employee ID")

    if st.button("Explain risk", type="primary"):
        with st.spinner("Generating explanation..."):
            code, data = api_post("/explain-risk", {"employee_id": employee_id})

        if code == 200:
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.metric("Risk score", f"{data['risk_score']:.0%}")
                st.metric("Risk band", data["risk_band"])
            with col_b:
                st.markdown("### Explanation")
                st.write(data["explanation"])

            with st.expander("Model drivers"):
                st.dataframe(pd.DataFrame(data.get("top_drivers", [])), use_container_width=True)
        else:
            st.error(data)


st.divider()
st.caption(
    "Decision support, not decision maker. Synthetic/public data only. "
    "All AI calls are logged by the API for auditability."
)
