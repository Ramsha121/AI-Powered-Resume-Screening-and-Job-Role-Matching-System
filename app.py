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
# DARK THEME CSS
# ---------------------------------------------------

st.markdown("""
<style>

.stApp{
background-color:#0E1117;
color:white;
}

.big-title{
font-size:70px;
font-weight:bold;
text-align:center;
color:#00F5D4;
}

.sub-title{
font-size:22px;
text-align:center;
color:white;
}

.stButton>button{
background-color:#00F5D4;
color:black;
font-size:18px;
font-weight:bold;
border-radius:12px;
height:50px;
width:220px;
}

.footer{
position:fixed;
bottom:0;
left:0;
width:100%;
text-align:center;
padding:10px;
font-size:14px;
color:white;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.markdown('<p class="big-title">🤖 AI Resume Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload your resume and get AI powered insights</p>', unsafe_allow_html=True)

st.write("")


# ---------------------------------------------------
# NLTK DOWNLOAD
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
# SKILL DATABASE
# ---------------------------------------------------

skill_dictionary = [

"python","r","sql","excel","tableau","power bi",
"machine learning","deep learning","ai","nlp",
"statistics","data analysis","pandas","numpy",
"matplotlib","seaborn","tensorflow","keras",
"pytorch","big data","hadoop","spark",
"mongodb","postgresql","mysql",
"dashboard","analytics","classification","regression"

]


# ---------------------------------------------------
# REQUIRED SKILLS FOR ROLES
# ---------------------------------------------------

required_skills = {

"Data Analyst":[
"python","sql","tableau","statistics","excel"
],

"Machine Learning Intern":[
"python","machine learning","pandas","numpy","deep learning"
],

"AI Intern":[
"python","deep learning","nlp","tensorflow","pytorch"
],

"Business Analyst":[
"sql","excel","dashboard","tableau","communication"
]

}


# ---------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------

uploaded_file = st.file_uploader("📄 Upload Resume PDF", type=["pdf"])


# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------

def extract_text(file):

    reader = PdfReader(file)

    text=""

    for page in reader.pages:

        t = page.extract_text()

        if t:
            text += t

    return text.lower()



def extract_skills(text):

    found=[]

    for skill in skill_dictionary:

        if skill in text:
            found.append(skill)

    return list(set(found))



def score_section(text, keywords):

    count=0

    for k in keywords:

        if k in text:
            count+=1

    score=(count/len(keywords))*10

    return round(score,2)



def ats_score(skill,exp,edu,culture):

    ats=(skill*3)+(exp*3)+(edu*2)+(culture*2)

    return round(min(ats,100),2)



def generate_wordcloud(text):

    wc=WordCloud(
        width=900,
        height=500,
        background_color="#0E1117",
        colormap="plasma",
        stopwords=stop_words
    ).generate(text)

    fig,ax=plt.subplots()

    ax.imshow(wc)
    ax.axis("off")

    return fig



def role_matching(text):

    roles={

    "Data Analyst":["python","sql","statistics","tableau"],

    "Machine Learning Intern":[
    "python","machine learning","pandas","numpy"
    ],

    "AI Intern":[
    "python","deep learning","nlp"
    ],

    "Business Analyst":[
    "sql","excel","dashboard"
    ]

    }

    scores={}

    for role in roles:

        score=0

        for skill in roles[role]:

            if skill in text:
                score+=1

        scores[role]=score*25

    return scores



def detect_skill_gap(text,role):

    required=required_skills[role]

    missing=[]

    for s in required:

        if s not in text:
            missing.append(s)

    return missing



# ---------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------

if uploaded_file:

    if st.button("🚀 Analyze Resume"):

        resume_text = extract_text(uploaded_file)


# ---------------------------------------------------
# SKILLS
# ---------------------------------------------------

        st.subheader("🧠 Extracted Skills")

        skills = extract_skills(resume_text)

        st.success(", ".join(skills))


# ---------------------------------------------------
# SECTION SCORES
# ---------------------------------------------------

        skill_score = score_section(resume_text, skill_dictionary)

        exp_keywords=["intern","project","experience","research"]

        edu_keywords=["bsc","msc","phd","bachelor"]

        culture_keywords=["team","leadership","communication"]

        exp_score = score_section(resume_text,exp_keywords)

        edu_score = score_section(resume_text,edu_keywords)

        culture_score = score_section(resume_text,culture_keywords)


# ---------------------------------------------------
# ATS SCORE
# ---------------------------------------------------

        ats = ats_score(skill_score,exp_score,edu_score,culture_score)

        st.subheader("📊 ATS Resume Score")

        fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=ats,

        gauge={'axis':{'range':[0,100]}},

        title={'text':"ATS Resume Score"}

        ))

        fig.update_layout(template="plotly_dark")

        st.plotly_chart(fig,use_container_width=True)


# ---------------------------------------------------
# WORD CLOUD
# ---------------------------------------------------

        st.subheader("💡 Resume Word Cloud")

        wc = generate_wordcloud(resume_text)

        st.pyplot(wc)



# ---------------------------------------------------
# ROLE MATCHING
# ---------------------------------------------------

        st.subheader("🎯 Best Job Role Match")

        scores = role_matching(resume_text)

        fig2 = px.bar(

        x=list(scores.keys()),
        y=list(scores.values()),
        color=list(scores.values()),
        color_continuous_scale="plasma"

        )

        fig2.update_layout(template="plotly_dark")

        st.plotly_chart(fig2,use_container_width=True)


# ---------------------------------------------------
# SKILL GAP
# ---------------------------------------------------

        top_role = max(scores, key=scores.get)

        st.subheader("📉 Skill Gap Analysis")

        st.info(f"Recommended Role: {top_role}")

        missing = detect_skill_gap(resume_text,top_role)

        if len(missing)==0:

            st.success("Your resume matches this role well!")

        else:

            st.write("Skills to improve:")

            for m in missing:

                st.write("•",m)


# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("""

<div class="footer">

Made with lots of ❤️ and Python 🐍  
<br>
🔗 LinkedIn: https://www.linkedin.com/in/YOUR-LINK/

</div>

""", unsafe_allow_html=True)
