from datetime import datetime
from app import db

class Symptom(db.Model):
    __tablename__ = 'symptoms'
    
    id = db.Column(db.Integer, primary_key=True)
    code_name = db.Column(db.String(100), unique=True, nullable=False) # e.g., 'fever'
    name = db.Column(db.String(120), nullable=False)                    # e.g., 'Fever'
    category = db.Column(db.String(50), nullable=False, default='General')
    description = db.Column(db.Text, nullable=True)
    is_emergency = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

class Disease(db.Model):
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General')
    description = db.Column(db.Text, nullable=False)
    common_symptoms = db.Column(db.Text, nullable=True)
    prevention = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    warning_signs = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
