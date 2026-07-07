# TWO COLUMN LAYOUT 
import streamlit as st

left, spacer, right = st.columns([1.1, 0.1, 0.9])
with left:
    # ----------- Driver selector ------------
    
    
    
    # ----------- Compound selector --------------
    st.markdown(
        '<p class ="selection-label" style = "margun-top:1.5rem">02 · Tyre Compound</p>',
        unsafe_allow_html = True
    )
    compounds = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
    
    # render tyres as visual buttons using columns
    tyre_cols = st.columns(5)
    selected_compound = st.session_state.get("compound", "MEDIUM")