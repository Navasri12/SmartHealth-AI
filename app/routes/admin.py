import os, joblib
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User, PatientProfile
from app.models.medical import Symptom, Disease
from app.models.prediction import Prediction, PredictionSymptom, ModelMetric
from app.utils.helpers import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_patients = User.query.filter_by(role='patient').count()
    total_predictions = Prediction.query.count()
    total_symptoms = Symptom.query.count()
    total_diseases = Disease.query.count()

    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(8).all()
    
    # Calculate disease distribution for admin charts
    disease_counts = {}
    preds = Prediction.query.all()
    for p in preds:
        disease_counts[p.predicted_disease] = disease_counts.get(p.predicted_disease, 0) + 1
        
    top_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return render_template(
        'admin/dashboard.html',
        total_patients=total_patients,
        total_predictions=total_predictions,
        total_symptoms=total_symptoms,
        total_diseases=total_diseases,
        recent_predictions=recent_predictions,
        top_diseases=top_diseases,
        disease_labels=[x[0] for x in top_diseases],
        disease_data=[x[1] for x in top_diseases]
    )

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='patient')
    if search:
        query = query.filter((User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%")))
    patients = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', patients=patients, search=search)

@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('Cannot deactivate an administrator account.', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    flash(f"Patient account for {user.name} has been {status_str}.", 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/symptoms', methods=['GET', 'POST'])
@login_required
@admin_required
def symptoms():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code_name = request.form.get('code_name', '').strip().lower().replace(' ', '_')
        category = request.form.get('category', 'General').strip()
        description = request.form.get('description', '').strip()
        is_emergency = True if request.form.get('is_emergency') else False

        if not name or not code_name:
            flash('Symptom Name and Code Name are required.', 'danger')
            return redirect(url_for('admin.symptoms'))

        existing = Symptom.query.filter_by(code_name=code_name).first()
        if existing:
            flash('A symptom with this code name already exists.', 'warning')
            return redirect(url_for('admin.symptoms'))

        sym = Symptom(
            name=name,
            code_name=code_name,
            category=category,
            description=description,
            is_emergency=is_emergency,
            active=True
        )
        db.session.add(sym)
        db.session.commit()
        flash(f"Symptom '{name}' added successfully.", 'success')
        return redirect(url_for('admin.symptoms'))

    symptom_list = Symptom.query.order_by(Symptom.category, Symptom.name).all()
    return render_template('admin/symptoms.html', symptoms=symptom_list)

@admin_bp.route('/diseases', methods=['GET', 'POST'])
@login_required
@admin_required
def diseases():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', 'General').strip()
        description = request.form.get('description', '').strip()
        common_symptoms = request.form.get('common_symptoms', '').strip()
        prevention = request.form.get('prevention', '').strip()
        recommendations = request.form.get('recommendations', '').strip()
        warning_signs = request.form.get('warning_signs', '').strip()

        if not name or not description:
            flash('Disease Name and Description are required.', 'danger')
            return redirect(url_for('admin.diseases'))

        disease = Disease.query.filter_by(name=name).first()
        if not disease:
            disease = Disease(name=name)
            db.session.add(disease)

        disease.category = category
        disease.description = description
        disease.common_symptoms = common_symptoms
        disease.prevention = prevention
        disease.recommendations = recommendations
        disease.warning_signs = warning_signs

        db.session.commit()
        flash(f"Disease entry for '{name}' saved successfully.", 'success')
        return redirect(url_for('admin.diseases'))

    disease_list = Disease.query.order_by(Disease.name).all()
    return render_template('admin/diseases.html', diseases=disease_list)

@admin_bp.route('/ml_analytics')
@login_required
@admin_required
def ml_analytics():
    metrics = ModelMetric.query.order_by(ModelMetric.f1_score.desc()).all()
    
    # Load feature list and artifact metadata if available
    base_dir = os.path.abspath(os.path.join(current_app.root_path, '..'))
    metrics_path = os.path.join(base_dir, 'models', 'metrics.pkl')
    
    artifact_data = None
    if os.path.exists(metrics_path):
        artifact_data = joblib.load(metrics_path)

    return render_template(
        'admin/ml_analytics.html',
        metrics=metrics,
        artifact_data=artifact_data
    )
