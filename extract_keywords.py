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

IGNORE_WORDS = {"resume", "cv", "curriculum", "vitae", "linkedin", "github", "education",
                "address", "contact", "email", "gmail", "phone", "mobile", "location", "profile"}

def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(email_pattern, text)
    return match.group() if match else "Not Found"

def extract_name(text):
    lines = text.strip().split("\n")
    for line in lines[:10]:
        line_clean = line.strip()
        # Match spaced-out uppercase letters (e.g., "N I K H I L   P A T I L")
        spaced_match = re.match(r"^([A-Z]\s*){3,}", line_clean)
        if spaced_match:
            words = re.split(r'\s{2,}', line_clean)  # Split on double+ spaces
            name_parts = [''.join(w.split()) for w in words]  # Remove single spaces between letters
            return ' '.join(name_parts).title()

        # Otherwise, match normally capitalized names
        cleaned_line = re.sub(r"[^a-zA-Z\s]", "", line)
        words = cleaned_line.split()
        filtered = [word for word in words if word.lower() not in IGNORE_WORDS]
        if len(filtered) >= 2:
            return ' '.join(filtered[:2])

    return "Not Found"

def extract_skills(text):
    found_skills = set()
    text_lower = text.lower()
    IGNORE_TERMS = {"environment", "team", "communication", "management", "skill", "abilities", "working", "experience"}

    # Search for "Skills" section
    skills_match = re.search(r"(skills|technical skills|strengths|core competencies)[\s:]*([\w\s,]+)", text_lower, re.IGNORECASE)
    if skills_match:
        skill_section = skills_match.group(2)
        extracted = [skill.strip() for skill in skill_section.split(",") if skill.strip()]
        found_skills.update(
            skill for skill in extracted 
            if 1 <= len(skill.split()) <= 3 and skill.lower() in {s.lower() for s in SKILLS} and skill.lower() not in IGNORE_TERMS
        )

    # Match all predefined skills in entire text
    found_skills.update(
        skill for skill in SKILLS 
        if skill.lower() in text_lower and skill.lower() not in IGNORE_TERMS
    )

    return ", ".join(found_skills) if found_skills else "Not Found"

def extract_keywords(text):
    return {
        "Name": extract_name(text),
        "Email": extract_email(text),
        "Skills": extract_skills(text),
    }

# Test function
if __name__ == "__main__":
    sample_resume = """N I K H I L   P A T I L
    nikhil@gmail.com
    Technical Skills: Python, Java, SQL, Machine Learning, Data Science, AWS
    Seeking a career in IT and AI."""
    
    extracted_info = extract_keywords(sample_resume)
    print("Extracted Info:", extracted_info)
