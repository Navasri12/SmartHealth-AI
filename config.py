import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smarthealth-ai-secret-key-2026-btech-major-project'
    
    # Serverless Vercel filesystem adjustment (/tmp is writable)
    if IS_VERCEL:
        DB_PATH = os.path.join('/tmp', 'smarthealth.db')
        REPORTS_DIR = os.path.join('/tmp', 'reports')
    else:
        DB_PATH = os.path.join(BASE_DIR, 'instance', 'smarthealth.db')
        REPORTS_DIR = os.path.join(BASE_DIR, 'instance', 'reports')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ML Model Configuration
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    MODEL_VERSION = 'SmartHealth-AI-v1.0'
