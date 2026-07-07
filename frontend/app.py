import streamlit as st
import requests
import json

from components.tyre import tyre_svg


# PAGE CONFIG 
st.set_page_config(
    page_title = "Box Box · F1 Strategy",
    page_icon =  "🏎️",
    layout = "wide",
    initial_sidebar_state = "collapsed",
)


# load CSS
with open("frontend/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# HERO SECTION
st.markdown("""
             <div class = "hero">
                <div>
                    <p class = "hero-title"><span>Box Box</span> · F1 Strategy</p>
                    <p class = "hero-sub">Pit Stop Optimizer · 2023 Season</p>
                </div>
                <div class = "hero-badge">ML-powered Strategy</div>
            </div>
           """, unsafe_allow_html = True)


st.components.v1.html(
    tyre_svg("SOFT"),
    height=150,
    width=150
)


# FOOTER 
st.markdown("""
            <div class = "footer">
            Box Box · F1 Strategy Optimizer · Built with XGBoost + FastAPI + Streamlit
            </div>
            """,
            unsafe_allow_html = True)