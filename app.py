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
    page_title="AI-Powered-Resume-Screening-and-Job-Role-Matching-System",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------
# THE ULTIMATE "BIGGER & BETTER" RED-BLACK THEME
# ---------------------------------------------------
st.markdown("""
<style>
/* GLOBAL FONT OVERRIDE - MAKES EVERYTHING LARGER */
html, body, [class*="st-"] {
    font-size: 30px !important;
    font-family: 'Inter', sans-serif;
}

/* MAIN BACKGROUND WITH DEPTH */
.stApp {
    background: radial-gradient(circle at center, #200000 0%, #050505 100%);
    color: white;
}

/* MASSIVE RESPONSIVE TITLE */
.big-title {
    font-size: clamp(60px, 12vw, 160px) !important;
    font-weight: 900 !important;
    text-align: center;
    background: linear-gradient(180deg, #ff0000 0%, #8b0000 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
    letter-spacing: -4px;
    filter: drop-shadow(0px 10px 20px rgba(255, 0, 0, 0.3));
    text-transform: uppercase;
}

/* ENHANCED SUBTITLE */
.sub-title {
    font-size: 36px !important;
    text-align: center;
    color: #ff4d4d;
    margin-bottom: 60px;
    font-weight: 300;
    text-transform: uppercase;
    letter-spacing: 4px;
}

/* GLASSMORPHISM CARDS */
.card {
    background: rgba(255, 255, 255, 0.05);
    padding: 40px;
    border-radius: 30px;
    margin-bottom: 35px;
    border: 2px solid rgba(255, 0, 0, 0.25);
    transition: 0.4s ease;
}
.card:hover {
    border-color: #ff0000;
    box-shadow: 0 0 40px rgba(255, 0, 0, 0.15);
}

/* HEADINGS */
h2 {
    font-size: 55px !important;
    color: #ff3333 !important;
    text-transform: uppercase;
    font-weight: 800 !important;
    border-left: 10px solid #ff0000;
    padding-left: 20px;
    margin-bottom: 30px !important;
}

/* METRICS & ALERTS */
[data-testid="stMetricValue"] {
    font-size: 80px !important;
    font-weight: 900 !important;
    color: #ff0000 !important;
}

[data-testid="stAlert"] {
    background-color: rgba(255, 0, 0, 0.1) !important;
    border: 1px solid #ff0000 !important;
    color: white !important;
    font-size: 30px !important;
}

/* BUTTON STYLE */
.stButton>button {
    background: linear-gradient(45deg, #ff0000, #4d0000) !important;
    color: white !important;
    font-size: 32px !important;
    font-weight: 900 !important;
    border-radius: 20px !important;
    height: 90px !important;
    width: 100% !important;
    border: none !important;
    box-shadow: 0 10px 30px rgba(255, 0, 0, 0.4) !important;
    transition: 0.3s ease;
}
.stButton>button:hover {
    transform: scale(1.02);
    box-shadow: 0 0 50px #ff0000 !important;
}

/* FOOTER */
.footer {
    width: 100%;
    text-align: center;
    padding: 50px;
    font-size: 24px;
    color: #888;
    background: rgba(0,0,0,0.5);
    border-top: 1px solid #300000;
    margin-top: 100px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE SECTION
# ---------------------------------------------------
st.markdown('<p class="big-title">AI ANALYZER</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Advanced Resume Intelligence</p>', unsafe_allow_html=True)

# ---------------------------------------------------
# NLTK DOWNLOAD (SAME LOGIC)
# ---------------------------------------------------
try:
    nltk.data.find("tokenizers/punkt")
except:
    nltk.download("punkt")
try:
    nltk.data.find("corpora/stopwords")
except:
    nltk.download("stopwords")

stop_words = set(stopwords.words("english"))

# ---------------------------------------------------
# DATA & FUNCTIONS (STRICTLY UNCHANGED)
# ---------------------------------------------------
skill_dictionary = [
    "python","r","sql","excel","tableau","power bi","machine learning","deep learning","ai","nlp",
    "statistics","data analysis","pandas","numpy","matplotlib","seaborn","tensorflow","keras",
    "pytorch","big data","hadoop","spark","mongodb","postgresql","mysql","dashboard","analytics","classification","regression"
]

required_skills = {
    "Data Analyst":["python","sql","tableau","statistics","excel"],
    "Machine Learning Intern":["python","machine learning","pandas","numpy","deep learning"],
    "AI Intern":["python","deep learning","nlp","tensorflow","pytorch"],
    "Business Analyst":["sql","excel","dashboard","tableau","communication"]
}

def extract_text(file):
    reader = PdfReader(file)
    text=""
    for page in reader.pages:
        t = page.extract_text()
        if t: text += t
    return text.lower()

def extract_skills(text):
    found=[]
    for skill in skill_dictionary:
        if skill in text: found.append(skill)
    return list(set(found))

def score_section(text, keywords):
    count=0
    for k in keywords:
        if k in text: count+=1
    return round((count/len(keywords))*10, 2)

def ats_score(skill,exp,edu,culture):
    ats=(skill*3)+(exp*3)+(edu*2)+(culture*2)
    return round(min(ats,100),2)

def generate_wordcloud(text):
    wc=WordCloud(width=1000, height=500, background_color="black", colormap="Reds", stopwords=stop_words).generate(text)
    fig,ax=plt.subplots(facecolor='black')
    ax.imshow(wc)
    ax.axis("off")
    return fig

def role_matching(text):
    roles={
        "Data Analyst":["python","sql","statistics","tableau"],
        "Machine Learning Intern":["python","machine learning","pandas","numpy"],
        "AI Intern":["python","deep learning","nlp"],
        "Business Analyst":["sql","excel","dashboard"]
    }
    scores={}
    for role in roles:
        score=0
        for skill in roles[role]:
            if skill in text: score+=1
        scores[role]=score*25
    return scores

def detect_skill_gap(text,role):
    required=required_skills[role]
    missing=[]
    for s in required:
        if s not in text: missing.append(s)
    return missing

# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------
uploaded_file = st.file_uploader("", type=["pdf"])

# ---------------------------------------------------
# ANALYZE BUTTON & RESULTS
# ---------------------------------------------------
if uploaded_file:
    if st.button("🚀 INITIATE ANALYSIS"):
        resume_text = extract_text(uploaded_file)

        # SKILLS CARD
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 EXTRACTED SKILLS")
        skills = extract_skills(resume_text)
        st.success(", ".join(skills).upper())
        st.markdown('</div>', unsafe_allow_html=True)

        # DATA CALCULATION
        skill_score = score_section(resume_text, skill_dictionary)
        exp_score = score_section(resume_text, ["intern","project","experience","research"])
        edu_score = score_section(resume_text, ["bsc","msc","phd","bachelor"])
        culture_score = score_section(resume_text, ["team","leadership","communication"])
        ats = ats_score(skill_score, exp_score, edu_score, culture_score)

        # ATS SCORE GAUGE
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 ATS SYSTEM SCORE")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ats,
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "white"},
                'bar': {'color': "#ff0000"},
                'bgcolor': "black",
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 90}
            }
        ))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'size': 20})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # WORD CLOUD
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💡 KEYWORD DENSITY")
        wc_fig = generate_wordcloud(resume_text)
        st.pyplot(wc_fig)
        st.markdown('</div>', unsafe_allow_html=True)

        # ROLE MATCHING
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🎯 ROLE COMPATIBILITY")
        scores = role_matching(resume_text)
        fig2 = px.bar(
            x=list(scores.keys()), y=list(scores.values()),
            color=list(scores.values()), color_continuous_scale="Reds"
        )
        fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'size': 18})
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # SKILL GAP
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📉 SKILL GAP ANALYSIS")
        top_role = max(scores, key=scores.get)
        st.info(f"Target Role: {top_role}")
        missing = detect_skill_gap(resume_text, top_role)
        if not missing:
            st.success("CRITICAL MATCH: ALL SKILLS PRESENT")
        else:
            st.write("### SKILL GAPS:")
            for m in missing:
                st.markdown(f"🚩 <span style='color:#ff4d4d; font-size:35px; font-weight:bold;'>{m.upper()}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("""
<div class="footer">
    MADE WITH ❤️ AND PYTHON 🐍 | 🔗 LinkedIn: YOUR-LINK
</div>
""", unsafe_allow_html=True)
