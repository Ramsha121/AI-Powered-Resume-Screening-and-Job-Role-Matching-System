import streamlit as st
import numpy as np
import re
import nltk
import plotly.express as px
import plotly.graph_objects as go

from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import nltk

# Ensure required NLTK resources are available
def download_nltk_resources():
    resources = ["punkt", "punkt_tab", "stopwords"]
    for resource in resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(resource)

download_nltk_resources()
# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("🤖 AI Resume Analyzer Dashboard")
st.write("Upload your resume and get an AI-powered analysis")

# -------------------------------------------------
# TEXT EXTRACTION
# -------------------------------------------------

def extract_resume_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text.lower()


def clean_text(text):
    return re.sub(r'\s+', ' ', text)


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

stop_words = set(stopwords.words('english'))

# -------------------------------------------------
# SKILL EXTRACTION
# -------------------------------------------------

def extract_skills_nlp(text):

    tokens = word_tokenize(text)
    tokens = [w for w in tokens if w.isalpha()]
    tokens = [w for w in tokens if w not in stop_words]

    found_skills = []

    for skill in skill_dictionary:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))

# -------------------------------------------------
# SCORING FUNCTION
# -------------------------------------------------

def score_feature(text, keywords):

    matches = sum(1 for kw in keywords if kw in text)

    score = (matches / len(keywords)) * 10

    return round(score,2)


# -------------------------------------------------
# KEYWORDS
# -------------------------------------------------

education_keywords = [
"bsc","bachelor","msc","master","phd",
"computer science","data science","statistics",
"mathematics","engineering","artificial intelligence",
"machine learning","deep learning"
]

experience_keywords = [
"intern","internship","project","research","experience",
"worked","company","client","team project",
"developed","implemented","designed"
]

culture_keywords = [
"team","leadership","communication","presentation",
"problem solving","adaptability","collaboration"
]


# -------------------------------------------------
# JOB ROLES
# -------------------------------------------------

roles = [
{"name":"Business Analyst","weights":np.array([0.4,0.3,0.2,0.1])},
{"name":"Machine Learning Intern","weights":np.array([0.5,0.2,0.2,0.1])},
{"name":"Data Analyst","weights":np.array([0.45,0.25,0.2,0.1])},
{"name":"AI Intern","weights":np.array([0.55,0.15,0.2,0.1])},
{"name":"Research Analyst","weights":np.array([0.3,0.3,0.25,0.15])}
]

# -------------------------------------------------
# JOB DESCRIPTIONS
# -------------------------------------------------

job_descriptions = {

"Business Analyst":
"business analysis sql excel dashboard reporting data visualization",

"Machine Learning Intern":
"machine learning python deep learning pandas numpy model training",

"Data Analyst":
"data analysis sql python tableau statistics visualization reporting",

"AI Intern":
"artificial intelligence neural networks deep learning nlp python",

"Research Analyst":
"research statistics data analysis research methodology modeling"
}

# -------------------------------------------------
# REQUIRED SKILLS
# -------------------------------------------------

required_skills = {

"Business Analyst":["sql","excel","data analysis","dashboard","tableau"],

"Machine Learning Intern":["python","machine learning","pandas","numpy"],

"Data Analyst":["sql","python","statistics","tableau","excel"],

"AI Intern":["python","deep learning","machine learning","nlp"],

"Research Analyst":["statistics","research","data analysis"]
}

# -------------------------------------------------
# ATS SCORE
# -------------------------------------------------

def calculate_ats_score(features):

    skill,exp,edu,culture = features

    ats = skill*3 + exp*3 + edu*2 + culture*2

    return round(min(ats,100),2)


# -------------------------------------------------
# TFIDF ROLE MATCHING
# -------------------------------------------------

def tfidf_role_matching(resume_text):

    docs = [resume_text]

    for role in job_descriptions:
        docs.append(job_descriptions[role])

    vectorizer = TfidfVectorizer()

    matrix = vectorizer.fit_transform(docs)

    resume_vector = matrix[0]

    similarities = cosine_similarity(resume_vector,matrix[1:])

    scores = {}

    for i,role in enumerate(job_descriptions):

        scores[role] = round(similarities[0][i]*100,2)

    return scores


# -------------------------------------------------
# SKILL GAP
# -------------------------------------------------

def detect_skill_gaps(resume_text,role):

    req = required_skills[role]

    missing = []

    for s in req:
        if s not in resume_text:
            missing.append(s)

    return missing


# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------

uploaded_file = st.file_uploader("Upload Resume (PDF)",type=["pdf"])


if uploaded_file:

    resume_text = extract_resume_text(uploaded_file)
    resume_text = clean_text(resume_text)

    skills_found = extract_skills_nlp(resume_text)

    skill = score_feature(resume_text,skill_dictionary)
    experience = score_feature(resume_text,experience_keywords)
    education = score_feature(resume_text,education_keywords)
    culture = score_feature(resume_text,culture_keywords)

    features = np.array([skill,experience,education,culture])

    ats_score = calculate_ats_score(features)

    # -------------------------------------------------
    # ATS GAUGE
    # -------------------------------------------------

    st.subheader("ATS Resume Score")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ats_score,
        title={'text':"ATS Score"},
        gauge={'axis':{'range':[0,100]}}
    ))

    st.plotly_chart(fig,use_container_width=True)

    # -------------------------------------------------
    # FEATURE BARS
    # -------------------------------------------------

    st.subheader("Resume Feature Scores")

    st.progress(skill/10)
    st.write("Skill Score:",skill)

    st.progress(experience/10)
    st.write("Experience Score:",experience)

    st.progress(education/10)
    st.write("Education Score:",education)

    st.progress(culture/10)
    st.write("Culture Score:",culture)

    # -------------------------------------------------
    # SKILLS
    # -------------------------------------------------

    st.subheader("Extracted Skills")

    st.write(", ".join(skills_found))

    # -------------------------------------------------
    # ROLE MATCHING
    # -------------------------------------------------

    results = []

    for role in roles:

        role_score = np.dot(role["weights"],features)/10

        role_score = min(role_score*100,100)

        results.append((role["name"],round(role_score,2)))

    results.sort(key=lambda x:x[1],reverse=True)

    role_names = [r[0] for r in results]
    role_scores = [r[1] for r in results]

    st.subheader("Best Job Role Matches")

    fig2 = px.bar(
        x=role_names,
        y=role_scores,
        labels={'x':'Role','y':'Match Score'}
    )

    st.plotly_chart(fig2,use_container_width=True)

    # -------------------------------------------------
    # TFIDF JOB MATCH
    # -------------------------------------------------

    st.subheader("NLP Job Similarity")

    tfidf_scores = tfidf_role_matching(resume_text)

    fig3 = px.bar(
        x=list(tfidf_scores.keys()),
        y=list(tfidf_scores.values()),
        labels={'x':'Role','y':'Similarity %'}
    )

    st.plotly_chart(fig3,use_container_width=True)

    # -------------------------------------------------
    # SKILL GAP
    # -------------------------------------------------

    top_role = results[0][0]

    missing = detect_skill_gaps(resume_text,top_role)

    st.subheader("Skill Gap Analysis")

    st.write("Recommended Role:",top_role)

    if len(missing)==0:
        st.success("No major skill gaps detected")
    else:
        st.write("Skills to improve:")
        for m in missing:
            st.write("-",m)
