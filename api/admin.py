from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from flask_paginate import Pagination, get_page_parameter

from . import db
from .models import Report, User
import validators

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/', methods=['GET', 'POST'])
@login_required
def admin_main():
    if current_user.role == 1:
        return redirect(url_for('admin.reports'))
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))

@admin.route('/users')
@login_required
def users():
    if current_user.role == 1:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        pagination = Pagination(page=page, total=User.query.count(), search=False, record_name='users', per_page=10)
        return render_template("admin/user_manager.html", user=current_user, users=User.query.paginate(page=page, per_page=10).items, pagination=pagination)
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))


@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id: int) -> str:
    if current_user.role == 1:
        user = User.query.get(user_id)
        if user:
            if user.role == 1:
                flash("You cannot delete an admin.", category='error')
                return redirect(url_for('admin.users'))
            else:
                db.session.delete(user)
                db.session.commit()
                flash("User deleted.", category='success')
                return redirect(url_for('admin.users'))
        else:
            flash("User not found.", category='error')
            return redirect(url_for('admin.users'))
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))

@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id: int) -> str:
    if current_user.role == 1:
        user = User.query.filter_by(id=user_id).first()
        if user:
            if user.id == current_user.id:
                flash(f"You can not edit yourself from the admin panel, use the standard profile edit page.", category='error')
                return redirect(url_for('admin.users'))
            return render_template("admin/edit_user.html", user=current_user, user_to_edit=user)
        else:
            return "User not found"
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))

@admin.route('/users/change_password', methods=['POST'])
@login_required
def change_password() -> str:
    if current_user.role == 1:
        data = request.form
        user_id = data.get('user_id')
        password = data.get('new_password')
        confirm_password = data.get('confirm_new_password')
        user = User.query.filter_by(id=user_id).first()
        if user:
            if password != confirm_password:
                flash("Passwords do not match", category='error')
            elif len(password) < 8:
                flash("Password is too short, it must be 8 characters or more", category='error')
            else:
                user.password = generate_password_hash(password, method='sha256')
                db.session.commit()
                flash("Password changed successfully", category='success')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        else:
            return "User not found"
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))


@admin.route('/users/change_role', methods=['POST'])
@login_required
def change_role() -> str:
    if current_user.role == 1:
        data = request.form
        user_id = data.get('user_id')
        role = data.get('role')
        user = User.query.filter_by(id=user_id).first()
        if user:
            if role == 'admin':
                user.role = 1
            else:
                user.role = 0
            db.session.commit()
            flash("Role changed successfully", category='success')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        else:
            return "User not found"
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))


@admin.route('/reports')
@login_required
def reports():
    if current_user.role == 1:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        pagination = Pagination(page=page, total=Report.query.count(), search=False, record_name='reports', per_page=10)
        return render_template("admin/report_manager.html", user=current_user, reports=Report.query.paginate(page=page, per_page=10).items, pagination=pagination)
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))

@admin.route('/reports/<int:report_id>')
@login_required
def show_report(report_id: int) -> str:
    if current_user.role == 1:
        report = Report.query.filter_by(id=report_id).first()
        if report:
            return render_template("admin/report_view.html", user=current_user, report=report)
        else:
            return "Report not found"
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))

@admin.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id: int) -> str:
    if current_user.role == 1:
        report = Report.query.get(report_id)
        if report:
            db.session.delete(report)
            db.session.commit()
            flash("Report deleted.", category='success')
            return redirect(url_for('admin.reports'))
        else:
            flash("Report not found.", category='error')
            return redirect(url_for('admin.reports'))
    else:
        flash("You are not an admin.", category='error')
        return redirect(url_for('views.home'))