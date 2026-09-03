from datetime import datetime
from app import db

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    predicted_disease = db.Column(db.String(120), nullable=False)
    probability = db.Column(db.Float, nullable=False) # e.g. 86.5
    top_predictions_json = db.Column(db.Text, nullable=True) # JSON of top 3
    explainable_ai_json = db.Column(db.Text, nullable=True) # JSON of feature contributions
    model_version = db.Column(db.String(50), default='SmartHealth-AI-v1.0')
    severity_score = db.Column(db.String(50), default='Moderate')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    selected_symptoms = db.relationship('PredictionSymptom', backref='prediction', lazy='joined', cascade='all, delete-orphan')

class PredictionSymptom(db.Model):
    __tablename__ = 'prediction_symptoms'
    
    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptoms.id'), nullable=True)
    symptom_code = db.Column(db.String(100), nullable=False)
    symptom_name = db.Column(db.String(120), nullable=False)
    severity = db.Column(db.String(30), default='Moderate') # Mild, Moderate, Severe
    duration = db.Column(db.String(50), default='1-3 days')

class ModelMetric(db.Model):
    __tablename__ = 'model_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(80), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    is_best = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
