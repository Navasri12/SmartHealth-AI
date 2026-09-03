import os, sys

# Ensure root directory is on Python module search path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Auto-train model if binary artifacts are missing on serverless container
model_file = os.path.join(BASE_DIR, 'models', 'disease_model.pkl')
if not os.path.exists(model_file):
    try:
        from train_model import train_and_evaluate
        train_and_evaluate()
    except Exception as e:
        print(f"[VERCEL INITIALIZATION] Model auto-train notice: {e}")

from app import create_app

app = create_app()
