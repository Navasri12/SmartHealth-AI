from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Administrator privileges are required to access this resource.', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def seed_database(db):
    """Populates database with default admin, symptoms, disease knowledge base, and model metrics."""
    from app.models.user import User
    from app.models.medical import Symptom, Disease
    from app.models.prediction import ModelMetric
    import os, joblib

    # 1. Create Default Admin User
    admin = User.query.filter_by(email='admin@smarthealth.ai').first()
    if not admin:
        admin = User(
            name='System Administrator',
            email='admin@smarthealth.ai',
            role='admin',
            phone='+1-800-SMART-HEALTH'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        print("[SEED] Created default admin account: admin@smarthealth.ai")

    # 2. Seed Symptoms
    if Symptom.query.count() == 0:
        symptom_catalog = [
            # General
            ('fever', 'Fever', 'General', 'Elevated body temperature above normal range (98.6°F / 37°C)', False),
            ('high_fever', 'High Fever (>102°F)', 'General', 'Critically elevated body temperature requiring close monitoring', False),
            ('prolonged_fever', 'Prolonged Fever', 'General', 'Fever persisting continuously for more than 3-4 days', False),
            ('chills', 'Chills & Shivering', 'General', 'Sensation of cold accompanied by involuntary shivering', False),
            ('fatigue', 'Fatigue & Lethargy', 'General', 'Persistent physical exhaustion or lack of energy', False),
            ('weakness', 'General Body Weakness', 'General', 'Reduced physical muscle strength or stamina', False),
            ('sweating', 'Excessive Sweating', 'General', 'Unusual or profuse perspiration not related to exercise', False),
            ('weight_gain', 'Unexplained Weight Gain', 'General', 'Rapid or unexpected increase in body weight', False),
            ('weight_loss', 'Unexplained Weight Loss', 'General', 'Significant unintentional drop in body weight', False),

            # Respiratory
            ('cough', 'Cough', 'Respiratory', 'Reflex action to clear airways of irritants or mucus', False),
            ('sore_throat', 'Sore Throat', 'Respiratory', 'Pain, scratchiness, or irritation in the throat', False),
            ('sneezing', 'Frequent Sneezing', 'Respiratory', 'Involuntary expulsion of air from nose', False),
            ('runny_nose', 'Runny Nose (Rhinorrhea)', 'Respiratory', 'Excess nasal fluid discharge', False),
            ('nasal_congestion', 'Nasal Congestion', 'Respiratory', 'Stuffy nose due to swollen nasal blood vessels', False),
            ('shortness_of_breath', 'Shortness of Breath', 'Respiratory', 'Difficulty breathing or feeling winded', True),
            ('wheezing', 'Wheezing', 'Respiratory', 'High-pitched whistling sound during breathing', False),
            ('chest_tightness', 'Chest Tightness', 'Respiratory', 'Constrictive sensation in the chest area', False),
            ('mucus_production', 'Mucus / Phlegm Production', 'Respiratory', 'Coughing up thick mucus or sputum', False),

            # Cardiovascular / Chest
            ('chest_pain', 'Chest Pain / Discomfort', 'Cardiovascular', 'Pain or uncomfortable pressure in the chest area', True),
            ('chest_discomfort', 'Mild Chest Discomfort', 'Cardiovascular', 'Slight pressure or discomfort in upper torso', False),
            ('heartburn', 'Heartburn / Acid Reflux', 'Cardiovascular', 'Burning sensation in the chest behind the breastbone', False),

            # Digestive
            ('nausea', 'Nausea', 'Digestive', 'Sensation of unease in stomach with urge to vomit', False),
            ('vomiting', 'Vomiting', 'Digestive', 'Forceful discharge of stomach contents', False),
            ('diarrhea', 'Diarrhea', 'Digestive', 'Loose, watery stool occurrences', False),
            ('abdominal_pain', 'Abdominal Pain / Cramps', 'Digestive', 'Pain localized in the stomach or gut region', False),

            # Neurological
            ('headache', 'Headache', 'Neurological', 'Pain in the head, upper neck, or scalp', False),
            ('muscle_pain', 'Muscle Pain (Myalgia)', 'Neurological', 'Aches or soreness across muscle groups', False),
            ('body_ache', 'Generalized Body Ache', 'Neurological', 'Widespread musculoskeletal discomfort', False),
            ('dizziness', 'Dizziness / Lightheadedness', 'Neurological', 'Feeling unsteady or faint', False),
            ('sensitivity_to_light', 'Sensitivity to Light (Photophobia)', 'Neurological', 'Discomfort or intolerance to bright light', False),
            ('sensitivity_to_sound', 'Sensitivity to Sound (Phonophobia)', 'Neurological', 'Heightened sensitivity to noise', False),
            ('blurred_vision', 'Blurred Vision', 'Neurological', 'Lack of sharp visual acuity', False),
            ('loss_of_taste_smell', 'Loss of Taste or Smell', 'Neurological', 'Partial or total loss of gustatory and olfactory senses', False),
            ('neck_pain', 'Neck Stiffness / Pain', 'Neurological', 'Discomfort moving or bending the neck', False),

            # Urinary / Endocrine
            ('frequent_urination', 'Frequent Urination', 'Urinary', 'Need to urinate more often than usual', False),
            ('painful_urination', 'Painful Urination (Dysuria)', 'Urinary', 'Burning sensation during urination', False),
            ('cloudy_urine', 'Cloudy Urine', 'Urinary', 'Turbid or opaque urine appearance', False),
            ('excessive_thirst', 'Excessive Thirst (Polydipsia)', 'Endocrine', 'Abnormal feeling of dehydration', False),
            ('slow_wound_healing', 'Slow Wound Healing', 'Endocrine', 'Cuts or sores taking unusually long to heal', False),

            # Skin / Eyes
            ('skin_rash', 'Skin Rash', 'Skin', 'Noticeable change in texture or color of skin', False),
            ('itchy_skin', 'Itchy Skin (Pruritus)', 'Skin', 'Irritating sensation causing urge to scratch', False),
            ('dry_skin', 'Dry / Flaky Skin', 'Skin', 'Rough or scaling skin texture', False),
            ('rash', 'Red Skin Patches / Spots', 'Skin', 'Localized red spots or macules', False),
            ('pale_skin', 'Pale Skin / Paleness', 'Skin', 'Abnormally light skin complexion', False),
            ('itchy_eyes', 'Itchy / Red Eyes', 'Eyes', 'Ocular irritation and redness', False),
            ('watery_eyes', 'Watery Eyes (Lachrymation)', 'Eyes', 'Excessive tearing of eyes', False),

            # Musculoskeletal
            ('joint_pain', 'Joint Pain (Arthralgia)', 'Musculoskeletal', 'Discomfort in one or more joints', False),
            ('joint_swelling', 'Joint Swelling', 'Musculoskeletal', 'Enlargement or fluid accumulation at joints', False),
            ('joint_stiffness', 'Joint Stiffness', 'Musculoskeletal', 'Difficulty moving joints, especially in morning', False),

            # Mental
            ('anxiety', 'Anxiety / Nervousness', 'Mental', 'Apprehension, tension, or racing thoughts', False)
        ]

        for code, name, cat, desc, is_emerg in symptom_catalog:
            sym = Symptom(code_name=code, name=name, category=cat, description=desc, is_emergency=is_emerg)
            db.session.add(sym)
        print("[SEED] Inserted default symptoms catalog.")

    # 3. Seed Diseases Knowledge Base
    if Disease.query.count() == 0:
        disease_catalog = [
            {
                'name': 'Influenza',
                'category': 'Respiratory',
                'description': 'A contagious viral respiratory infection affecting the nose, throat, and lungs.',
                'common_symptoms': 'Fever, Cough, Sore Throat, Muscle Aches, Fatigue, Headache, Chills.',
                'prevention': 'Annual flu vaccination, frequent handwashing, avoiding close contact with sick individuals.',
                'recommendations': 'Rest adequately, stay well hydrated, monitor temperature, use over-the-counter fever reducers if appropriate.',
                'warning_signs': 'Difficulty breathing, persistent chest pain, confusion, severe weakness.'
            },
            {
                'name': 'Common Cold',
                'category': 'Respiratory',
                'description': 'A mild viral infection of the upper respiratory tract involving the nose and throat.',
                'common_symptoms': 'Runny nose, Sneezing, Cough, Nasal Congestion, Sore Throat.',
                'prevention': 'Wash hands regularly, keep hands away from face, sanitize touched surfaces.',
                'recommendations': 'Drink warm liquids, rest, use saline nasal sprays or throat lozenges.',
                'warning_signs': 'Symptoms lasting over 10 days, severe ear pain, high fever.'
            },
            {
                'name': 'COVID-19',
                'category': 'Respiratory',
                'description': 'An infectious respiratory illness caused by the SARS-CoV-2 coronavirus.',
                'common_symptoms': 'Fever, Dry Cough, Loss of Taste/Smell, Fatigue, Shortness of Breath, Sore Throat.',
                'prevention': 'Vaccination, wearing masks in crowded indoor spaces, good ventilation, hand hygiene.',
                'recommendations': 'Isolate to prevent spread, monitor blood oxygen levels, maintain fluid intake.',
                'warning_signs': 'Low oxygen saturation (<94%), severe shortness of breath, persistent chest pain.'
            },
            {
                'name': 'Asthma',
                'category': 'Respiratory',
                'description': 'A chronic condition in which airways narrow, swell, and produce extra mucus.',
                'common_symptoms': 'Shortness of Breath, Wheezing, Chest Tightness, Coughing.',
                'prevention': 'Avoid known asthma triggers (pollen, dust, smoke, cold air), manage environmental allergens.',
                'recommendations': 'Keep prescribed rescue inhalers accessible, follow asthma action plan, practice breathing exercises.',
                'warning_signs': 'Severe breathlessness unresponsive to rescue inhaler, bluish lips/nails.'
            },
            {
                'name': 'Pneumonia',
                'category': 'Respiratory',
                'description': 'An infection that inflames air sacs in one or both lungs, which may fill with fluid or pus.',
                'common_symptoms': 'High Fever, Chest Pain when breathing/coughing, Productive Cough, Shortness of Breath, Chills.',
                'prevention': 'Pneumococcal vaccination, flu vaccination, non-smoking, proper oral hygiene.',
                'recommendations': 'Seek prompt professional medical evaluation. Rest, consume warm fluids, take prescribed antibiotics/antivirals if instructed by a doctor.',
                'warning_signs': 'Bluish skin/lips, high fever with shaking chills, confusion in older adults.'
            },
            {
                'name': 'GERD',
                'category': 'Digestive',
                'description': 'Gastroesophageal Reflux Disease occurs when stomach acid frequently flows back into the tube connecting mouth and stomach.',
                'common_symptoms': 'Heartburn, Regurgitation, Chest Discomfort, Difficulty Swallowing.',
                'prevention': 'Avoid trigger foods (spicy, fatty, caffeine), eat smaller meals, avoid lying down within 3 hours of eating.',
                'recommendations': 'Elevate the head of your bed, maintain healthy body weight, refrain from smoking.',
                'warning_signs': 'Difficulty swallowing (dysphagia), unexplained weight loss, vomiting blood.'
            },
            {
                'name': 'Gastroenteritis',
                'category': 'Digestive',
                'description': 'Intestinal infection marked by watery diarrhea, abdominal cramps, nausea, or vomiting.',
                'common_symptoms': 'Abdominal Pain, Nausea, Vomiting, Diarrhea, Mild Fever, Fatigue.',
                'prevention': 'Practice strict food hygiene, drink clean purified water, wash hands thoroughly after restroom use.',
                'recommendations': 'Sip oral rehydration solutions (ORS), eat bland foods (BRAT diet), avoid dairy/spicy foods.',
                'warning_signs': 'Signs of severe dehydration (extreme thirst, dry mouth, dark urine), blood in stool.'
            },
            {
                'name': 'Migraine',
                'category': 'Neurological',
                'description': 'A neurological condition characterized by intense, throbbing headaches usually on one side of the head.',
                'common_symptoms': 'Severe Headache, Nausea, Light Sensitivity, Sound Sensitivity, Dizziness, Visual Aura.',
                'prevention': 'Identify and avoid personal triggers (flickering light, stress, specific foods, sleep lack).',
                'recommendations': 'Rest in a quiet, dark room; apply cold compress to forehead; stay hydrated.',
                'warning_signs': 'Sudden "thunderclap" headache, headache with high fever, neck stiffness, weakness.'
            },
            {
                'name': 'Type 2 Diabetes',
                'category': 'Endocrine',
                'description': 'A metabolic disorder characterized by high blood glucose levels resulting from insulin resistance.',
                'common_symptoms': 'Excessive Thirst, Frequent Urination, Fatigue, Blurred Vision, Slow Wound Healing.',
                'prevention': 'Maintain healthy diet low in refined sugars, exercise regularly, maintain optimal body weight.',
                'recommendations': 'Monitor blood sugar levels as advised by your physician, stay active, follow balanced meal plans.',
                'warning_signs': 'Extreme lethargy, fruity breath odor, rapid breathing, loss of consciousness.'
            },
            {
                'name': 'Hypertension',
                'category': 'Cardiovascular',
                'description': 'A chronic condition where the force of the blood against artery walls is consistently too high.',
                'common_symptoms': 'Often asymptomatic; may cause Dizziness, Headache, Blurred Vision, Chest Discomfort.',
                'prevention': 'Reduce sodium intake, exercise 150 mins/week, limit alcohol, manage stress.',
                'recommendations': 'Monitor blood pressure regularly, maintain low-sodium diet, consult doctor for blood pressure management.',
                'warning_signs': 'Severe sudden headache, chest pain, numbness/weakness on one side of body.'
            }
        ]

        for d_data in disease_catalog:
            d = Disease(**d_data)
            db.session.add(d)
        print("[SEED] Inserted default disease knowledge base entries.")

    # 4. Seed Model Metrics from metrics.pkl if available
    if ModelMetric.query.count() == 0:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        metrics_path = os.path.join(base_dir, 'models', 'metrics.pkl')
        if os.path.exists(metrics_path):
            data = joblib.load(metrics_path)
            best_name = data.get('best_model_name')
            for m in data.get('metrics', []):
                mm = ModelMetric(
                    model_name=m['model_name'],
                    accuracy=m['accuracy'],
                    precision=m['precision'],
                    recall=m['recall'],
                    f1_score=m['f1_score'],
                    is_best=(m['model_name'] == best_name)
                )
                db.session.add(mm)
            print("[SEED] Inserted ML model comparison metrics into database.")

    db.session.commit()
