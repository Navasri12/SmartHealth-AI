import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smarthealth-ai-secret-key-2026-btech-major-project'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'smarthealth.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ML Model Configuration
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    MODEL_VERSION = 'SmartHealth-AI-v1.0'
    
    # PDF Uploads / Reports
    REPORTS_DIR = os.path.join(BASE_DIR, 'instance', 'reports')
