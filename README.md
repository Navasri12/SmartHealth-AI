# SmartHealth AI – Intelligent Symptom Analysis, Disease Prediction and Healthcare Support System

**Academic Title:** SmartHealth AI – An Intelligent Symptom Analysis, Disease Prediction and Healthcare Support System Using Machine Learning

---

## 📌 Project Overview
**SmartHealth AI** is a full-stack, machine learning-powered healthcare decision-support web application. Patients can register, securely authenticate, select categorized symptoms with severity levels and duration, and receive instant ML-based predictions of possible health conditions alongside model confidence probabilities, Explainable AI (XAI) feature contribution breakdowns, personalized lifestyle guidance, and downloadable PDF health reports.

It features a dedicated **Emergency Symptom Checker** safety layer that screens for critical symptoms (such as acute chest pain or breathing difficulty) and directs patients to immediate emergency care before running standard predictions.

---

## 🚀 Key Features

* **Multi-Symptom Selection Interface**: Searchable symptom cards categorized into General, Respiratory, Digestive, Neurological, Skin, Cardiovascular, Urinary, and Mental health.
* **Symptom Severity & Duration**: Captures Mild/Moderate/Severe intensity and duration (<1 day, 1–3 days, 4–7 days, >1 week) for advanced risk estimation.
* **AI Disease Risk Prediction**: Predicts top 3 differential health conditions with calibrated model confidence percentages.
* **Explainable AI (XAI)**: Visual bar representation of symptom importance contribution weights for model transparency.
* **Emergency Red-Flag Warnings**: Automatic pre-prediction safety override for acute/life-threatening symptoms.
* **Patient Health Dashboard**: Tracks total assessments, health risk index, recent predictions, and quick actions.
* **Interactive Chart Analytics**: Chart.js visualizations of symptom reporting frequencies and condition distribution trends.
* **PDF Health Report Download**: Generates styled PDF summaries via ReportLab for physician consultation.
* **Administrator Portal**: Patient account control (enable/disable), CRUD management for symptoms & disease knowledge base, and live ML model comparison analytics.
* **Model Evaluation Engine**: Trains and compares 5 ML classifiers (Random Forest, Decision Tree, Logistic Regression, Naive Bayes, Support Vector Machine) and persists performance metrics into database.

---

## 🛠️ Technology Stack

| Layer | Technology Used |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Chart.js, FontAwesome |
| **Backend Framework** | Python 3.12, Flask, Flask-SQLAlchemy, Flask-Login |
| **Machine Learning** | Scikit-Learn, Pandas, NumPy, Joblib |
| **Database** | SQLite (ORM designed for PostgreSQL / MySQL migration) |
| **PDF Generation** | ReportLab |

---

## 📁 Project Structure

```
SmartHealth AI/
├── app.py                      # Main Flask application entry point
├── config.py                   # Application environment configuration
├── requirements.txt            # Python dependency definitions
├── train_model.py              # ML dataset generation & model training script
├── README.md                   # Repository guide
├── PROJECT_REPORT.md           # 15-Chapter B.Tech Major Project Academic Thesis
│
├── dataset/
│   └── disease_symptom_dataset.csv  # Synthetic 2,240-row 32-disease multi-symptom dataset
│
├── models/                     # Saved Scikit-Learn ML artifacts
│   ├── disease_model.pkl       # Trained classifier (Logistic Regression - 97.1% F1)
│   ├── label_encoder.pkl       # Disease label encoder
│   ├── features.pkl            # 50-symptom feature vector list
│   └── metrics.pkl             # Comparative performance metrics
│
├── app/                        # Main Flask Package
│   ├── __init__.py             # Flask App Factory, Extensions & DB Seeding
│   ├── models/                 # SQLAlchemy DB Models (User, Symptom, Disease, Prediction)
│   ├── ml/                     # Inference engine & Explainable AI logic
│   ├── routes/                 # Blueprints (Main, Auth, Patient, Admin, API)
│   └── utils/                  # ReportLab PDF Generator & Admin Access Decorators
│
└── templates/                  # Jinja2 Modern Medical UI Templates
```

---

## 📊 Machine Learning Model Comparison

The system evaluates 5 distinct ML classifiers during training on the generated multi-symptom dataset:

| Model Algorithm | Accuracy | Precision | Recall | F1 Score | Status |
|---|---|---|---|---|---|
| **Logistic Regression** | **97.10%** | **97.46%** | **97.10%** | **97.10%** | 🏆 Selected Model |
| **Support Vector Machine (SVM)** | 96.21% | 96.66% | 96.21% | 96.20% | Evaluated |
| **Random Forest** | 95.31% | 95.62% | 95.31% | 95.30% | Evaluated |
| **Naive Bayes (MultinomialNB)** | 94.64% | 95.14% | 94.64% | 94.67% | Evaluated |
| **Decision Tree** | 81.92% | 83.33% | 81.92% | 81.79% | Evaluated |

---

## ⚡ Quick Setup & Running Instructions

### 1. Prerequisites
Ensure Python 3.10+ is installed on your machine.

### 2. Clone / Open Directory
```bash
cd "SmartHealth AI"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the ML Models
Run the training script to generate `dataset/disease_symptom_dataset.csv` and export model artifacts to `models/`:
```bash
python train_model.py
```

### 5. Launch Web Application
Start the Flask development server:
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Default Credentials

### Administrator Portal
* **URL:** `http://127.0.0.1:5000/admin/login`
* **Email:** `admin@smarthealth.ai`
* **Password:** `Admin@123`

### Patient Account
Create a new account at `http://127.0.0.1:5000/signup` or log in at `http://127.0.0.1:5000/login`.

---

## ⚠️ Medical Safety Disclaimer

> **IMPORTANT:** SmartHealth AI is designed purely as an educational decision-support tool. It does **NOT** provide a medical diagnosis, treatment plan, or prescription dosage. Always consult a qualified physician or healthcare provider for medical diagnosis and care. In case of acute or life-threatening symptoms (such as chest pain or breathing difficulty), seek immediate emergency services.
