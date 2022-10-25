from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html")

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if len(email) < 4:
            flash("Email length must be greater than 4 characters", category='error')
        elif password != confirm_password:
            flash("Passwords do not match", category='error')
        elif len(password) < 8:
            flash("Password is too short, it must be 8 characters or more", category='error')
        else:
            exists = User.query.filter_by(email=email).first()
            if not exists:
                new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash("Successfully created the account", category='success')
                login_user(new_user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Email already exists", category='error')

        return render_template("register.html", data=email)
    else:
        return render_template("register.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@auth.route('/profile/update', methods=['POST'])
@login_required
def update_profile(id: int):
    data = request.form
    if current_user.id == id:
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if len(email) < 4:
            flash("Email length must be greater than 4 characters", category='error')
        elif password != confirm_password:
            flash("Passwords do not match", category='error')
        elif len(password) < 8:
            flash("Password is too short, it must be 8 characters or more", category='error')
        else:
            current_user.email = email
            current_user.password = generate_password_hash(password, method='sha256')
            db.session.commit()
            flash("Successfully updated the account", category='success')

        return render_template("profile.html", user=current_user)
@auth.route('/profile/delete')
@login_required
def delete_profile():
    user = User.query.filter_by(id=current_user.id).first()
    if user == current_user:
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash("Account deleted successfully", category='success')
        return redirect(url_for('auth.login'))
    else:
        flash("You are not allowed to delete this account", category='error')
        return redirect(url_for('views.home'))

