import streamlit as st
import requests
import json

from components.tyre import tyre_svg
from components.layout import hero, footer


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
st.components.v1.html(
    hero()
    )



# TYRE SECTION
st.components.v1.html(
    tyre_svg("SOFT"),
    )


# FOOTER 
st.components.v1.html(
    footer()
    )