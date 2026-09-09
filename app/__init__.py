import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    try:
        os.makedirs(os.path.dirname(app.config['DB_PATH']), exist_ok=True)
    except Exception as e:
        print(f"[WARN] Directory creation notice: {e}")


    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    from app.models.user import User, PatientProfile
    from flask import session
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            uid = int(user_id)
        except Exception:
            return None

        user = User.query.get(uid)
        if not user and session.get('user_email'):
            email = session.get('user_email').lower()
            user = User.query.filter_by(email=email).first()
            if not user:
                try:
                    user = User(
                        id=uid,
                        name=session.get('user_name', 'Patient User'),
                        email=email,
                        role=session.get('user_role', 'patient'),
                        phone=session.get('user_phone', '')
                    )
                    user.set_password('Restored@123')
                    db.session.add(user)
                    db.session.commit()
                    
                    if user.role == 'patient':
                        prof = PatientProfile.query.filter_by(user_id=user.id).first()
                        if not prof:
                            prof = PatientProfile(user_id=user.id)
                            db.session.add(prof)
                            db.session.commit()
                except Exception as err:
                    db.session.rollback()
                    user = User.query.filter_by(email=email).first()
        return user


    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.patient import patient_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Register Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Initialize Database Tables & Seed
    with app.app_context():
        db.create_all()
        from app.utils.helpers import seed_database
        try:
            seed_database(db)
        except Exception as err:
            print(f"[WARN] Database seed notice: {err}")

    return app
