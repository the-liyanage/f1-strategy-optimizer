"""
components/selectors.py
========================
Driver, tyre compound, and mode selectors.
Uses native Streamlit components only — no CSS hacks.
"""
import streamlit as st
from components.tyre import tyre_svg, COMPOUND_COLOURS

DRIVERS   = ["VER", "HAM", "LEC", "SAI", "PER", "NOR", "ALO", "RUS", "STR", "PIA"]
COMPOUNDS = list(COMPOUND_COLOURS.keys())
MODES     = ["Standard", "Toto Mode", "Ferrari Mode", "Engineer Radio"]


def driver_selector() -> str:
    """
    Driver selector using st.selectbox.
    Simple and reliable — shows current driver in a dropdown.
    """
    st.markdown('<p class="sec-label">01 · Select Driver</p>', unsafe_allow_html=True)
    driver = st.selectbox(
        "Driver",
        DRIVERS,
        index=1,
        key="driver_select",
        label_visibility="collapsed",
    )
    return driver


def tyre_selector() -> str:
    """
    Tyre selector — real Streamlit buttons with SVG tyres above each one.
    No CSS hacks. Each button stores selection in session_state.
    """
    st.markdown(
        '<p class="sec-label" style="margin-top:1.5rem">02 · Tyre Compound</p>',
        unsafe_allow_html=True,
    )

    if "compound" not in st.session_state:
        st.session_state["compound"] = "MEDIUM"

    selected = st.session_state["compound"]
    cols = st.columns(5)

    for col, compound in zip(cols, COMPOUNDS):
        with col:
            is_active = selected == compound
            size = 72 if is_active else 60
            st.markdown(
                f'<div style="text-align:center;opacity:{"1" if is_active else "0.45"};'
                f'margin-bottom:6px">'
                f'{tyre_svg(compound, size=size, active=is_active)}'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(
                compound[:3],
                key=f"cmp_{compound}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state["compound"] = compound
                st.rerun()

    return st.session_state.get("compound", "MEDIUM")


def mode_selector() -> str:
    """
    Mode selector — native Streamlit horizontal radio.
    """
    st.markdown(
        '<p class="sec-label" style="margin-top:1.5rem">05 · Strategy Mode</p>',
        unsafe_allow_html=True,
    )
    return st.radio(
        "Strategy mode",
        MODES,
        horizontal=True,
        label_visibility="collapsed",
        key="mode_radio",
    )