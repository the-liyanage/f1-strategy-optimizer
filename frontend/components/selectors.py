import streamlit as st
from components.tyre import tyre_svg
def driver_selector():
    st.markdown(
        '<p class = "section-label"01 · Select Driver</p>', unsafe_allow_html = True)
    
    drivers = [
        "VER", "HAM", "LEC",
        "SAI", "PER", "NOR", "ALO",
        "RUS", "STR", "PIA"
    ]
    
    selected_driver = st.selectbox(
        "Driver",
        drivers,
        label_visibility = "collapsed",
    )
    return selected_driver
    
    
def tyre_selector():
    st.markdown(
        '<p class = "section-label" style = "margin-top: 1.5rem">02 · Tyre Compound</p>', unsafe_allow_html = True)
    
    compounds = ["SOFT",
                 "MEDIUM",
                 "HARD",
                 "INTERMEDIATE",
                 "WET"]
    
    # render tyres as visual buttons using columns
    tyre_cols = st.columns(5)
    selected_compound = st.session_state.get("compound", "MEDIUM")
    
    for i, (col, compound) in enumerate(zip(tyre_cols, compounds)):
        with col:
            is_active = selected_compound == compound
            active_class = "active" if is_active else ""
 
            st.markdown(f"""
            <div class="tyre-option {active_class}"
                 onclick="void(0)"
                 style="{'opacity:1;transform:scale(1.1)' if is_active else ''}">
                {tyre_svg(compound, size=52, active=is_active)}
                <span class="tyre-label">{compound[:3]}</span>
            </div>
            """, unsafe_allow_html=True)
 
            # actual clickable button (invisible, overlapping)
            if st.button(compound[:3], key=f"tyre_{compound}",
                         help=f"Select {compound}"):
                st.session_state["compound"] = compound
                st.rerun()
    selected_compound = st.session_state.get("compound", "MEDIUM")
    return selected_compound
  
    