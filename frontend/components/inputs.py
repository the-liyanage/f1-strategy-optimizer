"""
components/inputs.py
=====================
Race situation and tyre performance inputs.

FIX: number input labels were showing in red because Streamlit's default
CSS was overriding our muted colour. Fixed by wrapping each number input
in a div with a custom class and using more specific CSS selectors.
"""

import streamlit as st


def race_inputs() -> dict:
    """
    Sliders for the current race situation.

    Returns:
        dict: lap_number, position, laps_remaining, stint, total_laps
    """
    st.markdown(
        '<p class="sec-label" style="margin-top:1.5rem">03 · Race Situation</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        lap_number = st.slider(
            "Lap Number",
            min_value=1, max_value=78, value=34, key="lap_number",
        )
        laps_remaining = st.slider(
            "Laps Remaining",
            min_value=0, max_value=78, value=24, key="laps_remaining",
        )
        stint = st.slider(
            "Stint Number",
            min_value=1, max_value=4, value=2, key="stint",
        )

    with col2:
        position = st.slider(
            "Current Position",
            min_value=1, max_value=20, value=3, key="position",
        )
        total_laps = st.slider(
            "Total Race Laps",
            min_value=44, max_value=78, value=58, key="total_laps",
        )

    return {
        "lap_number":     int(lap_number),
        "position":       int(position),
        "laps_remaining": int(laps_remaining),
        "stint":          int(stint),
        "total_laps":     int(total_laps),
    }


def performance_inputs() -> dict:
    """
    Number inputs for tyre performance metrics.

    FIX: labels are now plain text rendered as markdown ABOVE
    each number input (label_visibility="collapsed" on the input itself).
    This gives us full control over label styling without fighting
    Streamlit's internal CSS.

    Returns:
        dict: tyre_life, lap_time_delta, degradation_from_stint_start,
              lap_time_rolling3
    """
    st.markdown(
        '<p class="sec-label" style="margin-top:1.5rem">04 · Tyre Performance</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        tyre_life = st.slider(
            "Tyre Age (laps)",
            min_value=0, max_value=56, value=21, key="tyre_life",
        )

        # Custom label rendered as markdown — avoids Streamlit red label bug
        st.markdown('<p class="input-label">Lap Δ vs previous (s)</p>',
                    unsafe_allow_html=True)
        lap_delta = st.number_input(
            "Lap Δ vs previous (s)",
            value=0.90, step=0.10, format="%.2f",
            key="lap_delta",
            label_visibility="collapsed",
        )

    with col2:
        st.markdown('<p class="input-label">Degradation from stint start (s)</p>',
                    unsafe_allow_html=True)
        degradation = st.number_input(
            "Degradation from stint start (s)",
            value=2.30, step=0.10, format="%.2f",
            key="degradation",
            label_visibility="collapsed",
        )

        st.markdown('<p class="input-label">Rolling avg lap time (s)</p>',
                    unsafe_allow_html=True)
        rolling_avg = st.number_input(
            "Rolling avg lap time (s)",
            value=92.50, step=0.50, format="%.1f",
            key="rolling_avg",
            label_visibility="collapsed",
        )

    return {
        "tyre_life":                    int(tyre_life),
        "lap_time_delta":               float(lap_delta),
        "degradation_from_stint_start": float(degradation),
        "lap_time_rolling3":            float(rolling_avg),
    }
    