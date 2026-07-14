"""
components/selectors.py - clean, no CSS hacks
"""
import streamlit as st
from components.tyre import tyre_svg, COMPOUND_COLOURS

DRIVERS   = ["VER", "HAM", "LEC", "SAI", "PER", "NOR", "ALO", "RUS", "STR", "PIA"]
COMPOUNDS = list(COMPOUND_COLOURS.keys())


def driver_selector() -> str:
    st.markdown('<p class="sec-label">01 · Select Driver</p>', unsafe_allow_html=True)
    return st.selectbox(
        "Driver", DRIVERS, index=1,
        key="driver_select", label_visibility="collapsed",
    )


def tyre_selector() -> str:
    st.markdown('<p class="sec-label" style="margin-top:1.5rem">02 · Tyre Compound</p>',
                unsafe_allow_html=True)

    if "compound" not in st.session_state:
        st.session_state["compound"] = "MEDIUM"

    selected = st.session_state["compound"]
    cols = st.columns(5)

    for col, compound in zip(cols, COMPOUNDS):
        with col:
            is_active = selected == compound
            st.markdown(
                f'<div style="text-align:center;opacity:{"1.0" if is_active else "0.4"};'
                f'transition:all 0.15s;margin-bottom:6px">'
                f'{tyre_svg(compound, size=68 if is_active else 56, active=is_active)}'
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
    """Kept for backwards compat — mode is now rendered in right panel."""
    return st.session_state.get("mode_radio", "Standard")