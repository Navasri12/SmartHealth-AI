import os, json
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User, PatientProfile
from app.models.medical import Symptom, Disease
from app.models.prediction import Prediction, PredictionSymptom
from app.ml.predictor import predictor_service
from app.utils.pdf_generator import generate_prediction_pdf

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
        
    predictions_query = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc())
    total_predictions = predictions_query.count()
    recent_predictions = predictions_query.limit(5).all()
    latest_prediction = recent_predictions[0] if recent_predictions else None
    
    # Calculate health risk index
    risk_level = "Low"
    if latest_prediction:
        if latest_prediction.probability > 85.0 and latest_prediction.severity_score == 'High':
            risk_level = "High Risk"
        elif latest_prediction.probability > 70.0:
            risk_level = "Moderate"
        else:
            risk_level = "Low Risk"

    return render_template(
        'patient/dashboard.html',
        total_predictions=total_predictions,
        latest_prediction=latest_prediction,
        recent_predictions=recent_predictions,
        risk_level=risk_level
    )

@patient_bp.route('/symptoms', methods=['GET', 'POST'])
@login_required
def symptoms():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        # Selected symptoms format: dict of {symptom_code: {'severity': val, 'duration': val}}
        selected_codes = request.form.getlist('symptoms')
        if not selected_codes:
            flash('Please select at least one symptom to run the AI prediction model.', 'warning')
            return redirect(url_for('patient.symptoms'))

        symptoms_dict = {}
        has_severe = False
        
        for code in selected_codes:
            sev = request.form.get(f'severity_{code}', 'Moderate')
            dur = request.form.get(f'duration_{code}', '1-3 days')
            if sev == 'Severe':
                has_severe = True
            symptoms_dict[code] = {'severity': sev, 'duration': dur}

        # ML Predictor Execution
        res = predictor_service.predict(symptoms_dict)

        # Handle Emergency Warning
        if res.get('is_emergency'):
            return render_template(
                'patient/prediction.html',
                is_emergency=True,
                emergency_info=res['emergency_info']
            )

        # Calculate severity score
        overall_severity = 'High' if has_severe or res['probability'] > 85.0 else 'Moderate'

        # Fetch disease educational information
        disease_info = Disease.query.filter_by(name=res['primary_disease']).first()

        # Save Prediction Record to Database
        pred_record = Prediction(
            user_id=current_user.id,
            predicted_disease=res['primary_disease'],
            probability=res['probability'],
            top_predictions_json=json.dumps(res['top_predictions']),
            explainable_ai_json=json.dumps(res['explainable_ai']),
            model_version=res['model_version'],
            severity_score=overall_severity
        )
        db.session.add(pred_record)
        db.session.flush() # Get pred_record.id

        # Save selected symptoms details
        for code, details in symptoms_dict.items():
            sym_obj = Symptom.query.filter_by(code_name=code).first()
            ps = PredictionSymptom(
                prediction_id=pred_record.id,
                symptom_id=sym_obj.id if sym_obj else None,
                symptom_code=code,
                symptom_name=sym_obj.name if sym_obj else code.replace('_', ' ').title(),
                severity=details['severity'],
                duration=details['duration']
            )
            db.session.add(ps)

        db.session.commit()
        return redirect(url_for('patient.view_prediction', prediction_id=pred_record.id))

    # GET Request: Group symptoms by category
    all_symptoms = Symptom.query.filter_by(active=True).order_by(Symptom.category, Symptom.name).all()
    categorized_symptoms = {}
    for s in all_symptoms:
        categorized_symptoms.setdefault(s.category, []).append(s)

    return render_template('patient/symptoms.html', categorized_symptoms=categorized_symptoms)

@patient_bp.route('/prediction/<int:prediction_id>')
@login_required
def view_prediction(prediction_id):
    pred = Prediction.query.get_or_404(prediction_id)
    if pred.user_id != current_user.id and not current_user.is_admin():
        flash('Access restricted.', 'danger')
        return redirect(url_for('patient.dashboard'))

    disease_info = Disease.query.filter_by(name=pred.predicted_disease).first()
    top_predictions = json.loads(pred.top_predictions_json) if pred.top_predictions_json else []
    explainable_ai = json.loads(pred.explainable_ai_json) if pred.explainable_ai_json else []

    selected_symptoms_dict = {
        ps.symptom_code: {'severity': ps.severity, 'duration': ps.duration}
        for ps in pred.selected_symptoms
    }
    immediate_precautions = predictor_service.get_immediate_precautions(pred.predicted_disease, selected_symptoms_dict)

    return render_template(
        'patient/prediction.html',
        is_emergency=False,
        prediction=pred,
        disease_info=disease_info,
        top_predictions=top_predictions,
        explainable_ai=explainable_ai,
        immediate_precautions=immediate_precautions
    )


@patient_bp.route('/history')
@login_required
def history():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    return render_template('patient/history.html', predictions=predictions)

@patient_bp.route('/analytics')
@login_required
def analytics():
    # Fetch all user predictions
    user_preds = Prediction.query.filter_by(user_id=current_user.id).all()
    
    # Calculate symptom frequency
    symptom_counts = {}
    disease_counts = {}
    
    for p in user_preds:
        disease_counts[p.predicted_disease] = disease_counts.get(p.predicted_disease, 0) + 1
        for ps in p.selected_symptoms:
            symptom_counts[ps.symptom_name] = symptom_counts.get(ps.symptom_name, 0) + 1
            
    # Sort top symptoms
    top_symptoms = sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    top_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:6]

    return render_template(
        'patient/analytics.html',
        total_assessments=len(user_preds),
        top_symptoms=top_symptoms,
        top_diseases=top_diseases,
        symptom_labels=[x[0] for x in top_symptoms],
        symptom_data=[x[1] for x in top_symptoms],
        disease_labels=[x[0] for x in top_diseases],
        disease_data=[x[1] for x in top_diseases]
    )

@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    prof = PatientProfile.query.filter_by(user_id=user.id).first()
    
    if request.method == 'POST':
        user.name = request.form.get('name', '').strip()
        user.phone = request.form.get('phone', '').strip()
        user.date_of_birth = request.form.get('date_of_birth', '').strip()
        user.gender = request.form.get('gender', '').strip()

        if not prof:
            prof = PatientProfile(user_id=user.id)
            db.session.add(prof)

        h_val = request.form.get('height')
        w_val = request.form.get('weight')
        prof.height = float(h_val) if h_val and h_val.strip() else None
        prof.weight = float(w_val) if w_val and w_val.strip() else None
        prof.blood_group = request.form.get('blood_group')
        prof.allergies = request.form.get('allergies', '').strip()
        prof.existing_conditions = request.form.get('existing_conditions', '').strip()

        db.session.commit()
        flash('Medical profile updated successfully.', 'success')
        return redirect(url_for('patient.profile'))

    return render_template('patient/profile.html', user=user, profile=prof)

@patient_bp.route('/report/<int:prediction_id>/pdf')
@login_required
def download_pdf(prediction_id):
    pred = Prediction.query.get_or_404(prediction_id)
    if pred.user_id != current_user.id and not current_user.is_admin():
        flash('Access restricted.', 'danger')
        return redirect(url_for('patient.dashboard'))

    disease_info = Disease.query.filter_by(name=pred.predicted_disease).first()
    prof = PatientProfile.query.filter_by(user_id=current_user.id).first()

    reports_dir = current_app.config['REPORTS_DIR']
    try:
        os.makedirs(reports_dir, exist_ok=True)
    except Exception:
        pass
    pdf_filename = f"SmartHealth_Assessment_{pred.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_filename)


    generate_prediction_pdf(pred, current_user, prof, disease_info, pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
