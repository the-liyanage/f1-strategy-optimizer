import streamlit as st

def race_inputs():
    st.markdown(
        '<p class ="section-label" style = "margin-top:1.8rem">03 · Race Situation</p>', unsafe_allow_html = "True")
    
    col1, col2 = st.columns(2)
    with col1:
        tyre_life = st.slider("Tyre Age laps", 0, 56, 21)
        position = st.slider("Current Position", 1, 20, 3)
        stint = st.slider("Stint Number", 1, 4, 2)
    return tyre_life, position, stint 