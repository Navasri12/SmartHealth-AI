from flask import Blueprint, jsonify, request
from app.models.medical import Symptom, Disease
from app.models.prediction import Prediction

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/symptoms/search')
def search_symptoms():
    query = request.args.get('q', '').strip()
    if not query:
        symptoms = Symptom.query.filter_by(active=True).limit(20).all()
    else:
        symptoms = Symptom.query.filter(
            Symptom.active == True,
            (Symptom.name.ilike(f"%{query}%")) | (Symptom.code_name.ilike(f"%{query}%"))
        ).limit(20).all()

    results = [{
        'id': s.id,
        'code_name': s.code_name,
        'name': s.name,
        'category': s.category,
        'description': s.description,
        'is_emergency': s.is_emergency
    } for s in symptoms]

    return jsonify({'status': 'success', 'count': len(results), 'symptoms': results})

@api_bp.route('/diseases/<string:name>')
def get_disease(name):
    disease = Disease.query.filter_by(name=name).first()
    if not disease:
        return jsonify({'status': 'error', 'message': 'Disease not found'}), 404
        
    return jsonify({
        'status': 'success',
        'disease': {
            'name': disease.name,
            'category': disease.category,
            'description': disease.description,
            'common_symptoms': disease.common_symptoms,
            'prevention': disease.prevention,
            'recommendations': disease.recommendations,
            'warning_signs': disease.warning_signs
        }
    })
