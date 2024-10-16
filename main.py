import os
import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import PyPDF2
from collections import Counter
import re

# Set up the Gemini API
# gemini_api_key = st.secrets["gemini_api_key"] if "gemini_api_key" in st.secrets else os.getenv("gemini_api_key")
genai.configure(api_key="AIzaSyA6Bl6zg6bcFaA4Y8LyuAgNGrw2BxujRwQ")


def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        st.error(f"Error fetching the URL: {e}")
        return ""


def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""


def extract_text_from_txt(file):
    try:
        return file.read().decode('utf-8')
    except Exception as e:
        st.error(f"Error reading TXT file: {e}")
        return ""


def extract_keywords(text):
    # Simple keyword extraction (you might want to use a more sophisticated method)
    words = re.findall(r'\b\w+\b', text.lower())
    return Counter(words)


def calculate_keyword_match(job_keywords, resume_keywords):
    common_keywords = set(job_keywords.keys()) & set(resume_keywords.keys())
    return len(common_keywords) / len(job_keywords) if job_keywords else 0


def analyze_resume(job_description, resume_text):
    job_keywords = extract_keywords(job_description)
    resume_keywords = extract_keywords(resume_text)
    keyword_match = calculate_keyword_match(job_keywords, resume_keywords)

    prompt = f"""
    You are an advanced Applicant Tracking System (ATS) with the capability to provide detailed feedback. Analyze the following resume against the provided job description. 

    Job Description:
    {job_description}

    Resume:
    {resume_text}

    Keyword Match Score: {keyword_match:.2%}

    Provide an analysis and recommendations in the following format:

    1. Overall Match:
    - Provide a brief overview of how well the resume matches the job description.
    - Comment on the keyword match score.

    2. Key Skills Alignment:
    - List the key skills mentioned in the job description.
    - Identify which of these skills are present or missing in the resume.

    3. Experience Relevance:
    - Evaluate how well the candidate's experience aligns with the job requirements.
    - Highlight any particularly relevant experiences.

    4. Education and Certifications:
    - Comment on the relevance of the candidate's education and certifications.
    - Suggest any additional certifications that might be beneficial.

    5. Resume Structure and Formatting:
    - Evaluate the overall structure and readability of the resume.
    - Suggest improvements for ATS optimization.

    6. Recommendations:
    - Provide specific, actionable recommendations to improve the resume's ATS compatibility and overall strength for this position.

    Ensure your analysis and recommendations are specific, actionable, and tailored to optimize the resume for ATS systems and the given job description.
    """

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error during analysis: {e}")
        return ""


# Streamlit App Layout
st.title("🤖 ATS Simulator and Resume Enhancer")

st.markdown("""
This application simulates an Applicant Tracking System (ATS) and provides recommendations to optimize your resume for the desired job.
""")

# Job Posting Input
st.header("🔍 Job Posting Details")

job_description = ""
job_link = st.text_input("Enter the job posting URL (optional):")
job_file = st.file_uploader("Or upload the job description file (PDF/TXT):", type=['pdf', 'txt'])
job_text_input = st.text_area("Or paste the job description text here:")

if job_link:
    st.info("Fetching job description from URL...")
    job_description = extract_text_from_url(job_link)
    if job_description:
        st.success("Job description fetched successfully.")
elif job_file:
    st.info("Extracting job description from uploaded file...")
    if job_file.type == "application/pdf":
        job_description = extract_text_from_pdf(job_file)
    else:
        job_description = extract_text_from_txt(job_file)
    if job_description:
        st.success("Job description extracted successfully.")
elif job_text_input:
    job_description = job_text_input
    if job_description.strip():
        st.success("Job description input received.")
    else:
        st.warning("Job description text is empty.")
else:
    st.warning("Please provide the job description via URL, file upload, or text input.")

# Resume Upload
st.header("📝 Upload Your Resume")
resume_file = st.file_uploader("Upload your resume (PDF/TXT):", type=['pdf', 'txt'])

resume_text = ""
if resume_file:
    st.info("Extracting text from resume...")
    if resume_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(resume_file)
    else:
        resume_text = extract_text_from_txt(resume_file)
    if resume_text:
        st.success("Resume text extracted successfully.")
    else:
        st.error("Failed to extract text from resume.")
else:
    st.warning("Please upload your resume.")

# Analyze Button
if st.button("Analyze Resume") and job_description and resume_text:
    with st.spinner("Analyzing your resume..."):
        analysis = analyze_resume(job_description, resume_text)
        if analysis:
            st.subheader("ATS Analysis and Recommendations")
            st.write(analysis)
        else:
            st.error("Failed to get analysis and recommendations.")