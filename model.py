import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize Lemmatizer
lemmatizer = WordNetLemmatizer()

# Preprocessing function
def preprocess_text(text):
    if pd.isnull(text):
        return ""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# Load dataset
df = pd.read_csv('refined_data.csv')
print("Columns in dataset:", df.columns)

# Ensure correct column names
if 'Resume Text' not in df.columns or 'Job Role' not in df.columns:
    raise KeyError("Dataset must contain 'Resume Text' and 'Job Role' columns")

# Check job role distribution
print("Job Role Counts Before Balancing:", df['Job Role'].value_counts())

# Duplicate underrepresented job roles to have at least 5 samples per role
min_samples = 5
df_balanced = df.loc[df.index.repeat(min_samples // df['Job Role'].value_counts().reindex(df['Job Role']).fillna(1).astype(int))]

# Check new counts
print("Job Role Counts After Balancing:", df_balanced['Job Role'].value_counts())

# Preprocess text columns
df_balanced['cleaned_resume'] = df_balanced['Resume Text'].apply(preprocess_text)
df_balanced['cleaned_job_description'] = df_balanced['Job Role'].apply(preprocess_text)

# TF-IDF Vectorization (Combine Resume and Job Description)
tfidf_vectorizer = TfidfVectorizer(max_features=1000)
X = tfidf_vectorizer.fit_transform(df_balanced['cleaned_resume'] + " " + df_balanced['cleaned_job_description']).toarray()

# Save TF-IDF Vectorizer
joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.pkl')

# ATS Score Prediction Model
y_ats = df_balanced['ATS Score']
X_train, X_test, y_train, y_test = train_test_split(X, y_ats, test_size=0.2, random_state=42)
ats_model = RandomForestRegressor(n_estimators=100, random_state=42)
ats_model.fit(X_train, y_train)
ats_predictions = ats_model.predict(X_test)
print(f'Mean Squared Error (ATS Score): {mean_squared_error(y_test, ats_predictions)}')
joblib.dump(ats_model, 'ats_model.pkl')

# Job Role Prediction Model
y_job_role = df_balanced['Job Role'].astype(str)

# Use stratified split
X_train, X_test, y_train, y_test = train_test_split(X, y_job_role, test_size=0.2, stratify=y_job_role, random_state=42)

# Use Logistic Regression
from sklearn.linear_model import LogisticRegression
job_role_model = LogisticRegression(max_iter=1000)
job_role_model.fit(X_train, y_train)

# Predict top 3 job roles
proba = job_role_model.predict_proba(X_test)
predicted_indices = np.argsort(proba, axis=1)[:, -3:][:, ::-1]  # Get top 3 predictions
predicted_roles = [[job_role_model.classes_[idx] for idx in row] for row in predicted_indices]

y_test_list = y_test.tolist()
correct_predictions = sum([y_test_list[i] in predicted_roles[i] for i in range(len(y_test_list))])
accuracy = correct_predictions / len(y_test_list)
print(f'Job Role Prediction Top-3 Accuracy: {accuracy:.2f}')

# Save the model
joblib.dump(job_role_model, 'job_role_model.pkl')

print("Models trained and saved successfully!")
