"""
components/inputs.py
=====================
Race situation and tyre performance inputs.
All native Streamlit — sliders and number inputs.
"""
import streamlit as st


def race_inputs() -> dict:
    """Race situation sliders."""
    st.markdown(
        '<p class="sec-label" style="margin-top:1.5rem">03 · Race Situation</p>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        lap_number     = st.slider("Lap Number",      1, 78, 34, key="lap_number")
        laps_remaining = st.slider("Laps Remaining",  0, 78, 24, key="laps_remaining")
        stint          = st.slider("Stint Number",    1,  4,  2, key="stint")
    with col2:
        position   = st.slider("Current Position", 1, 20,  3, key="position")
        total_laps = st.slider("Total Race Laps", 44, 78, 58, key="total_laps")

    return {
        "lap_number":     int(lap_number),
        "position":       int(position),
        "laps_remaining": int(laps_remaining),
        "stint":          int(stint),
        "total_laps":     int(total_laps),
    }


def performance_inputs() -> dict:
    """Tyre performance number inputs."""
    st.markdown(
        '<p class="sec-label" style="margin-top:1.5rem">04 · Tyre Performance</p>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        tyre_life = st.slider("Tyre Age (laps)", 0, 56, 21, key="tyre_life")
        lap_delta = st.number_input(
            "Lap Δ vs previous (s)",
            value=0.90, step=0.10, format="%.2f", key="lap_delta",
        )
    with col2:
        degradation = st.number_input(
            "Degradation from stint start (s)",
            value=2.30, step=0.10, format="%.2f", key="degradation",
        )
        rolling_avg = st.number_input(
            "Rolling avg lap time (s)",
            value=92.50, step=0.50, format="%.1f", key="rolling_avg",
        )

    return {
        "tyre_life":                    int(tyre_life),
        "lap_time_delta":               float(lap_delta),
        "degradation_from_stint_start": float(degradation),
        "lap_time_rolling3":            float(rolling_avg),
    }