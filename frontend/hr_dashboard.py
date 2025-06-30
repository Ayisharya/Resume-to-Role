import streamlit as st
import sys
import os
import requests
import json
import altair as alt  # 📊 for bar chart

#  Make sure the backend folder is included in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from matcher import match_resume

# Gemini API Setup
API_KEY = "AIzaSyATwH943SZeBseHDCECEFJvBnvxFZpPjYU"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def chatbot_response(query):
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": query}]}]}
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    return " Gemini API failed to respond."

def hr_dashboard():
    st.sidebar.header("🤖 Assistant Chat")
    query = st.sidebar.text_input("Ask something...")
    if query:
        with st.spinner("Thinking..."):
            st.sidebar.markdown(chatbot_response(query))

    st.header(" HR Job Fit Analyzer")
    st.write("Upload a candidate's resume and we will suggest matching roles and required upskilling.")

    with st.form("hr_form"):
        cv = st.file_uploader("Upload Candidate CV (PDF)", type=["pdf"])
        exp = st.number_input("Years of Experience", 0, 50, 1)
        job = st.text_input("Earlier Job Role")
        location = st.text_input("Location")
        submit = st.form_submit_button("Evaluate Fit")

    if submit:
        if not all([cv, exp, job, location]):
            st.warning("Please complete all fields and upload CV.")
        else:
            results = match_resume(cv, exp, location, job)
            if results.empty:
                st.info("No suitable roles found.")
            else:
                st.success("Matches found!")

                top_results = results.head(5)

                # 📊 Bar Chart
                st.subheader(" Top 5 Role Matches")
                chart_data = top_results[['Role', 'Match%']]
                bar_chart = alt.Chart(chart_data).mark_bar(color="#4CAF50").encode(
                    x=alt.X('Role', sort='-y'),
                    y=alt.Y('Match%', title='Match Percentage')
                ).properties(width=600)
                st.altair_chart(bar_chart)

                # 💼 Role Details
                for _, r in top_results.iterrows():
                    st.markdown(f"### {r['Role']} — Match: {r['Match%']}%")
                    st.markdown(f"**Missing Skills:** {', '.join(r['Missing Skills']) if r['Missing Skills'] else 'None'}")
                    if r['Courses']:
                        st.markdown("**Recommended Courses:**")
                        for c in r['Courses']:
                            st.markdown(f"- [{c['Course Title']}]({c['Course Link']}) for `{c['Skill']}`")
                    st.markdown(f"🔁 Suggested for: **{r['Project']}** — {'Promotion Path' if r['Promotion'] else '↔️ Lateral Move'}")
                    st.markdown("---")

