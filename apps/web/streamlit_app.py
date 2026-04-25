"""
Agile HR Copilot — Streamlit demo UI.

Decision support, not decision maker.
"""
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


API_BASE = "http://127.0.0.1:8001/api"
ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "lakehouse/gold"

# Brand palette ------------------------------------------------------------
NAVY = "#1F3A5F"
YELLOW = "#F0B429"
NEUTRAL = "#546E7A"
GOOD = "#2E7D32"
RISK = "#D93025"
SOFT_BG = "#F7F9FC"
BORDER = "#E5EAF2"


st.set_page_config(
    page_title="Agile HR Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---- Global styling ------------------------------------------------------
st.markdown(
    f"""
    <style>
        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 2.5rem;
            max-width: 1180px;
        }}
        h1, h2, h3, h4 {{
            color: {NAVY};
            font-weight: 600;
            letter-spacing: -0.01em;
        }}
        .ahr-hero {{
            padding: 1.6rem 1.8rem;
            border-radius: 18px;
            background: linear-gradient(135deg, {NAVY} 0%, #2A4D7A 100%);
            color: white;
            box-shadow: 0 6px 20px rgba(31,58,95,0.18);
        }}
        .ahr-hero h1 {{
            color: white;
            margin: 0;
            font-size: 1.85rem;
        }}
        .ahr-hero p {{
            margin: .35rem 0 0 0;
            color: #DCE5F2;
            font-size: 0.97rem;
        }}
        .ahr-hero .pill {{
            display: inline-block;
            padding: 0.18rem 0.7rem;
            border-radius: 999px;
            background: {YELLOW};
            color: {NAVY};
            font-weight: 600;
            font-size: 0.78rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-right: 0.4rem;
        }}
        .ahr-card {{
            padding: 1rem 1.15rem;
            border-radius: 14px;
            background: white;
            border: 1px solid {BORDER};
            box-shadow: 0 1px 3px rgba(20,30,55,0.04);
        }}
        .ahr-kpi-label {{
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {NEUTRAL};
            margin-bottom: 0.25rem;
        }}
        .ahr-kpi-value {{
            font-size: 1.55rem;
            font-weight: 700;
            color: {NAVY};
            line-height: 1.1;
        }}
        .ahr-kpi-sub {{
            font-size: 0.78rem;
            color: {NEUTRAL};
            margin-top: 0.2rem;
        }}
        .ahr-status-good {{
            color: {GOOD};
            font-weight: 600;
        }}
        .ahr-status-bad {{
            color: {RISK};
            font-weight: 600;
        }}
        .ahr-status-neutral {{
            color: {NEUTRAL};
            font-weight: 600;
        }}
        .ahr-source {{
            padding: 0.7rem 0.9rem;
            border-left: 4px solid {YELLOW};
            background: {SOFT_BG};
            border-radius: 8px;
            margin-bottom: 0.55rem;
        }}
        .ahr-source-name {{
            font-weight: 600;
            color: {NAVY};
            font-size: 0.92rem;
        }}
        .ahr-source-meta {{
            color: {NEUTRAL};
            font-size: 0.78rem;
        }}
        .ahr-footer {{
            margin-top: 1.6rem;
            padding-top: 0.9rem;
            border-top: 1px solid {BORDER};
            color: {NEUTRAL};
            font-size: 0.83rem;
            text-align: center;
        }}
        .ahr-band-high {{
            color: {RISK};
            font-weight: 700;
        }}
        .ahr-band-medium {{
            color: {YELLOW};
            font-weight: 700;
        }}
        .ahr-band-low {{
            color: {GOOD};
            font-weight: 700;
        }}
        div[data-testid="stTabs"] button[role="tab"] {{
            font-weight: 600;
            color: {NEUTRAL};
        }}
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            color: {NAVY};
            border-bottom: 3px solid {YELLOW} !important;
        }}
        .stButton > button[kind="primary"] {{
            background: {NAVY};
            border-color: {NAVY};
        }}
        .stButton > button[kind="primary"]:hover {{
            background: #163052;
            border-color: #163052;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---- API helpers ---------------------------------------------------------
def api_get(path: str):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=20)
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return 0, {"error": "connection refused"}
    except Exception as e:
        return 0, {"error": str(e)}


def api_post(path: str, payload: dict, timeout: int = 60):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=timeout)
        return r.status_code, r.json()
    except requests.exceptions.ConnectionError:
        return 0, {"error": "connection refused"}
    except Exception as e:
        return 0, {"error": str(e)}


def render_backend_offline():
    st.error(
        "Backend is not reachable on `http://127.0.0.1:8001`. "
        "Start FastAPI in another terminal before using this app."
    )
    st.code(
        "cd D:\\Agile_HR_Copilot\n"
        ".\\.venv\\Scripts\\Activate.ps1\n"
        "uvicorn apps.api.app.main:app --port 8001",
        language="powershell",
    )


# ---- Hero ----------------------------------------------------------------
st.markdown(
    """
    <div class="ahr-hero">
        <span class="pill">People Analytics Accelerator</span>
        <span class="pill" style="background: rgba(255,255,255,0.15); color: white;">Fabric-inspired</span>
        <h1>Agile HR Copilot</h1>
        <p>Board-ready narratives, policy-grounded answers, and explainable attrition risk —
        powered by a medallion lakehouse and governed AI.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")


# ---- Status strip --------------------------------------------------------
status_code, health = api_get("/health")
backend_online = status_code == 200

s1, s2, s3 = st.columns(3)
with s1:
    state = '<span class="ahr-status-good">● Online</span>' if backend_online else '<span class="ahr-status-bad">● Offline</span>'
    st.markdown(
        f"""
        <div class="ahr-card">
            <div class="ahr-kpi-label">Backend</div>
            <div class="ahr-kpi-value">{state}</div>
            <div class="ahr-kpi-sub">FastAPI · port 8001</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s2:
    rag_ready = bool(health.get("rag_ready")) if backend_online else False
    label = '<span class="ahr-status-good">Ready</span>' if rag_ready else '<span class="ahr-status-neutral">Not ready</span>'
    st.markdown(
        f"""
        <div class="ahr-card">
            <div class="ahr-kpi-label">Policy retriever</div>
            <div class="ahr-kpi-value">{label}</div>
            <div class="ahr-kpi-sub">Local TF-IDF over HR policy PDFs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s3:
    chunks = health.get("policy_chunks", 0) if backend_online else 0
    st.markdown(
        f"""
        <div class="ahr-card">
            <div class="ahr-kpi-label">Policy corpus</div>
            <div class="ahr-kpi-value">{chunks}</div>
            <div class="ahr-kpi-sub">indexed chunks</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

if not backend_online:
    render_backend_offline()
    st.stop()


# ---- Tabs ----------------------------------------------------------------
tab_narr, tab_qa, tab_risk = st.tabs(
    ["📝  Board Narrative", "💬  Policy Q&A", "🔍  Explain Attrition Risk"]
)


# ===== Tab 1: Board Narrative ============================================
with tab_narr:
    st.subheader("Generate a board-ready people analytics narrative")
    st.caption(
        "Enter the headline KPIs for the period. The Copilot will produce a concise CHRO-ready "
        "briefing. If Gemini is unavailable, a deterministic local narrative is returned instead."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        period = st.text_input("Reporting period", value="Q3 2026")
        headcount = st.number_input("Headcount", value=1420, step=10)
    with col2:
        attrition_rate = st.text_input("Attrition rate", value="18%")
        high_risk = st.number_input("High-risk employees", value=87, step=1)
    with col3:
        engagement = st.text_input("Engagement index", value="68/100")
        open_reqs = st.number_input("Open requisitions", value=24, step=1)

    if st.button("Generate narrative", type="primary", key="gen_narr"):
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

        with st.spinner("Drafting executive narrative..."):
            code, data = api_post("/narrative", payload)

        if code == 200:
            st.markdown("#### Narrative")
            st.markdown(
                f"""
                <div class="ahr-card" style="background: {SOFT_BG};">
                    <div style="white-space: pre-wrap; line-height: 1.55; color: #1A2434;">
                        {data["narrative"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(f"Period: {data.get('period', period)} · Generated by Agile HR Copilot")
        else:
            st.error(f"Narrative generation failed (HTTP {code}). Details: {data}")


# ===== Tab 2: Policy Q&A =================================================
with tab_qa:
    st.subheader("Ask a policy-grounded question")
    st.caption(
        "Answers are grounded in the indexed HR policy PDFs. Sources are always shown. "
        "If the corpus does not contain the answer, the Copilot will say so rather than guess."
    )

    suggested = st.selectbox(
        "Suggested questions",
        [
            "What does our retention policy say about stay interviews?",
            "How does the compensation policy handle pay-equity reviews?",
            "What does the diversity & inclusion policy say about wellbeing support?",
            "Custom question…",
        ],
        index=0,
    )

    default_q = "" if suggested == "Custom question…" else suggested
    question = st.text_area("Question", value=default_q, height=90, key="qa_input")

    if st.button("Ask Copilot", type="primary", key="ask_btn"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Retrieving policy context..."):
                code, data = api_post("/ask", {"question": question})

            if code == 200:
                st.markdown("#### Answer")
                st.markdown(
                    f"""
                    <div class="ahr-card" style="background: {SOFT_BG};">
                        <div style="white-space: pre-wrap; line-height: 1.55; color: #1A2434;">
                            {data.get("answer", "")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                sources = data.get("sources", [])
                st.markdown(f"#### Sources <span style='color:{NEUTRAL}; font-size:.85rem;'>({len(sources)} retrieved)</span>",
                            unsafe_allow_html=True)
                for src in sources:
                    score = src.get("score", 0.0)
                    st.markdown(
                        f"""
                        <div class="ahr-source">
                            <div class="ahr-source-name">{src['source']}</div>
                            <div class="ahr-source-meta">chunk {src['chunk']} · retrieval score {score:.3f}</div>
                            <div style="color:#1A2434; font-size:.9rem; margin-top:.35rem;">{src.get('preview', '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.error(f"Q&A request failed (HTTP {code}). Details: {data}")


# ===== Tab 3: Explain Attrition Risk =====================================
with tab_risk:
    st.subheader("Explain attrition risk in plain English")
    st.caption(
        "Pick an employee. The Copilot returns the SHAP-driven top risk factors and a "
        "supportive, manager-friendly explanation. This is decision support, not a decision."
    )

    risk_df = None
    employee_id = None
    risk_path = GOLD / "fact_attrition_risk.parquet"

    if risk_path.exists():
        try:
            risk_df = pd.read_parquet(risk_path)
            top = risk_df.sort_values("RiskScore", ascending=False).head(50)
            employee_id = st.selectbox(
                "Select an employee (sorted by risk score, highest first)",
                options=top["EmployeeID"].tolist(),
                format_func=lambda eid: (
                    f"{eid}  ·  risk "
                    f"{risk_df.loc[risk_df.EmployeeID == eid, 'RiskScore'].iloc[0]:.0%}  ·  "
                    f"{risk_df.loc[risk_df.EmployeeID == eid, 'RiskBand'].iloc[0]}"
                ),
            )
        except Exception as e:
            st.warning(f"Could not load risk table: {e}")
            employee_id = st.text_input("Employee ID")
    else:
        st.info(
            "Risk table not found. Run `python scripts\\day2_train_attrition_model.py` "
            "to generate `lakehouse/gold/fact_attrition_risk.parquet`."
        )
        employee_id = st.text_input("Employee ID")

    if st.button("Explain risk", type="primary", key="explain_btn") and employee_id:
        with st.spinner("Generating explanation..."):
            code, data = api_post("/explain-risk", {"employee_id": employee_id})

        if code == 200:
            band = str(data.get("risk_band", "")).lower()
            band_class = {"high": "ahr-band-high", "medium": "ahr-band-medium", "low": "ahr-band-low"}.get(band, "ahr-status-neutral")

            kc1, kc2, kc3 = st.columns([1, 1, 2])
            with kc1:
                st.markdown(
                    f"""
                    <div class="ahr-card">
                        <div class="ahr-kpi-label">Risk score</div>
                        <div class="ahr-kpi-value">{data['risk_score']:.0%}</div>
                        <div class="ahr-kpi-sub">model probability</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with kc2:
                st.markdown(
                    f"""
                    <div class="ahr-card">
                        <div class="ahr-kpi-label">Risk band</div>
                        <div class="ahr-kpi-value"><span class="{band_class}">{data['risk_band']}</span></div>
                        <div class="ahr-kpi-sub">Low &lt; 25% · Medium 25–50% · High ≥ 50%</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with kc3:
                drivers = data.get("top_drivers", [])
                drivers_html = "".join(
                    f"<li><b>{d['driver']}</b> "
                    f"<span style='color:{RISK if d['impact']>0 else GOOD};'>"
                    f"({'+' if d['impact']>0 else ''}{d['impact']:.3f})</span></li>"
                    for d in drivers
                )
                st.markdown(
                    f"""
                    <div class="ahr-card">
                        <div class="ahr-kpi-label">Top drivers (SHAP)</div>
                        <ol style="margin:.25rem 0 0 1rem; padding:0; color:#1A2434;">
                            {drivers_html}
                        </ol>
                        <div class="ahr-kpi-sub" style="margin-top:.4rem;">+ pushes risk up · − pushes risk down</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")
            st.markdown("#### Manager-friendly explanation")
            st.markdown(
                f"""
                <div class="ahr-card" style="background: {SOFT_BG};">
                    <div style="white-space: pre-wrap; line-height: 1.55; color: #1A2434;">
                        {data.get("explanation", "")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("View raw driver table"):
                st.dataframe(
                    pd.DataFrame(data.get("top_drivers", [])),
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.error(f"Explain-risk request failed (HTTP {code}). Details: {data}")


# ---- Footer --------------------------------------------------------------
st.markdown(
    """
    <div class="ahr-footer">
        <b>Decision support, not decision maker.</b> Synthetic / public data only.
        All AI calls are audit-logged by the API. See <code>docs/model_card.md</code> for limitations.
    </div>
    """,
    unsafe_allow_html=True,
)
