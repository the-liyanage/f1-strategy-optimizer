from pathlib import Path

import streamlit as st
import requests
import json


from components.selectors import driver_selector, tyre_selector
from components.inputs import race_inputs
from components.layout import hero, footer

API_URL = "http://localhost:8000"

# PAGE CONFIG 
def page_config():
    st.set_page_config(
        page_title = "Box Box · F1 Strategy",
        page_icon =  "🏎️",
        layout = "wide",
        initial_sidebar_state = "collapsed",
)


def inject_css():
    css_path = Path(__file__).parent / "style.css"
    with open(css_path) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html = True)
    
def render_hero():
    hero_banner = hero()
       
def render_left_panel() -> tuple:
    driver = driver_selector()
    compound = tyre_selector()
    race = race_inputs()
    
    return driver, compound, race

def render_footer():
    footer_panel = footer()
    
      
def main():
    page_config()
    inject_css()
    
    render_hero()
    
    st.markdown('<div class = "main-wrap">', unsafe_allow_html = True)
    
    
    left, _, right = st.columns([1.1, 0.08, 0.92])
    
    with left:
        driver, compound, race =render_left_panel()
    st.markdown('</div>', unsafe_allow_html=True)
    
    render_footer()
if __name__ == "__main__":
    main()