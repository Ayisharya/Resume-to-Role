import PyPDF2, re
SKILLS_DB = []
def load_skills_db(skills_file='backend/course_db.csv'):
    import pandas as pd
    df = pd.read_csv(skills_file)
    return sorted(df['Skill'].unique(), key=len, reverse=True)

SKILLS_DB = load_skills_db()

def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_skills(text):
    found = {skill for skill in SKILLS_DB if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE)}
    return list(found)
