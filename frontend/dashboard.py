import streamlit as st
import sys
import os

# 👇 This line ensures Python can find files in ../backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from matcher import match_resume 
import requests
import json

API_KEY = "AIzaSyATwH943SZeBseHDCECEFJvBnvxFZpPjYU"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def chatbot_response(query):
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": query}]}]}
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    return " Gemini API failed to respond."

def employee_dashboard():
    st.sidebar.header("🤖 Assistant Chat")
    query = st.sidebar.text_input("Ask something...")
    if query:
        with st.spinner("Thinking..."):
            st.sidebar.markdown(chatbot_response(query))

    st.header(" Career Growth Assistant")
    with st.form("employee_form"):
        first = st.text_input("First Name")
        last = st.text_input("Last Name")
        loc = st.text_input("Location")
        current_job = st.text_input("Current Job Title")
        current_exp = st.number_input("Years of Experience", 0, 50, 1)
        pdf = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        submitted = st.form_submit_button("Analyze Opportunities")

    if submitted:
        if not all([first, last, loc, current_job, pdf]):
            st.error("Please complete all fields.")
        else:
            df = match_resume(pdf, current_exp, loc, current_job)
            if df.empty:
                st.warning("No good matches found.")
            else:
                for _, row in df.head(5).iterrows():
                    st.subheader(f"{row['Role']} — Match: {row['Match%']}%")
                    st.markdown(f"**Missing Skills:** {', '.join(row['Missing Skills']) if row['Missing Skills'] else 'None'}")
                    if row['Courses']:
                        st.markdown(" Recommended Courses:")
                        for course in row['Courses']:
                            st.markdown(f"- [{course['Course Title']}]({course['Course Link']}) — `{course['Skill']}`")
                    st.markdown(f"{' Promotion opportunity!' if row['Promotion'] else '📌 Lateral Move'}")
                    st.markdown("---")