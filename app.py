import os
import joblib
import numpy as np
import PyPDF2
import google.generativeai as genai  # ✅ Import Google AI API
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from utils import preprocess_text  
from extract_keywords import extract_keywords  

# Initialize Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Database
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Load ML Models
ats_model = joblib.load('ats_model.pkl')
job_role_model = joblib.load('job_role_model.pkl')
tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')

# ✅ Configure Google AI API
genai.configure(api_key="AIzaSyACL2Z0NLEOQq1WXmKSAodZqJXnEcYcu90") 
model = genai.GenerativeModel("gemini-2.0-flash")

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Resume Analysis Model
class ResumeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ats_score = db.Column(db.Float, nullable=False)
    job_roles = db.Column(db.Text, nullable=False)  # Ensure this line exists
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    skills = db.Column(db.Text)
    education = db.Column(db.Text)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Updated for SQLAlchemy 2.0


@app.route('/')
def home():
    return render_template('index.html')

# User Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please login.", "danger")
            return redirect(url_for('login'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Try again.", "danger")
    
    return render_template('login.html')

# User Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('_flashes', None)  # ✅ Prevent duplicate flash messages
    flash("Successfully logged out.", "success")
    return redirect(url_for('home'))


# ✅ Resume Prediction Route (With AI Suggestions)
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if 'resume' not in request.files:
        flash("No file uploaded.", "danger")
        return redirect(url_for('home'))

    file = request.files['resume']
    if not file or file.filename.strip() == '':
        flash("No selected file.", "danger")
        return redirect(url_for('home'))

    # Save uploaded file
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(pdf_path)

    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        flash("The uploaded PDF contains no readable text.", "danger")
        return redirect(url_for('home'))

    # Process the text
    cleaned_resume = preprocess_text(text)
    resume_features = tfidf_vectorizer.transform([cleaned_resume]).toarray()

    # Make predictions
    ats_score = round(ats_model.predict(resume_features)[0], 2)
    
    # Predict Job Roles (Top 3 Relevant Roles)
    job_role_probs = job_role_model.predict_proba(resume_features)[0]
    top_3_indices = np.argsort(job_role_probs)[-3:][::-1]  # Get top 3 roles
    top_3_roles = [job_role_model.classes_[i] for i in top_3_indices]
    job_roles_str = ', '.join(top_3_roles)  # Store as a string in DB
    
    # Extract Keywords (Name, Email, Skills, Education)
    extracted_info = extract_keywords(text)
    name = extracted_info.get("Name", "Not Found")
    email = extracted_info.get("Email", "Not Found")
    skills = extracted_info.get("Skills", "Not Found")
    education = extracted_info.get("Education", "Not Found")

    # ✅ Store analysis in the database
    new_analysis = ResumeAnalysis(
        user_id=current_user.id,
        ats_score=ats_score,
        job_roles=job_roles_str,
        name=name,
        email=email,
        skills=skills,
        education=education
    )
    db.session.add(new_analysis)
    db.session.commit()

    flash("Resume analysis saved successfully!", "success")

    # ✅ Generate AI Resume Suggestions
    ai_prompt = f"""
    This is a candidate's resume:
    ---
    {text}
    ---
    Provide resume improvement suggestions in bullet points. Focus on formatting, content clarity, and key skill highlights.
    """
    try:
        response = model.generate_content(ai_prompt)
        resume_suggestions = response.text
    except Exception as e:
        print("AI Suggestion Error:", e)
        resume_suggestions = "No suggestions available at the moment."

    return render_template(
        'index.html',
        prediction=ats_score,
        job_roles=job_roles_str,
        extracted_info=extracted_info,
        resume_suggestions=resume_suggestions
    )

@app.route('/generate_suggestions', methods=['GET'])
@login_required
def generate_suggestions():
    """Fetches the latest resume text and generates AI suggestions."""
    
    # Fetch the latest resume analysis for the logged-in user
    latest_analysis = ResumeAnalysis.query.filter_by(user_id=current_user.id).order_by(ResumeAnalysis.id.desc()).first()
    
    if not latest_analysis:
        return jsonify({"suggestions": "No resume found. Please upload one first."})

    resume_text = f"""
    Name: {latest_analysis.name}
    Email: {latest_analysis.email}
    Skills: {latest_analysis.skills}
    Education: {latest_analysis.education}
    Job Roles: {latest_analysis.job_roles}
    ATS Score: {latest_analysis.ats_score}
    """
    
    # AI Prompt
    ai_prompt = f"""
    This is a candidate's resume:
    ---
    {resume_text}
    ---
    Provide detailed suggestions to improve the resume, focusing on formatting, skills, and missing details.
    """

    try:
        import re
        response = model.generate_content(ai_prompt)
        resume_suggestions = re.sub(r"[\*\_]+(.*?)[\*\_]+", r"\1", response.text)  # Removes all *italic* and **bold** formatting
        resume_suggestions = re.sub(r"\*", "", resume_suggestions)
  
    except Exception as e:
        print("AI Suggestion Error:", e)
        resume_suggestions = "Unable to generate suggestions at the moment."

    return jsonify({"suggestions": resume_suggestions})

# Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    """ Extracts text from a PDF file. """
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text
    except Exception as e:
        print("Error extracting text from PDF:", e)
    return text


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
