
import streamlit as st


# HERO SECTION
def hero():
    st.markdown(
        """
        <div class = "hero">
                <div>
                    <p class = "hero-title"><span>Box Box</span> · F1 Strategy</p>
                    <p class = "hero-sub">Pit Stop Optimizer · 2023 Season</p>
                </div>
                <div class = "hero-badge">ML-powered Strategy</div>
        </div>
        
        """, unsafe_allow_html = True 
        
    )
    
# FOOTER SECTION
def footer():
    st.markdown("""
            <div class = "footer">
            Box Box · F1 Strategy Optimizer · Built with XGBoost + FastAPI + Streamlit
            </div>
            """,
            unsafe_allow_html = True)
    