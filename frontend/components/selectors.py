# selectors return a CHOICE from a fixed set of options
        # which driver, which compound, which mode
# inputs return a NUMBER the user configures 
        # lap count, tyre age, degradation





import streamlit as st
from components.tyre import tyre_svg, COMPOUND_COLOURS


DRIVERS = ["VER", "HAM", "LEC", "SAI", "PER", "NOR", "ALO", "RUS", "STR", "PIA"]

COMPOUNDS = list(COMPOUND_COLOURS.keys()) # this preserves order

def on_driver_change():
    """Callback to instantly sync selectbox state to the custom chip state"""
    st.session_state["driver"] = st.session_state["driver_select"]

def driver_selector()-> str:
    st.markdown(
        '<p class="sec-label">01 · Select Driver</p>',
        unsafe_allow_html=True
        )
    # read current selection from session state
    current = st.session_state.get("driver", "HAM")
    
    # Decorative chip row
    chips_html = '<div class = "driver-grid">'
    
    for driver in DRIVERS:
        active_class = "active" if driver == current else ""
        chips_html += f'<span class = "driver-chip{active_class}">{driver}</span>'
    chips_html += "</div>"
    st.markdown(chips_html, unsafe_allow_html = True)
        
    
     # Functional selectbox — the actual control that updates state
    chosen = st.selectbox(
        "Driver",
        DRIVERS,
        index=DRIVERS.index(current),
        label_visibility="collapsed",
        key="driver_select",
        on_change=on_driver_change
    )
    
    return chosen



def tyre_selector() -> str:
    """
    renders PIRELLI tyre SVGs as a compound selector.
    
    each compound gets its own column with:
        - the tyre SVG
        - the compound short name below it
        - the hidden Streamlit button that handles the click
    """
    
    st.markdown(
        '<p class="sec-label" style="margin-top:1.5rem">02 · Tyre Compound</p>',
        unsafe_allow_html=True)
    
    
    
    # 1. Fetch current state at the start
    selected_compound = st.session_state.get("compound", "MEDIUM")
    cols = st.columns(len(COMPOUNDS))
    
    for col, compound in zip(cols, COMPOUNDS):
        with col:
            is_active = selected_compound == compound
            active_class = "active" if is_active else ""
 
            # Render the custom visual wrapper
            st.markdown(
                f'<div class="tyre-item {active_class}">'
                f'{tyre_svg(compound, size=48, active=is_active)}'
                f'<span class = "tyre-lbl">{compound[:3]}</span>'
                f'</div>',
                unsafe_allow_html=True
                )
 
            # functional button
            
            if st.button(
                compound[:3], 
                key=f"cmp_{compound}",
                help=f"Select {compound}",
            ):
                st.session_state["compound"] = compound
                st.rerun()
            
            
    # 3. Return the exact state we read at the beginning (callbacks ensure accuracy on rerun)
    return st.session_state.get("compound", "MEDIUM")