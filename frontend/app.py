"""
frontend/app.py — Entry point
Run: streamlit run frontend/app.py
"""
from pathlib import Path
import requests
import streamlit as st

from components.selectors import driver_selector, tyre_selector, mode_selector
from components.inputs import race_inputs, performance_inputs
from components.cards import recommendation_card, empty_card, error_card

API_URL = "http://localhost:8000"


def page_config():
    st.set_page_config(
        page_title="Box Box · F1 Strategy",
        page_icon="🏎️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_css():
    css_path = Path(__file__).parent / "style.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <div class="hero">
        <div>
            <div class="hero-title"><span>Box Box</span> · F1 Strategy</div>
            <div class="hero-sub">Pit Stop Optimizer · 2023 Season</div>
        </div>
        <div class="hero-badge">ML-Powered Strategy</div>
    </div>""", unsafe_allow_html=True)


def render_left_panel() -> tuple:
    driver   = driver_selector()
    compound = tyre_selector()
    race     = race_inputs()
    perf     = performance_inputs()
    mode     = mode_selector()
    predict  = st.button("GET STRATEGY RECOMMENDATION", type="primary", use_container_width=True)

    payload = {
        "driver":                       driver,
        "compound":                     compound,
        "lap_number":                   race["lap_number"],
        "position":                     race["position"],
        "laps_remaining":               race["laps_remaining"],
        "stint":                        race["stint"],
        "total_laps":                   race["total_laps"],
        "tyre_life":                    perf["tyre_life"],
        "lap_time_delta":               perf["lap_time_delta"],
        "degradation_from_stint_start": perf["degradation_from_stint_start"],
        "lap_time_rolling3":            perf["lap_time_rolling3"],
    }
    return payload, mode, predict


def render_right_panel(payload, mode, predict_clicked):
    st.markdown('<p class="sec-label">Strategy Output</p>', unsafe_allow_html=True)

    if not predict_clicked:
        empty_card()
        return

    try:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        if r.status_code == 200:
            rec = r.json()
            rec["position"] = payload["position"]
            recommendation_card(rec, mode)
        else:
            error_card(f"API error {r.status_code}: {r.text}")
    except requests.exceptions.ConnectionError:
        error_card(
            "Cannot connect to API.<br><br>"
            "<code style='color:#ff9f43'>uvicorn src.api.main:app --reload --port 8000</code>"
        )
    except Exception as e:
        error_card(f"Error: {str(e)}")


def main():
    page_config()
    inject_css()
    render_hero()

    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    left, _, right = st.columns([1.1, 0.08, 0.92])

    with left:
        payload, mode, predict_clicked = render_left_panel()
    with right:
        render_right_panel(payload, mode, predict_clicked)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        Box Box · F1 Strategy Optimizer · XGBoost + FastAPI + Streamlit
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()