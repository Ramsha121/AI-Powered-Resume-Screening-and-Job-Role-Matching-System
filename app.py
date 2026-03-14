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
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------
# RED-BLACK DARK THEME + OPTIMIZED FONTS
# ---------------------------------------------------
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp{
background: radial-gradient(circle at center, #200000 0%, #050505 100%);
color:white;
font-size:24px !important;
}

/* REDUCED TITLE SIZE - CLEANER & MORE BALANCED */
.big-title{
font-size: clamp(40px, 6vw, 80px) !important;
font-weight: 900 !important;
text-align: center !important;
background: linear-gradient(180deg, #ff0000 0%, #8b0000 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
margin-bottom: 10px !important;
letter-spacing: -1px !important;
filter: drop-shadow(0px 5px 10px rgba(255, 0, 0, 0.3));
}

/* SUBTITLE */
.sub-title{
font-size: 32px !important;
text-align: center !important;
color: #ff4d4d !important;
margin-bottom: 40px !important;
font-weight: 300 !important;
}

/* SECTION CARDS */
.card{
background: rgba(255,255,255,0.03);
padding: 30px !important;
border-radius: 20px !important;
margin-bottom: 30px !important;
border: 1px solid rgba(255,0,0,0.2);
}

/* HEADINGS */
h2{
font-size: 45px !important;
color: #ff4d4d !important;
font-weight: 800 !important;
}
h3{
font-size: 36px !important;
color: #ff8080 !important;
}

/* TEXT */
p, span, label, li { 
font-size: 24px !important;
}

/* BUTTON STYLE */
.stButton>button{
background: linear-gradient(45deg,#ff0000,#8b0000);
color: white !important;
font-size: 28px !important;
font-weight: bold !important;
border-radius: 15px !important;
height: 70px !important;
width: 100% !important;
border: none !important;
transition: 0.3s !important;
box-shadow: 0 4px 15px rgba(255,0,0,0.3);
}
.stButton>button:hover{
transform: scale(1.02) !important;
box-shadow: 0px 0px 25px red !important;
}

/* FOOTER */
.footer{
width: 100%;
text-align: center;
padding: 30px !important;
font-size: 22px !important;
color: #888 !important;
border-top: 1px solid #300000 !important;
margin-top: 50px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.markdown('<p class="big-title">AI-Powered Resume Insights </p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload your resume and get AI powered insights</p>', unsafe_allow_html=True)
st.write("")

# ---------------------------------------------------
# NLTK DOWNLOAD
# ---------------------------------------------------
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download("punkt")
        nltk.download("stopwords")
    except:
        pass

download_nltk_data()
stop_words = set(stopwords.words("english"))

# ---------------------------------------------------
# DATA & DICTIONARIES
# ---------------------------------------------------
skill_dictionary = [
"python","r","sql","excel","tableau","power bi","machine learning","deep learning","ai","nlp",
"statistics","data analysis","pandas","numpy","matplotlib","seaborn","tensorflow","keras",
"pytorch","big data","hadoop","spark","mongodb","postgresql","mysql","dashboard","analytics",
"classification","regression"
]

required_skills = {
"Data Analyst":["python","sql","tableau","statistics","excel"],
"Machine Learning Intern":["python","machine learning","pandas","numpy","deep learning"],
"AI Intern":["python","deep learning","nlp","tensorflow","pytorch"],
"Business Analyst":["sql","excel","dashboard","tableau","communication"]
}

role_links = {
"Data Analyst": "https://www.linkedin.com/jobs/data-analyst-jobs/",
"Machine Learning Intern": "https://www.linkedin.com/jobs/machine-learning-intern-jobs/",
"AI Intern": "https://www.linkedin.com/jobs/ai-intern-jobs/",
"Business Analyst": "https://www.linkedin.com/jobs/business-analyst-jobs/"
}

# ---------------------------------------------------
# LOGIC FUNCTIONS (STRICTLY UNCHANGED)
# ---------------------------------------------------
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
    wc=WordCloud(width=900, height=500, background_color="black", colormap="Reds", stopwords=stop_words).generate(text)
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
# FILE UPLOAD & INTERFACE
# ---------------------------------------------------
uploaded_file = st.file_uploader("📄 Upload Resume PDF", type=["pdf"])

if uploaded_file:
    if st.button("🚀 INITIATE ANALYSIS"):
        resume_text = extract_text(uploaded_file)

        # SKILLS CARD
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 Extracted Skills")
        skills = extract_skills(resume_text)
        st.success(", ".join(skills).upper())
        st.markdown('</div>', unsafe_allow_html=True)

        # SCORING
        skill_score = score_section(resume_text, skill_dictionary)
        exp_score = score_section(resume_text, ["intern","project","experience","research"])
        edu_score = score_section(resume_text, ["bsc","msc","phd","bachelor"])
        culture_score = score_section(resume_text, ["team","leadership","communication"])
        ats = ats_score(skill_score, exp_score, edu_score, culture_score)

        # ATS GAUGE
        st.subheader("📊 ATS Resume Score")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ats,
            gauge={'axis':{'range':[0,100], 'tickcolor':"white"}, 'bar':{'color':"red"}, 'bgcolor':"black"}
        ))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', font={'size':18})
        st.plotly_chart(fig, use_container_width=True)

        # WORD CLOUD
        st.subheader("💡 Resume Word Cloud")
        wc = generate_wordcloud(resume_text)
        st.pyplot(wc)

        # ROLE MATCHING
        st.subheader("🎯 Best Job Role Match")
        scores = role_matching(resume_text)
        for role, score in scores.items():
            link = role_links.get(role, "#")
            st.markdown(f"🚩 **{role}** → Match: {score}% → [Search Jobs]({link})")

        top_role = max(scores, key=scores.get)
        st.info(f"Recommended Focus: **{top_role}**")

        # SKILL GAP
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📉 Skill Gap Analysis")
        missing = detect_skill_gap(resume_text, top_role)
        if not missing:
            st.success("Perfect Match for this role!")
        else:
            st.write("Skills to improve for your top match:")
            for m in missing:
                st.markdown(f"- <span style='color:#ff4d4d; font-weight:bold;'>{m.upper()}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown(f"""
<div class="footer">
    Made with ❤️ and Python 🐍 | 🔗 LinkedIn: <a href="https://www.linkedin.com/in/ramsha-khan-582522291" style="color:#ff4d4d">Ramsha Khan</a>
</div>
""", unsafe_allow_html=True)
