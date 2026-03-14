import streamlit as st
import numpy as np
import nltk
import re
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from PyPDF2 import PdfReader
from wordcloud import WordCloud
from nltk.corpus import stopwords

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="ULTIMATE AI ANALYZER",
    page_icon="🔥",
    layout="wide"
)

# ---------------------------------------------------
# MASSIVE FONT & PREMIUM RED-BLACK THEME
# ---------------------------------------------------
st.markdown("""
<style>
    /* GLOBAL FONT SCALE */
    html, body, [class*="st-"] {
        font-size: 24px !important; /* Forces everything to be larger */
        font-family: 'Inter', sans-serif;
    }

    /* MAIN BACKGROUND */
    .stApp {
        background: radial-gradient(circle at center, #200000 0%, #050505 100%);
        color: #ffffff;
    }

    /* BETTER TITLE: CYBERPUNK STYLE */
    .mega-title {
        font-size: clamp(60px, 10vw, 150px) !important;
        font-weight: 900 !important;
        text-align: center;
        text-transform: uppercase;
        background: linear-gradient(180deg, #ff0000 0%, #8b0000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 0px;
        filter: drop-shadow(0px 5px 15px rgba(255, 0, 0, 0.4));
        letter-spacing: -5px;
    }

    .mega-subtitle {
        font-size: 32px !important;
        text-align: center;
        color: #ff4d4d;
        font-weight: 300;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 60px;
    }

    /* CARD SYSTEM */
    .glass-box {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 0, 0, 0.2);
        border-radius: 30px;
        padding: 40px;
        margin-bottom: 30px;
        transition: 0.3s;
    }
    .glass-box:hover {
        border-color: #ff0000;
        background: rgba(255, 0, 0, 0.05);
    }

    /* HEADERS */
    h2, h3 {
        font-size: 45px !important;
        color: #ff3333 !important;
        text-transform: uppercase;
        border-left: 8px solid #ff0000;
        padding-left: 20px;
    }

    /* METRICS */
    [data-testid="stMetricValue"] {
        font-size: 70px !important;
        font-weight: 900 !important;
        color: #ff0000 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 24px !important;
        color: #aaa !important;
    }

    /* BUTTONS */
    .stButton>button {
        font-size: 30px !important;
        font-weight: 900 !important;
        height: 80px !important;
        border-radius: 20px !important;
        background: #ff0000 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 30px rgba(255, 0, 0, 0.3) !important;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOGIC SETUP
# ---------------------------------------------------
@st.cache_resource
def init_nlp():
    nltk.download('punkt')
    nltk.download('stopwords')

init_nlp()
stop_words = set(stopwords.words("english"))

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown('<p class="mega-title">PRO ANALYZER</p>', unsafe_allow_html=True)
st.markdown('<p class="mega-subtitle">Neural Resume Intelligence</p>', unsafe_allow_html=True)

# ---------------------------------------------------
# APP CONTENT
# ---------------------------------------------------
uploaded_file = st.file_uploader("", type=["pdf"])

if uploaded_file:
    # 1. Extraction
    reader = PdfReader(uploaded_file)
    raw_text = " ".join([page.extract_text() for page in reader.pages]).lower()
    
    # 2. Logic (Simplified for demonstration)
    skills_db = ["python", "sql", "r", "tableau", "excel", "machine learning", "statistics", "ai"]
    found_skills = [s for s in skills_db if s in raw_text]
    score = min(len(found_skills) * 15 + 10, 100)

    # 3. Dashboard
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("RESUME STRENGTH", f"{score}%")
    with c2:
        st.metric("SKILLS DETECTED", len(found_skills))
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Detailed Breakdown
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown('<div class="glass-box">', unsafe_allow_html=True)
        st.subheader("🧠 PROFICIENCY GAUGE")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={
                'axis': {'range': [0, 100], 'tickfont': {'size': 20}},
                'bar': {'color': "#ff0000"},
                'bgcolor': "black",
                'steps': [{'range': [0, 50], 'color': '#300000'}]
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'size': 20})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="glass-box">', unsafe_allow_html=True)
        st.subheader("🎯 GAP ANALYSIS")
        st.write(f"**Target Role:** Data Analyst")
        missing = ["tableau", "excel"]
        for m in missing:
            st.markdown(f"🚀 <span style='color:#ff4d4d; font-size:30px; font-weight:bold;'>{m.upper()}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. Word Cloud
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.subheader("💡 KEYWORD CLOUD")
    wc = WordCloud(width=1000, height=400, background_color="black", colormap="Reds").generate(raw_text)
    fig_wc, ax = plt.subplots(figsize=(15, 7))
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig_wc)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("""
<div style="text-align:center; padding: 60px; font-size: 28px; color: #666; font-weight: bold;">
    MADE WITH ❤️ AND PYTHON 🐍
</div>
""", unsafe_allow_html=True)
