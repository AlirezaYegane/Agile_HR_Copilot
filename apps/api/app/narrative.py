from pathlib import Path
import os

import google.generativeai as genai
from dotenv import load_dotenv


NARRATIVE_PROMPT = """You are a senior people analytics consultant preparing a briefing for a CHRO.

Write a concise, board-ready narrative for the period below using the KPIs.

Constraints:
- 150 words maximum
- Three short paragraphs:
  (1) headline KPI and what moved
  (2) most important driver
  (3) one recommended action
- No jargon.
- No hedging language such as "it seems", "perhaps", or "may indicate".
- Quote numbers from the KPIs verbatim.
- Do not invent numbers.
- End with "Next review: [one sentence]"

PERIOD: {period}

KPIs:
{kpis}

NARRATIVE:
"""


def _fallback_narrative(period: str, kpis: dict, error: str | None = None) -> str:
    headcount = kpis.get("Headcount", "the current workforce")
    attrition = kpis.get("Attrition Rate", "the reported attrition rate")
    high_risk = kpis.get("High Risk Count", "the current high-risk cohort")
    engagement = kpis.get("Engagement Index", "the current engagement index")

    fallback_note = ""
    if error:
        fallback_note = " Local fallback narrative used because the configured Gemini model was unavailable."

    return (
        f"For {period}, headcount is {headcount}, attrition is {attrition}, and the engagement index is {engagement}. "
        f"The main people-risk signal is the high-risk employee cohort, currently reported as {high_risk}.{fallback_note}\n\n"
        "The priority is to focus retention activity on teams and tenure groups where risk is concentrated, rather than treating attrition as a broad organisation-wide issue.\n\n"
        "Recommended action: run targeted stay-interviews for high-risk employees and review workload, progression, and manager-support signals before the next reporting cycle. "
        "Next review: compare high-risk movement and attrition trend after the first retention intervention cycle."
    )


def generate_narrative(period: str, kpis: dict, root: Path) -> str:
    load_dotenv(root / ".env")

    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key or api_key.startswith("YOUR_"):
        return _fallback_narrative(period, kpis, error="GOOGLE_API_KEY missing")

    kpi_block = "\n".join(f"- {k}: {v}" for k, v in kpis.items())
    prompt = NARRATIVE_PROMPT.format(period=period, kpis=kpi_block)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return _fallback_narrative(period, kpis, error=str(e))
