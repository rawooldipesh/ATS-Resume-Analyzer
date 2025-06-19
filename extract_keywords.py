import re

# Expanded Skill Set
SKILLS = {
    "Python", "Java", "C++", "JavaScript", "SQL", "HTML", "CSS", "Machine Learning", 
    "Deep Learning", "Data Science", "AI", "Cloud Computing", "Cybersecurity",
    "React", "Node.js", "AWS", "Docker", "Kubernetes", "TensorFlow", "Pandas", "NLP",
    "Excel", "Power BI", "Tableau", "MongoDB", "MySQL", "PostgreSQL", "Flask", "Django",
    "Android Development", "Swift", "Kotlin", "Flutter", "Blockchain", "Solidity",
    "Ethical Hacking", "Risk Management", "SEO", "Marketing", "Content Writing",
    "Graphic Design", "Illustrator", "Photoshop", "Leadership", "Communication",
    "Teamwork", "Adaptability", "Cooperation", "Analytical Thinking", "Programming",
    "Technical Writing", "Project Management", "Optimistic and Hardworking", 
    "Able to work under pressure", "Time Management", "Budgeting", "Scheduling",
    "PLC Programming", "SCADA Development", "LabVIEW", "AutoCAD", "MATLAB", "Simulink",
    "Arduino", "Raspberry Pi", "SolidWorks", "Data Acquisition", "Embedded Systems",
    "Software Development", "Networking", "Database Administration", "Cyber Threat Analysis"
}

IGNORE_WORDS = {
    "resume", "cv", "curriculum", "vitae", "linkedin", "github", "education",
    "address", "contact", "email", "gmail", "phone", "mobile", "location", "profile"
}

def extract_email(text):
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group().strip() if match else "Not Found"


def extract_name(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for line in lines[:15]:  # Focus on top 15 lines
        if any(keyword in line.lower() for keyword in ['link', 'skill', 'email', 'summary']):
            continue  # Skip unwanted headers

        # Match ALL-CAPS name
        if re.fullmatch(r"[A-Z\s]{5,30}", line) and " " in line:
            return ' '.join(line.split()).title()

        # Match capitalized names
        words = line.split()
        if 1 < len(words) <= 3 and all(w[0].isupper() for w in words if w.isalpha()):
            return line.strip()

    return "Not Found"



def extract_skills(text):
    found_skills = set()
    text_lower = text.lower()
    ignore_terms = {"environment", "team", "communication", "management", "skill", "abilities", "working", "experience"}

    # Match defined skills
    for skill in SKILLS:
        if re.search(rf"\b{re.escape(skill.lower())}\b", text_lower):
            if not any(term in skill.lower() for term in ignore_terms):
                found_skills.add(skill)

    return ", ".join(sorted(found_skills)) if found_skills else "Not Found"


def extract_keywords(text):
    return {
        "Name": extract_name(text),
        "Email": extract_email(text),
        "Skills": extract_skills(text),
    }

# Optional Test Code
if __name__ == "__main__":
    sample_resume = """DIPESH RAWOOL
    rawooldipesh0@gmail.com
    Tech Skills: Python, Java, SQL, Machine Learning, React, AI
    Looking for a role in backend development or AI research."""
    
    extracted_info = extract_keywords(sample_resume)
    print("Extracted Info:", extracted_info)
