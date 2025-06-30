import pandas as pd
from sentence_transformers import SentenceTransformer, util
from resume_parser import extract_text, extract_skills

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_jobs(csv_path='backend/job_database.csv'):
    return pd.read_csv(csv_path)

def load_courses(csv_path='backend/course_db.csv'):
    return pd.read_csv(csv_path)

def match_resume(pdf_file, current_exp, location, current_job_title):
    text = extract_text(pdf_file)
    skills = extract_skills(text)
    emp_vec = model.encode(" ".join(skills))

    jobs = load_jobs()
    courses = load_courses()
    results = []

    for _, job in jobs.iterrows():
        if job['Location'] != 'ANY' and job['Location'] not in location:
            continue
        job_skills = [s.strip() for s in job["Required Skills"].split(",")]
        job_vec = model.encode(" ".join(job_skills))
        sim = util.cos_sim(emp_vec, job_vec).item()
        missing = set(job_skills) - set(skills)
        rec_courses = courses[courses['Skill'].isin(missing)][['Skill','Course Title','Course Link']].to_dict('records')
        is_promotion = ("Senior" in job["Job Title"] or job["Min Experience"] > current_exp) and sim > 0.5

        results.append({
            "Role": job["Job Title"],
            "Match%": round(sim * 100, 1),
            "Missing Skills": missing,
            "Courses": rec_courses,
            "Promotion": is_promotion,
            "Project": job["Project Area"]
        })

    return pd.DataFrame(sorted(results, key=lambda r: r["Match%"], reverse=True))
