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
    page_title="AI Resume Intelligence",
    page_icon="🎯",
    layout="wide"
)

# ---------------------------------------------------
# ULTIMATE NOIR-RED THEME
# ---------------------------------------------------
st.markdown("""
<style>
    /* Animated Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0a0000 0%, #1a0000 50%, #000000 100%);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #ffffff;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Containers */
    .main-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 40px;
        border: 1px solid rgba(255, 77, 77, 0.1);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 30px;
    }

    /* Typography */
    .hero-title {
        font-size: clamp(50px, 8vw, 100px);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to right, #ff4d4d, #8b0000);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        filter: drop-shadow(0 5px 15px rgba(255, 0, 0, 0.2));
    }

    .stat-label {
        font-size: 16px;
        color: #ff8080;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }

    /* Metric Enhancement */
    [data-testid="stMetric"] {
        background: rgba(255, 0, 0, 0.05);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #ff4d4d;
    }

    /* Custom File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(255, 77, 77, 0.3);
        padding: 20px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.01);
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 60px;
        background: linear-gradient(45deg, #ff0000, #4d0000);
        border: none;
        color: white;
        font-weight: 800;
        font-size: 20px;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(255, 0, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# PRE-FLIGHT CHECKS
# ---------------------------------------------------
@st.cache_resource
def load_nlp():
    nltk.download('punkt')
    nltk.download('stopwords')

load_nlp()
STOPWORDS = set(stopwords.words("english"))

SKILL_CATALOGUE = [
    "python","r","sql","tableau","power bi", "machine learning","deep learning","ai","nlp",
    "statistics","data analysis","pandas","numpy","matplotlib","seaborn","tensorflow","keras",
    "pytorch","big data","hadoop","spark","mongodb","postgresql","mysql","dashboard","analytics"
]

# ---------------------------------------------------
# DASHBOARD LOGIC
# ---------------------------------------------------
def process_pdf(file):
    reader = PdfReader(file)
    content = ""
    for page in reader.pages:
        content += page.extract_text() or ""
    return content.lower()

def analyze_resume(text):
    found = [s for s in SKILL_CATALOGUE if s in text]
    score = min(len(found) * 15, 100)
    return list(set(found)), score

# ---------------------------------------------------
# LAYOUT
# ---------------------------------------------------
st.markdown('<p class="hero-title">INSIGHT ENGINE</p>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666; font-size:20px; margin-bottom:40px;'>Empowering Careers with Neural Intelligence</p>", unsafe_allow_html=True)

# Main Interaction Area
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    file = st.file_uploader("DROP RESUME PDF HERE", type=["pdf"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if file:
    text_data = process_pdf(file)
    skills, match_pct = analyze_resume(text_data)

    # TOP METRICS ROW
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("MATCH RATE", f"{match_pct}%")
    with m2: st.metric("SKILLS", len(skills))
    with m3: st.metric("PAGES", len(PdfReader(file).pages))
    with m4: st.metric("COMPLEXITY", "Optimal" if match_pct > 70 else "Basic")

    st.write("")

    # ANALYTICS DASHBOARD
    col_a, col_b = st.columns([1, 1.2])

    with col_a:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🎯 Neural Proficiency Gauge")
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=match_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#ff0000"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#444",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(255, 0, 0, 0.1)'},
                    {'range': [50, 80], 'color': 'rgba(255, 0, 0, 0.2)'}
                ],
            }
        ))
        gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "Arial"}, height=300)
        st.plotly_chart(gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("🚀 Competency Mapping")
        if skills:
            # Create a nice badge layout
            badge_html = "".join([f'<span style="background:rgba(255,0,0,0.2); color:#ff4d4d; border:1px solid #ff4d4d; padding:5px 15px; border-radius:50px; margin:5px; display:inline-block; font-weight:bold;">{s.upper()}</span>' for s in skills])
            st.markdown(badge_html, unsafe_allow_html=True)
        else:
            st.error("NO TECHNICAL COMPETENCIES DETECTED.")
        st.markdown('</div>', unsafe_allow_html=True)

    # BOTTOM ROW: WORDCLOUD
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("☁️ Semantic Word Density")
    wc = WordCloud(
        width=1200, 
        height=400, 
        background_color=None, 
        mode="RGBA", 
        colormap="Reds", 
        font_path=None # Can add custom font path here
    ).generate(text_data)
    
    fig, ax = plt.subplots(figsize=(15, 5), facecolor='none')
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("""
<div style="text-align:center; padding: 50px; opacity: 0.4;">
    DESIGNED BY AI | STREAMLIT CLOUD DEPLOYED | 2026
</div>
""", unsafe_allow_html=True)
