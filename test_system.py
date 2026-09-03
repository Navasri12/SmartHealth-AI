import os
import sys

# Append project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Symptom, Disease, Prediction

def run_system_verification():
    print("=" * 60)
    print("      SMARTHEALTH AI - SYSTEM VERIFICATION TEST SUITE     ")
    print("=" * 60)
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    client = app.test_client()
    
    with app.app_context():
        # 1. Database & Seed verification
        user_count = User.query.count()
        symptom_count = Symptom.query.count()
        disease_count = Disease.query.count()
        
        print(f"[TEST 1] DB Seeding Check:")
        print(f"   - Users in DB: {user_count}")
        print(f"   - Symptoms in Catalog: {symptom_count}")
        print(f"   - Diseases in Knowledge Base: {disease_count}")
        assert symptom_count > 0, "Symptoms catalog is empty!"
        assert disease_count > 0, "Disease knowledge base is empty!"
        print("   -> PASSED [OK]\n")
        
        # 2. Public Landing Page Test
        res = client.get('/')
        print(f"[TEST 2] Public Landing Page (GET /): Status Code {res.status_code}")
        assert res.status_code == 200, "Home page failed to load!"
        print("   -> PASSED [OK]\n")
        
        # 3. Patient Registration Test
        test_email = "testpatient@smarthealth.ai"
        existing_test = User.query.filter_by(email=test_email).first()
        if existing_test:
            db.session.delete(existing_test)
            db.session.commit()
            
        signup_data = {
            'name': 'Test Patient',
            'email': test_email,
            'phone': '1234567890',
            'date_of_birth': '1995-05-15',
            'gender': 'Male',
            'password': 'TestPassword123',
            'confirm_password': 'TestPassword123',
            'height': '175',
            'weight': '70',
            'blood_group': 'O+',
            'allergies': 'None',
            'existing_conditions': 'None'
        }
        res = client.post('/signup', data=signup_data, follow_redirects=True)
        print(f"[TEST 3] Patient Registration (POST /signup): Status Code {res.status_code}")
        created_patient = User.query.filter_by(email=test_email).first()
        assert created_patient is not None, "Failed to register test patient!"
        print("   -> PASSED [OK]\n")
        
        # 4. Patient Login Test
        login_data = {
            'email': test_email,
            'password': 'TestPassword123'
        }
        res = client.post('/login', data=login_data, follow_redirects=True)
        print(f"[TEST 4] Patient Login (POST /login): Status Code {res.status_code}")
        assert b"Welcome back, Test Patient" in res.data, "Login failed to render patient dashboard!"
        print("   -> PASSED [OK]\n")

        # 5. Symptom Selector & ML Inference Test
        res = client.get('/patient/symptoms')
        print(f"[TEST 5] Symptom Selection Interface (GET /patient/symptoms): Status Code {res.status_code}")
        assert res.status_code == 200, "Symptom selection page failed to render!"
        
        # Post Symptoms (Fever, Cough, Fatigue)
        pred_data = {
            'symptoms': ['fever', 'cough', 'fatigue'],
            'severity_fever': 'Moderate',
            'duration_fever': '1-3 days',
            'severity_cough': 'Moderate',
            'duration_cough': '1-3 days',
            'severity_fatigue': 'Mild',
            'duration_fatigue': '1-3 days'
        }
        res = client.post('/patient/symptoms', data=pred_data, follow_redirects=True)
        print(f"[TEST 6] ML Prediction Execution (POST /patient/symptoms): Status Code {res.status_code}")
        assert b"AI Symptom Analysis & Risk Prediction" in res.data or b"Possible Health Condition" in res.data, "Prediction inference failed!"
        print("   -> PASSED [OK]\n")

        # 6. Patient Portal Navigation Tests
        res = client.get('/patient/dashboard')
        print(f"[TEST 7] Patient Dashboard (GET /patient/dashboard): Status Code {res.status_code}")
        assert res.status_code == 200, "Patient dashboard failed!"

        res = client.get('/patient/history')
        print(f"[TEST 8] Patient History (GET /patient/history): Status Code {res.status_code}")
        assert res.status_code == 200, "Patient history failed!"
        assert b"Assessment History" in res.data, "Patient history content missing!"

        res = client.get('/patient/analytics')
        print(f"[TEST 9] Patient Insights (GET /patient/analytics): Status Code {res.status_code}")
        assert res.status_code == 200, "Patient analytics failed!"
        assert b"Health Trend Analytics" in res.data, "Patient analytics content missing!"

        res = client.get('/patient/profile')
        print(f"[TEST 10] Patient Profile (GET /patient/profile): Status Code {res.status_code}")
        assert res.status_code == 200, "Patient profile failed!"
        assert b"Test Patient" in res.data, "Patient profile details missing!"
        print("   -> PASSED [OK]\n")

        # Logout Patient
        client.get('/logout', follow_redirects=True)

        # 7. Admin Authentication & Dashboard Tests
        admin_login = {
            'email': 'admin@smarthealth.ai',
            'password': 'Admin@123'
        }
        res = client.post('/admin/login', data=admin_login, follow_redirects=True)
        print(f"[TEST 11] Admin Login (POST /admin/login): Status Code {res.status_code}")
        assert b"Administrator Control Center" in res.data or b"System Analytics" in res.data, "Admin login failed!"

        res = client.get('/admin/users')
        print(f"[TEST 12] Admin Registered Patients List (GET /admin/users): Status Code {res.status_code}")
        assert res.status_code == 200, "Admin users list failed!"
        assert b"Test Patient" in res.data, "Registered patient missing from admin user list!"

        res = client.get('/admin/symptoms')
        print(f"[TEST 13] Admin Symptom Catalog (GET /admin/symptoms): Status Code {res.status_code}")
        assert res.status_code == 200, "Admin symptoms failed!"

        res = client.get('/admin/diseases')
        print(f"[TEST 14] Admin Disease Knowledge Base (GET /admin/diseases): Status Code {res.status_code}")
        assert res.status_code == 200, "Admin diseases failed!"

        res = client.get('/admin/ml_analytics')
        print(f"[TEST 15] Admin ML Analytics (GET /admin/ml_analytics): Status Code {res.status_code}")
        assert res.status_code == 200, "Admin ML analytics failed!"
        assert b"Logistic Regression" in res.data, "ML comparison table metrics missing!"
        print("   -> PASSED [OK]\n")

    print("=" * 60)
    print(" [SUCCESS] ALL 15 VERIFICATION TESTS COMPLETED SUCCESSFULLY! ")
    print("=" * 60)

if __name__ == '__main__':
    run_system_verification()
