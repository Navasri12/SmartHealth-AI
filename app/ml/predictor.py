import os
import joblib
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODEL_DIR = os.path.join(BASE_DIR, 'models')

EMERGENCY_SYMPTOMS = {
    'chest_pain': 'Chest Pain / Pressure (Possible cardiac emergency)',
    'shortness_of_breath': 'Severe Shortness of Breath / Breathing Difficulty',
    'high_fever': 'Critically High Fever with Disorientation',
    'loss_of_taste_smell': 'Acute Sudden Sensory Loss'
}

EMERGENCY_TRIGGERS = [
    {'symptoms': ['chest_pain', 'shortness_of_breath'], 'reason': 'Combination of acute chest pain and breathing difficulty requires immediate emergency medical evaluation.'},
    {'symptoms': ['chest_pain'], 'reason': 'Acute chest discomfort or pain can be an indicator of cardiovascular distress.'},
    {'symptoms': ['shortness_of_breath', 'wheezing', 'chest_tightness'], 'reason': 'Severe respiratory distress requires immediate urgent medical intervention.'}
]

class PredictorService:
    def __init__ (self):
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self.metrics = None
        self._load_artifacts()

    def _load_artifacts(self):
        model_path = os.path.join(MODEL_DIR, 'disease_model.pkl')
        encoder_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
        features_path = os.path.join(MODEL_DIR, 'features.pkl')
        metrics_path = os.path.join(MODEL_DIR, 'metrics.pkl')

        if os.path.exists(model_path) and os.path.exists(encoder_path) and os.path.exists(features_path):
            self.model = joblib.load(model_path)
            self.label_encoder = joblib.load(encoder_path)
            self.feature_names = joblib.load(features_path)
            if os.path.exists(metrics_path):
                self.metrics = joblib.load(metrics_path)
        else:
            print("[WARN] ML artifacts not found. Please run train_model.py first.")

    def check_emergency(self, selected_symptom_codes):
        """Evaluates whether selected symptoms trigger an emergency safety warning."""
        symptom_set = set(selected_symptom_codes)
        
        for rule in EMERGENCY_TRIGGERS:
            if all(s in symptom_set for s in rule['symptoms']):
                return {
                    'is_emergency': True,
                    'reason': rule['reason'],
                    'message': "CRITICAL WARNING: The combination of symptoms selected indicates potential urgent medical distress. Please call emergency services (e.g. 911 / local emergency number) or visit the nearest emergency department immediately. Do not rely solely on online prediction for acute or severe symptoms."
                }
        return {'is_emergency': False}

    def predict(self, selected_symptoms_dict):
        """
        selected_symptoms_dict: dict of {symptom_code: {'severity': 'Mild'/'Moderate'/'Severe', 'duration': '...'}}
        Returns dict with top predictions, XAI feature contributions, and emergency flag.
        """
        if not self.model or not self.feature_names:
            self._load_artifacts()
            if not self.model:
                raise RuntimeError("ML model artifacts are missing. Run train_model.py to initialize models.")

        selected_codes = list(selected_symptoms_dict.keys())
        
        # Check emergency safety layer
        emergency_status = self.check_emergency(selected_codes)
        if emergency_status['is_emergency']:
            return {
                'is_emergency': True,
                'emergency_info': emergency_status
            }

        # Build feature vector
        vector = np.zeros((1, len(self.feature_names)))
        for idx, feat in enumerate(self.feature_names):
            if feat in selected_symptoms_dict:
                # Apply slight severity weighting to input vector if needed
                vector[0, idx] = 1.0

        # Model Inference Probabilities
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(vector)[0]
        else:
            # Fallback for models without direct decision_function / predict_proba
            pred_idx = self.model.predict(vector)[0]
            probabilities = np.zeros(len(self.label_encoder.classes_))
            probabilities[pred_idx] = 1.0

        # Sort top 3 predictions
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_predictions = []
        for rank, idx in enumerate(top_indices):
            disease_name = self.label_encoder.inverse_transform([idx])[0]
            prob_pct = round(float(probabilities[idx]) * 100, 1)
            top_predictions.append({
                'rank': rank + 1,
                'disease': disease_name,
                'probability': prob_pct
            })

        primary_predicted_disease = top_predictions[0]['disease']
        primary_probability = top_predictions[0]['probability']

        # Explainable AI (XAI): Calculate feature contributions for selected symptoms
        xai_contributions = self._explain_prediction(selected_symptoms_dict, primary_predicted_disease)

        # Immediate Precautions & Next Steps
        immediate_precautions = self.get_immediate_precautions(primary_predicted_disease, selected_symptoms_dict)

        return {
            'is_emergency': False,
            'primary_disease': primary_predicted_disease,
            'probability': primary_probability,
            'top_predictions': top_predictions,
            'explainable_ai': xai_contributions,
            'immediate_precautions': immediate_precautions,
            'model_version': 'SmartHealth-AI-v1.0'
        }

    def get_immediate_precautions(self, disease_name, selected_symptoms_dict):
        """Generates dynamic immediate precautions & action steps for patient safety."""
        precautions = []
        
        # 1. Rest & Physical Exertion
        precautions.append({
            'icon': 'fa-bed',
            'title': 'Rest & Activity Reduction',
            'detail': 'Minimize physical strain and prioritize 7-9 hours of restorative sleep to assist immune recovery.'
        })

        # 2. Fluid Intake & Hydration
        precautions.append({
            'icon': 'fa-glass-water',
            'title': 'Continuous Hydration',
            'detail': 'Sip water, warm broths, or oral rehydration fluids continuously (2-3 liters/day) to prevent dehydration.'
        })

        # 3. Vital Sign & Progression Logging
        has_fever = any('fever' in code for code in selected_symptoms_dict.keys())
        if has_fever:
            precautions.append({
                'icon': 'fa-thermometer',
                'title': 'Temperature & Vital Monitoring',
                'detail': 'Record body temperature every 4-6 hours using a digital thermometer. Note peak readings and fever spikes.'
            })
        else:
            precautions.append({
                'icon': 'fa-clipboard-list',
                'title': 'Symptom Journaling',
                'detail': 'Document any new or changing symptoms twice daily to share with your healthcare practitioner.'
            })

        # 4. Infection Control & Exposure Minimization
        resp_diseases = ['Influenza', 'Common Cold', 'COVID-19', 'Bronchitis', 'Pneumonia', 'Sinusitis']
        if disease_name in resp_diseases:
            precautions.append({
                'icon': 'fa-mask-face',
                'title': 'Infection Isolation & Hygiene',
                'detail': 'Wear a face mask in shared household spaces, maintain room ventilation, and sanitize hands regularly.'
            })
        else:
            precautions.append({
                'icon': 'fa-apple-whole',
                'title': 'Nutrition & Avoidance',
                'detail': 'Eat light, easily digestible meals. Avoid heavy, greasy, spicy, or caffeinated foods during recovery.'
            })

        # 5. Clinical Consultation Schedule
        has_severe = any(d.get('severity') == 'Severe' for d in selected_symptoms_dict.values())
        if has_severe:
            precautions.append({
                'icon': 'fa-user-doctor',
                'title': 'Prompt Medical Evaluation',
                'detail': 'Due to severe symptom intensity, schedule an appointment with a primary care physician within 24-48 hours.'
            })
        else:
            precautions.append({
                'icon': 'fa-user-doctor',
                'title': 'Clinical Follow-up Timing',
                'detail': 'If symptoms persist beyond 3-5 days or fail to improve with rest, consult a qualified healthcare provider.'
            })

        return precautions


    def _explain_prediction(self, selected_symptoms_dict, predicted_disease):
        """Generates explainable AI feature contribution weights for selected symptoms."""
        contributions = []
        selected_codes = list(selected_symptoms_dict.keys())
        
        if not selected_codes:
            return contributions

        # Check model coefficients or feature importances if available
        if hasattr(self.model, 'coef_'): # Logistic Regression
            disease_idx = list(self.label_encoder.classes_).index(predicted_disease)
            coefs = self.model.coef_[disease_idx]
            weights = []
            for code in selected_codes:
                if code in self.feature_names:
                    f_idx = self.feature_names.index(code)
                    weights.append(max(0.01, float(coefs[f_idx])))
                else:
                    weights.append(0.1)
            
            total_w = sum(weights) or 1.0
            for code, w in zip(selected_codes, weights):
                impact_pct = round((w / total_w) * 100, 1)
                contributions.append({
                    'symptom_code': code,
                    'symptom_name': code.replace('_', ' ').title(),
                    'importance_pct': max(5.0, impact_pct)
                })

        elif hasattr(self.model, 'feature_importances_'): # Random Forest / Decision Tree
            importances = self.model.feature_importances_
            weights = []
            for code in selected_codes:
                if code in self.feature_names:
                    f_idx = self.feature_names.index(code)
                    weights.append(max(0.01, float(importances[f_idx])))
                else:
                    weights.append(0.1)
            total_w = sum(weights) or 1.0
            for code, w in zip(selected_codes, weights):
                impact_pct = round((w / total_w) * 100, 1)
                contributions.append({
                    'symptom_code': code,
                    'symptom_name': code.replace('_', ' ').title(),
                    'importance_pct': max(5.0, impact_pct)
                })

        else: # Heuristic fallback
            equal_pct = round(100.0 / len(selected_codes), 1)
            for code in selected_codes:
                contributions.append({
                    'symptom_code': code,
                    'symptom_name': code.replace('_', ' ').title(),
                    'importance_pct': equal_pct
                })

        # Normalize contribution percentages to sum to 100%
        total = sum(item['importance_pct'] for item in contributions)
        if total > 0:
            for item in contributions:
                item['importance_pct'] = round((item['importance_pct'] / total) * 100, 1)

        # Sort descending by importance
        contributions.sort(key=lambda x: x['importance_pct'], reverse=True)
        return contributions

# Global instance
predictor_service = PredictorService()
