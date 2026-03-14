import streamlit as st
import numpy as np
import re
import nltk
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from wordcloud import WordCloud
from PIL import Image
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide"
)


# -------------------------------------------------
# DARK THEME CSS
# -------------------------------------------------

st.markdown(
"""
<style>

.stApp {
    background-color: #0e1117;
    color: white;
}

h1, h2, h3, h4 {
    color: #00F5D4;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #0e1117;
color: white;
text-align: center;
padding: 10px;
font-size: 14px;
}

</style>
""",
unsafe_allow_html=True
)

st.title("🤖 AI Resume Analyzer Dashboard")
st.write("Upload your resume and get AI-powered insights")



# -------------------------------------------------
# NLTK DOWNLOAD
# -------------------------------------------------

try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except:
    nltk.download('stopwords')


stop_words = set(stopwords.words('english'))


# -------------------------------------------------
# TEXT EXTRACTION
# -------------------------------------------------

def extract_resume_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        t = page.extract_text()

        if t:
            text += t

    return text.lower()


def clean_text(text):

    text = re.sub(r'\s+', ' ', text)

    return text


# -------------------------------------------------
# SKILL DICTIONARY
# -------------------------------------------------

skill_dictionary = [
"python","r","sql","excel","tableau","power bi",
"machine learning","deep learning","ai",
"data analysis","statistics","nlp","computer vision",
"tensorflow","keras","pytorch",
"pandas","numpy","matplotlib","seaborn",
"data visualization","big data","hadoop","spark",
"mysql","postgresql","mongodb",
"scikit","git","github","api",
"dashboard","analytics","regression","classification"
]


# -------------------------------------------------
# SKILL EXTRACTION
# -------------------------------------------------

def extract_skills_nlp(text):

    tokens = nltk.word_tokenize(text)

    tokens = [w for w in tokens if w.isalpha()]

    tokens = [w for w in tokens if w not in stop_words]

    skills = []

    for skill in skill_dictionary:

        if skill in text:

            skills.append(skill)

    return list(set(skills))


# -------------------------------------------------
# FEATURE SCORING
# -------------------------------------------------

def score_feature(text, keywords):

    matches = sum(1 for kw in keywords if kw in text)

    score = (matches / len(keywords)) * 10

    return round(score,2)


education_keywords = [
"bsc","bachelor","msc","master","phd",
"computer science","data science","statistics"
]

experience_keywords = [
"intern","internship","project","research",
"developed","implemented","team","experience"
]

culture_keywords = [
"team","leadership","communication",
"problem solving","collaboration"
]


# -------------------------------------------------
# ATS SCORE
# -------------------------------------------------

def calculate_ats_score(features):

    skill,exp,edu,culture = features

    ats = skill*3 + exp*3 + edu*2 + culture*2

    return round(min(ats,100),2)


# -------------------------------------------------
# WORD CLOUD
# -------------------------------------------------

def generate_wordcloud(text):

    wordcloud = WordCloud(
        width=900,
        height=600,
        background_color="#0e1117",
        colormap="plasma",
        stopwords=stop_words
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10,6))

    ax.imshow(wordcloud, interpolation="bilinear")

    ax.axis("off")

    return fig


# -------------------------------------------------
# ROLE MATCH
# -------------------------------------------------

roles = {
"Data Analyst":["sql","python","statistics","tableau"],
"Machine Learning Intern":["python","machine learning","pandas","numpy"],
"AI Intern":["python","deep learning","nlp"],
"Business Analyst":["excel","sql","dashboard"],
}


def role_matching(resume_text):

    scores = {}

    for role in roles:

        score = 0

        for skill in roles[role]:

            if skill in resume_text:

                score += 1

        scores[role] = score*25

    return scores


# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])


if uploaded_file:

    resume_text = extract_resume_text(uploaded_file)

    resume_text = clean_text(resume_text)


# -------------------------------------------------
# SKILLS
# -------------------------------------------------

    skills_found = extract_skills_nlp(resume_text)

    st.subheader("🧠 Extracted Skills")

    st.write(", ".join(skills_found))


# -------------------------------------------------
# FEATURE SCORES
# -------------------------------------------------

    skill = score_feature(resume_text,skill_dictionary)

    experience = score_feature(resume_text,experience_keywords)

    education = score_feature(resume_text,education_keywords)

    culture = score_feature(resume_text,culture_keywords)

    features = np.array([skill,experience,education,culture])


# -------------------------------------------------
# ATS SCORE
# -------------------------------------------------

    ats_score = calculate_ats_score(features)

    st.subheader("📊 ATS Resume Score")

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=ats_score,

        title={'text':"ATS Score"},

        gauge={
        'axis':{'range':[0,100]},
        'bar':{'color':"#00F5D4"}
        }

    ))

    st.plotly_chart(fig,use_container_width=True)


# -------------------------------------------------
# WORD CLOUD
# -------------------------------------------------

    st.subheader("💡 Resume Word Cloud")

    wc = generate_wordcloud(resume_text)

    st.pyplot(wc)


# -------------------------------------------------
# ROLE MATCHING
# -------------------------------------------------

    st.subheader("🚀 Job Role Matching")

    scores = role_matching(resume_text)

    fig2 = px.bar(

        x=list(scores.keys()),

        y=list(scores.values()),

        color=list(scores.values()),

        color_continuous_scale="plasma"

    )

    st.plotly_chart(fig2,use_container_width=True)


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown(
"""
<div class="footer">

Made with lots of ❤️ and Python 🐍  

🔗 LinkedIn: https://www.linkedin.com/

</div>
""",
unsafe_allow_html=True
)
