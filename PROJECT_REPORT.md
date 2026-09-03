# B.TECH MAJOR PROJECT ACADEMIC REPORT

## Project Title
**SmartHealth AI – An Intelligent Symptom Analysis, Disease Prediction and Healthcare Support System Using Machine Learning**

---

### Abstract
Modern healthcare access remains uneven, with patients frequently struggling to interpret early physical symptoms or evaluate when professional medical intervention is required. This project presents **SmartHealth AI**, an intelligent decision-support web application designed to bridge the gap between initial symptom awareness and clinical care. Built using Python, Flask, SQLAlchemy, Scikit-Learn, and Chart.js, SmartHealth AI accepts multi-symptom inputs with severity and duration qualifiers, performs pre-prediction emergency safety screening, evaluates trained machine learning classifiers (Logistic Regression, Random Forest, SVM, Naive Bayes, Decision Tree), outputs top differential disease predictions with calibrated probabilities, provides Explainable AI (XAI) feature contribution visualizers, and generates downloadable ReportLab PDF health reports.

---

## Chapter 1: Introduction

### 1.1 Overview
Healthcare decision-making at the patient level often suffers from information asymmetry and anxiety-driven web searches. Individuals experiencing symptoms frequently turn to non-specialized search engines, resulting in either unneeded panic or dangerous delay in seeking emergency medical attention. **SmartHealth AI** offers a structured, data-driven alternative by applying supervised machine learning algorithms to categorized patient symptom inputs.

### 1.2 Motivation
With the rapid evolution of artificial intelligence and web technologies, building transparent, accessible, and safe medical decision-support systems has become a crucial milestone in digital health. The motivation behind SmartHealth AI is to deliver a reliable educational framework that prioritizes patient safety, explainability, and structured medical guidance while adhering strictly to ethical medical disclaimers.

---

## Chapter 2: Problem Statement

Patients lack immediate, structured tools to systematically evaluate their symptoms, understand potential underlying health conditions, receive transparent explanations for algorithmic assessments, and distinguish mild self-treatable conditions from acute medical emergencies. Existing web resources often lack severity weighting, explainable AI, integrated safety guardrails, or exportable consultation summaries for healthcare providers.

---

## Chapter 3: Existing System

### 3.1 Description of Traditional Methods
Traditional online symptom checkers primarily rely on static decision trees, manual rule-based IF-THEN lookup matrices, or generic keyword search engines.

### 3.2 Drawbacks of Existing Systems
1. **Lack of Machine Learning Adaptation**: Static rule engines cannot adapt to complex multi-symptom interactions or probabilistic confidence scores.
2. **Missing Severity & Duration Qualifiers**: Treat symptoms as binary (present/absent) without accounting for mild vs. severe intensity.
3. **Black-Box Predictions**: Fail to provide Explainable AI (XAI) feature importance breakdowns.
4. **Inadequate Emergency Safety Layer**: Often present predictions even when life-threatening emergency symptoms (e.g. chest pain, shortness of breath) are reported.
5. **No Exportable Reports**: Lack automated PDF summary generation for physician review.

---

## Chapter 4: Proposed System

**SmartHealth AI** resolves these limitations through an integrated architecture:
* **ML-Based Inference Engine**: Supervised multi-class classification predicting top 3 differential conditions with percentage confidence.
* **Pre-Prediction Emergency Guard**: Screens symptoms against critical red-flag rules to override standard prediction when urgent care is needed.
* **Explainable AI (XAI)**: Calculates symptom importance weights for transparency.
* **Severity & Duration Weighting**: Captures intensity and timeline parameters.
* **Dual Portals**: Dedicated Patient Portal (dashboard, history, analytics, PDF download) and Admin Portal (user management, symptom/disease CRUD, ML performance comparison).

---

## Chapter 5: System Requirements

### 5.1 Hardware Requirements
* **Processor**: Intel Core i3 / AMD Ryzen 3 or higher.
* **RAM**: 4 GB minimum (8 GB recommended).
* **Disk Space**: 500 MB free storage.

### 5.2 Software Requirements
* **Operating System**: Windows 10/11, macOS, or Linux.
* **Programming Language**: Python 3.10+
* **Framework**: Flask 3.0+
* **ML Libraries**: Scikit-Learn, Pandas, NumPy, Joblib
* **Database**: SQLite (SQLAlchemy ORM)
* **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js

---

## Chapter 6: System Architecture

```
                       ┌─────────────────────────┐
                       │  Patient / Admin UI     │
                       └────────────┬────────────┘
                                    │ HTTP / REST
                       ┌────────────▼────────────┐
                       │   Flask Application     │
                       └─────┬──────────────┬────┘
                             │              │
        ┌────────────────────▼──┐        ┌──▼────────────────────┐
        │ Emergency Safety Check │        │  ML Inference Engine  │
        └───────────────────────┘        │  (Logistic Reg / RF)  │
                                         └──────────┬────────────┘
                                                    │
                                         ┌──────────▼────────────┐
                                         │  SQLite Database &    │
                                         │  Model Artifacts .pkl │
                                         └───────────────────────┘
```

---

## Chapter 7: Methodology

1. **Dataset Construction**: Generating 2,240 realistic sample records across 32 medical conditions and 50 binary symptom features with introduced variation.
2. **Preprocessing & Encoding**: Label encoding of targets, feature vector normalization, 80/20 train-test splitting.
3. **Model Evaluation**: Training 5 classifiers (Random Forest, Decision Tree, Logistic Regression, Naive Bayes, SVM) and evaluating Accuracy, Precision, Recall, and F1 Score.
4. **Explainable AI Integration**: Extracting class coefficient vectors / feature importances to calculate percentage contributions.
5. **Report Generation**: Dynamically rendering ReportLab PDF documents containing demographics, symptoms, predictions, and disclaimers.

---

## Chapter 8: Machine Learning Model

### 8.1 Model Performance Results
Evaluating 5 classifiers produced the following metrics:

* **Logistic Regression**: **97.10% Accuracy | 97.46% Precision | 97.10% Recall | 97.10% F1 Score** (Selected Model)
* **Support Vector Machine (SVM)**: 96.21% Accuracy | 96.66% Precision | 96.21% Recall | 96.20% F1 Score
* **Random Forest**: 95.31% Accuracy | 95.62% Precision | 95.31% Recall | 95.30% F1 Score
* **Naive Bayes**: 94.64% Accuracy | 95.14% Precision | 94.64% Recall | 94.67% F1 Score
* **Decision Tree**: 81.92% Accuracy | 83.33% Precision | 81.92% Recall | 81.79% F1 Score

### 8.2 Selection Rationale
Logistic Regression achieved the highest weighted F1 score (97.10%) while offering high inference speed and mathematical transparency for Explainable AI coefficient extraction.

---

## Chapter 9: Database Design

The relational SQLite database consists of 7 core tables:
1. `users`: User identity, hashed passwords, roles (`patient`/`admin`), activity status.
2. `patient_profiles`: Height, weight, blood group, allergies, pre-existing conditions.
3. `symptoms`: Symptom catalog, category, description, emergency flags.
4. `diseases`: Educational condition details, prevention guidelines, recommendations.
5. `predictions`: Assessment records, predicted disease, probability, XAI JSON.
6. `prediction_symptoms`: Selected symptoms per assessment, severity, duration.
7. `model_metrics`: Saved ML evaluation metrics.

---

## Chapter 10: Implementation

The codebase is organized into modular blueprints (`auth`, `main`, `patient`, `admin`, `api`). Key implementation highlights include:
* **`train_model.py`**: Automated model training and `.pkl` artifact generation.
* **`app/ml/predictor.py`**: Prediction pipeline and Explainable AI weight calculator.
* **`app/utils/pdf_generator.py`**: ReportLab flowable PDF layout builder.
* **`static/js/main.js`**: Dynamic symptom filter and interactive checkbox controls.

---

## Chapter 11: Testing

### 11.1 Automated & Scripted Testing
* Executed dataset generation and model training scripts without errors.
* Verified DB schema creation and seeding routines.

### 11.2 Manual System Testing
* **Authentication**: Tested registration, patient login, admin authorization, and session invalidation.
* **Symptom Prediction**: Tested symptom selections (e.g. Fever + Cough) yielding Influenza / Respiratory predictions with ~90% confidence.
* **Emergency Override**: Verified selecting "Chest Pain" + "Shortness of Breath" triggers urgent care red alert.
* **PDF Download**: Verified generation of structured PDF assessment reports.

---

## Chapter 12: Results

SmartHealth AI successfully fulfills all functional and non-functional project objectives:
* Achieved 97.10% ML classification F1 score.
* Responsive, modern healthcare visual design system (Bootstrap 5 + custom CSS).
* Operational patient history, Chart.js analytics, and administrative management.

---

## Chapter 13: Limitations

1. **Synthetic Training Dataset**: The current model utilizes synthetic data designed for demonstration; real-world deployment requires validated clinical datasets (e.g. MIMIC-III).
2. **Non-Diagnostic Scope**: System outputs are limited to decision-support and educational recommendations.
3. **No Direct Telehealth**: Appointment booking and direct doctor messaging are not yet integrated.

---

## Chapter 14: Future Scope

* Integration of Large Language Model (LLM) natural language symptom description parsing.
* Wearable device IoT telemetry sync (heart rate, blood oxygen).
* Multilingual support for global accessibility.
* Mobile application development using Flutter / React Native.

---

## Chapter 15: Conclusion

**SmartHealth AI** successfully demonstrates the integration of machine learning classifiers, web application development, Explainable AI, and medical safety guardrails. The platform provides an intuitive, reliable, and educational decision-support environment for patients while delivering comprehensive administrative control and model transparency.
