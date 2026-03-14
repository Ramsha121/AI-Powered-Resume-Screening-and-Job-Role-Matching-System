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
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------
# ENHANCED RED-BLACK GLASS UI
# ---------------------------------------------------
st.markdown("""
<style>
    /* MAIN BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1a0000, #050505, #000000);
        color: white;
    }

    /* TITLES: Balanced Size for Impact */
    .big-title {
        font-size: 85px !important;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff0000, #ff4d4d, #8b0000);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        letter-spacing: -2px;
    }

    .sub-title {
        font-size: 24px;
        text-align: center;
        color: #bbbbbb;
        margin-bottom: 40px;
        font-weight: 300;
    }

    /* GLASS CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 0, 0, 0.15);
        margin-bottom: 25px;
    }

    /* TYPOGRAPHY */
    h2, h3 {
        color: #ff4d4d !important;
        font-weight: 700 !important;
    }
    
    p, span, label, .stMarkdown {
        font-size: 18px !important;
        line-height: 1.6;
    }

    /* METRICS */
    [data-testid="stMetricValue"] {
        font-size: 50px !important;
        font-weight: 800 !important;
        color: #ff0000 !important;
    }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(45deg, #ff0000, #660000);
        color: white;
        font-size: 20px !important;
        font-weight: bold;
        border-radius: 12px;
        padding: 15px;
        width: 100%;
        border: none;
        transition: 0.4s;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 0, 0, 0.5);
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #080808;
        border-right: 1px solid #330000;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# APP LOGIC & SETUP
# ---------------------------------------------------
@st.cache_resource
def setup_nltk():
    nltk.download('punkt')
    nltk.download('stopwords')

setup_nltk()
stop_words = set(stopwords.words("english"))

skill_db = [
    "python","sql","tableau","power bi","machine learning","deep learning",
    "nlp","statistics","pandas","numpy","tensorflow","keras","pytorch",
    "aws","azure","scikit-learn","matplotlib","seaborn","excel"
]

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown('<p class="big-title">RESUME AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Advanced PDF Analysis & Skill Mapping</p>', unsafe_allow_html=True)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    st.title("🎯 Analysis Panel")
    target_role = st.selectbox("Compare against role:", 
                               ["Data Scientist", "Machine Learning Intern", "Data Analyst", "AI Engineer"])
    st.markdown("---")
    st.write("This tool uses Natural Language Processing to extract key competencies from your profile.")

# ---------------------------------------------------
# MAIN CONTENT
# ---------------------------------------------------
uploaded_file = st.file_uploader("Drop your Resume (PDF)", type=["pdf"])

def extract_content(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.lower()

if uploaded_file:
    # Processing
    resume_text = extract_content(uploaded_file)
    found_skills = [s for s in skill_db if s in resume_text]
    
    # Calculate mock scores based on text density
    skill_score = min(len(found_skills) * 12, 100)
    exp_matches = len(re.findall(r"(intern|experience|project|work)", resume_text))
    ats_score = min((skill_score * 0.6) + (exp_matches * 10) + 15, 100)

    # UI ROW 1: METRICS
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("ATS Match", f"{int(ats_score)}%")
    c2.metric("Skills Found", len(found_skills))
    c3.metric("Clarity", "High")
    st.markdown('</div>', unsafe_allow_html=True)

    # UI ROW 2: VISUALS
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Skill Analysis Gauge")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ats_score,
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "#ff0000"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [
                    {'range': [0, 50], 'color': '#220000'},
                    {'range': [50, 80], 'color': '#440000'}
                ]
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white", 'family': "sans-serif"}, height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🛠️ Expertise Tag Cloud")
        if found_skills:
            # Displaying skills as colored tags
            for s in found_skills:
                st.markdown(f"🚩 <span style='color:#ff8080; font-weight:bold;'>{s.upper()}</span>", unsafe_allow_html=True)
        else:
            st.write("No technical skills detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    # UI ROW 3: WORDCLOUD
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔍 Keyword Relevance")
    wc = WordCloud(width=1000, height=400, background_color=None, mode="RGBA", colormap="Reds").generate(resume_text)
    fig_wc, ax = plt.subplots(figsize=(10, 4), facecolor='none')
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig_wc)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("""
<div style="text-align:center; padding: 40px; color: #444; font-size: 14px;">
    SYSTEM STATUS: OPTIMIZED | THEME: NOIR RED | VERSION 2.1
</div>
""", unsafe_allow_html=True)
