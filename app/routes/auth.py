from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, PatientProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('patient.dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        date_of_birth = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Optional Profile Fields
        height = request.form.get('height')
        weight = request.form.get('weight')
        blood_group = request.form.get('blood_group')
        allergies = request.form.get('allergies', '').strip()
        existing_conditions = request.form.get('existing_conditions', '').strip()

        # Validation
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/signup.html')

        if password != confirm_password:
            flash('Passwords do not match. Please verify your password.', 'danger')
            return render_template('auth/signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/signup.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email address already exists. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        # Create user
        user = User(
            name=name,
            email=email,
            phone=phone,
            date_of_birth=date_of_birth,
            gender=gender,
            role='patient'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush() # Get user.id

        # Create profile
        profile = PatientProfile(
            user_id=user.id,
            height=float(height) if height and height.strip() else None,
            weight=float(weight) if weight and weight.strip() else None,
            blood_group=blood_group if blood_group else None,
            allergies=allergies if allergies else None,
            existing_conditions=existing_conditions if existing_conditions else None
        )
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful! Please log in with your credentials.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('patient.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email address or password. Please try again.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated. Please contact administrator support.', 'danger')
            return render_template('auth/login.html')

        if user.is_admin():
            flash('Admin detected. Please use the Admin Portal Login page.', 'info')
            return redirect(url_for('auth.admin_login'))

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('patient.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin():
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password) or not user.is_admin():
            flash('Invalid administrator credentials.', 'danger')
            return render_template('auth/admin_login.html')

        if not user.is_active:
            flash('Admin account is inactive.', 'danger')
            return render_template('auth/admin_login.html')

        login_user(user)
        flash('Successfully authenticated as Administrator.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('auth/admin_login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
