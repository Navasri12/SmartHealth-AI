import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smarthealth-ai-secret-key-2026-btech-major-project'
    
    # Session Cookie Security for Serverless Deployment
    SESSION_COOKIE_NAME = 'smarthealth_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400 * 30  # 30 Days
    
    # Remote Database URL (PostgreSQL / Supabase / Neon) or Serverless /tmp SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        DB_PATH = None
        REPORTS_DIR = os.path.join('/tmp', 'reports') if IS_VERCEL else os.path.join(BASE_DIR, 'instance', 'reports')
    elif IS_VERCEL:
        DB_PATH = os.path.join('/tmp', 'smarthealth.db')
        REPORTS_DIR = os.path.join('/tmp', 'reports')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    else:
        DB_PATH = os.path.join(BASE_DIR, 'instance', 'smarthealth.db')
        REPORTS_DIR = os.path.join(BASE_DIR, 'instance', 'reports')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ML Model Configuration
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    MODEL_VERSION = 'SmartHealth-AI-v1.0'
