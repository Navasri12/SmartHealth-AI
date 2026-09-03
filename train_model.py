import os
import random
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

# Define paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# List of 50 comprehensive symptoms
SYMPTOMS = [
    'fever', 'cough', 'fatigue', 'sore_throat', 'muscle_pain', 'headache', 'chills', 'body_ache',
    'sneezing', 'runny_nose', 'nasal_congestion', 'loss_of_taste_smell', 'shortness_of_breath',
    'wheezing', 'chest_tightness', 'chest_pain', 'high_fever', 'sweating', 'heartburn',
    'chest_discomfort', 'nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'sensitivity_to_light',
    'sensitivity_to_sound', 'dizziness', 'blurred_vision', 'neck_pain', 'frequent_urination',
    'excessive_thirst', 'slow_wound_healing', 'prolonged_fever', 'rash', 'itchy_eyes', 'watery_eyes',
    'mucus_production', 'painful_urination', 'cloudy_urine', 'skin_rash', 'itchy_skin', 'dry_skin',
    'joint_pain', 'joint_swelling', 'joint_stiffness', 'weakness', 'pale_skin', 'weight_gain',
    'weight_loss', 'anxiety'
]

# Disease mapping with signature symptoms
DISEASE_PROFILES = {
    'Influenza': ['fever', 'cough', 'fatigue', 'sore_throat', 'muscle_pain', 'headache', 'chills', 'body_ache'],
    'Common Cold': ['cough', 'sneezing', 'runny_nose', 'sore_throat', 'nasal_congestion', 'fatigue', 'headache'],
    'COVID-19': ['fever', 'cough', 'loss_of_taste_smell', 'shortness_of_breath', 'fatigue', 'sore_throat', 'headache'],
    'Asthma': ['shortness_of_breath', 'wheezing', 'chest_tightness', 'cough', 'fatigue'],
    'Pneumonia': ['high_fever', 'cough', 'chest_pain', 'shortness_of_breath', 'fatigue', 'chills', 'sweating', 'mucus_production'],
    'GERD': ['heartburn', 'chest_discomfort', 'nausea', 'sore_throat'],
    'Gastroenteritis': ['abdominal_pain', 'nausea', 'vomiting', 'diarrhea', 'fever', 'fatigue'],
    'Migraine': ['headache', 'nausea', 'sensitivity_to_light', 'sensitivity_to_sound', 'dizziness', 'blurred_vision'],
    'Tension Headache': ['headache', 'neck_pain', 'fatigue', 'muscle_pain'],
    'Hypertension': ['dizziness', 'headache', 'blurred_vision', 'chest_discomfort', 'fatigue'],
    'Type 2 Diabetes': ['excessive_thirst', 'frequent_urination', 'fatigue', 'blurred_vision', 'slow_wound_healing'],
    'Malaria': ['high_fever', 'chills', 'sweating', 'headache', 'nausea', 'muscle_pain'],
    'Typhoid': ['prolonged_fever', 'abdominal_pain', 'fatigue', 'headache', 'diarrhea', 'rash'],
    'Allergic Rhinitis': ['sneezing', 'runny_nose', 'itchy_eyes', 'watery_eyes', 'nasal_congestion'],
    'Bronchitis': ['cough', 'mucus_production', 'fatigue', 'shortness_of_breath', 'chest_discomfort'],
    'Urinary Tract Infection': ['painful_urination', 'frequent_urination', 'abdominal_pain', 'cloudy_urine', 'fever'],
    'Dermatitis / Eczema': ['skin_rash', 'itchy_skin', 'dry_skin'],
    'Psoriasis': ['skin_rash', 'dry_skin', 'joint_pain'],
    'Rheumatoid Arthritis': ['joint_pain', 'joint_swelling', 'joint_stiffness', 'fatigue', 'fever'],
    'Osteoarthritis': ['joint_pain', 'joint_stiffness', 'weakness'],
    'Anemia': ['fatigue', 'weakness', 'pale_skin', 'dizziness', 'shortness_of_breath'],
    'Hypothyroidism': ['fatigue', 'weight_gain', 'dry_skin', 'weakness'],
    'Hyperthyroidism': ['weight_loss', 'anxiety', 'sweating', 'fatigue'],
    'Sinusitis': ['headache', 'nasal_congestion', 'runny_nose', 'fever', 'cough'],
    'Appendicitis': ['abdominal_pain', 'nausea', 'vomiting', 'fever'],
    'Kidney Stones': ['abdominal_pain', 'painful_urination', 'nausea', 'vomiting', 'fever'],
    'Anxiety Disorder': ['anxiety', 'fatigue', 'dizziness', 'chest_tightness'],
    'Vertigo': ['dizziness', 'nausea', 'blurred_vision', 'headache'],
    'Angina Pectoris': ['chest_pain', 'shortness_of_breath', 'fatigue', 'dizziness', 'sweating'],
    'Irritable Bowel Syndrome': ['abdominal_pain', 'diarrhea', 'nausea'],
    'Chickenpox': ['fever', 'skin_rash', 'fatigue', 'body_ache'],
    'Dengue Fever': ['high_fever', 'body_ache', 'joint_pain', 'skin_rash', 'headache', 'nausea']
}

def generate_dataset(samples_per_disease=60):
    """Generates synthetic dataset with realistic variation and noise for robust training."""
    rows = []
    np.random.seed(42)
    random.seed(42)
    
    for disease, core_symptoms in DISEASE_PROFILES.items():
        for _ in range(samples_per_disease):
            row = {'disease': disease}
            for sym in SYMPTOMS:
                if sym in core_symptoms:
                    # Core symptom present 80-95% of the time
                    row[sym] = 1 if random.random() < 0.88 else 0
                else:
                    # Non-core symptom present 1-5% of the time (noise)
                    row[sym] = 1 if random.random() < 0.03 else 0
            
            # Ensure at least 2 core symptoms are present
            present_core = [sym for sym in core_symptoms if row[sym] == 1]
            if len(present_core) < 2:
                for sym in random.sample(core_symptoms, min(3, len(core_symptoms))):
                    row[sym] = 1
                    
            rows.append(row)
            
    df = pd.DataFrame(rows)
    csv_path = os.path.join(DATASET_DIR, 'disease_symptom_dataset.csv')
    df.to_csv(csv_path, index=False)
    print(f"[OK] Generated dataset with {len(df)} records across {len(DISEASE_PROFILES)} diseases saved to {csv_path}")
    return df

def train_and_evaluate():
    df = generate_dataset(samples_per_disease=70)
    
    X = df[SYMPTOMS]
    y_raw = df['disease']
    
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Naive Bayes': MultinomialNB(),
        'Support Vector Machine': SVC(probability=True, kernel='rbf', random_state=42)
    }
    
    metrics_list = []
    trained_model_objs = {}
    
    best_model_name = None
    best_f1 = -1.0
    best_model_obj = None
    
    print("\n--- Model Training & Evaluation ---")
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        metrics_list.append({
            'model_name': name,
            'accuracy': round(float(acc) * 100, 2),
            'precision': round(float(prec) * 100, 2),
            'recall': round(float(rec) * 100, 2),
            'f1_score': round(float(f1) * 100, 2)
        })
        
        trained_model_objs[name] = model
        print(f"Model: {name:<22} | Acc: {acc*100:.2f}% | Prec: {prec*100:.2f}% | Rec: {rec*100:.2f}% | F1: {f1*100:.2f}%")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model_obj = model

    print(f"\n[BEST MODEL] Selected Model: {best_model_name} (F1 Score: {best_f1*100:.2f}%)")
    
    # Save artifacts
    joblib.dump(best_model_obj, os.path.join(MODEL_DIR, 'disease_model.pkl'))
    joblib.dump(le, os.path.join(MODEL_DIR, 'label_encoder.pkl'))
    joblib.dump(SYMPTOMS, os.path.join(MODEL_DIR, 'features.pkl'))
    joblib.dump({
        'best_model_name': best_model_name,
        'metrics': metrics_list,
        'symptoms_list': SYMPTOMS,
        'diseases_list': list(le.classes_)
    }, os.path.join(MODEL_DIR, 'metrics.pkl'))
    
    print("[OK] Successfully saved model, label encoder, feature list, and metrics artifacts into models/ directory.")

if __name__ == '__main__':
    train_and_evaluate()
