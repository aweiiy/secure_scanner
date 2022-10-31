import os

from flask import Blueprint, render_template, redirect, flash, send_file
import celery.states as states
from flask import Response, request
from flask import url_for, jsonify
from fpdf import FPDF
from werkzeug.security import generate_password_hash

from .models import Report, User
from .worker import celery
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
from . import db
import validators
import shutil


views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/reports')
@login_required
def reports():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    Reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.id.desc())
    pagination = Pagination(page=page, total=Reports.count(), search=False, record_name='reports', per_page=10)
    return render_template("user/reports.html", user=current_user, reports=Reports.paginate(page=page, per_page=10).items, pagination=pagination)

@views.route('/api/genereate_report', methods=['POST'])
@login_required
def generate_report():
    data = request.form
    website_name = data.get('website')
    if validators.url(website_name):
        report = Report(name=website_name, task_id='' , user_id=current_user.id)
        db.session.add(report)
        db.session.commit()
        task = celery.send_task('tasks.generate_report', args=[website_name, report.id])
        report.task_id = task.id
        report.status = task.state
        db.session.commit()
        os.mkdir(f'reports/{report.id}')
        flash("Scan started, check back later for generated report.", category='success')
        return redirect(url_for('views.reports'))
        #return f"<a href='{url_for('views.taskstatus', task_id=task.id)}'>check status of {website_name} report </a>"
    else:
        flash("Invalid URL, use http:// or https://", category='error')
        return redirect(url_for('views.home'))

@views.route('/reports/<report_id>')
@login_required
def show_report(report_id):
    report = Report.query.get(report_id)
    if report:
        if report.user_id == current_user.id:
            res = celery.AsyncResult(report.task_id)
            if res.state == states.SUCCESS:
                return render_template("user/report.html", user=current_user, report=report, task_id=report.task_id, scan_data=report.scan_data)
            else:
                flash("Report is not ready yet", category='error')
                return render_template("generating.html", user=current_user, report=report, task_id=report.task_id)



@views.route('/reports/check_status/', methods=['POST'])
def taskstatus():
    task_id = request.form.get('task_id')
    res = celery.AsyncResult(task_id)
    if res.state == states.SUCCESS:
        return jsonify({'status': 'Ready to download', 'state': res.state})
    else:
        return jsonify({'status': res.state, 'state': res.state})



@views.route('/api/add/<report_id>', methods=['POST'])
def add_report_file(report_id: int):
    auth = request.authorization
    #curl -u admin:admin -F "file=@nmap" 127.0.0.1:5001/api/add/1
    if auth and auth.username == 'admin' and auth.password == 'admin':
        report = Report.query.get(report_id)
        if report:
            file = request.files['file']
            file.save(f'reports/{report_id}/{file.filename}')
            return Response(status=200)
        else:
            return Response(status=404)
    else:
        return Response(status=401)


@views.route('/check/<int:report_id>')
def check_task(report_id: int):
    report = Report.query.get(report_id)
    if report:
        task_id = report.task_id
        res = celery.AsyncResult(task_id)
        report.status = res.state
        db.session.commit()
        return res.state
    else:
        return "Report not found"




@views.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id: int) -> str:
    report = Report.query.filter_by(id=report_id).first()
    if report:
        if report.user_id == current_user.id:
            celery.control.revoke(report.task_id, terminate=True)
            flash(f"Report for {report.name} has been deleted successfully.", category='success')
            db.session.delete(report)
            db.session.commit()
            shutil.rmtree(f'reports/{report_id}')
            return redirect(url_for('views.reports'))
        else:
            return "You do not have permission to delete this report"
    else:
        return "Report not found"


@views.route('/reports/<int:report_id>/download', methods=['GET'])
@login_required
def download_report(report_id: int) -> str:
    report = Report.query.filter_by(id=report_id).first()
    if report:
        if report.user_id == current_user.id:
            res = celery.AsyncResult(report.task_id)
            if res.state == states.SUCCESS:
                return send_file(f'reports/{report_id}/Generated_Report.pdf', as_attachment=True, download_name=f'{report.name}_report.pdf')
            else:
                flash("Report is not ready yet", category='error')
                return redirect(url_for('views.reports'))
        else:
            return "You do not have permission to download this report"
    else:
        return "Report not found"


@views.route('/api/count_files/<int:report_id>', methods=['GET'])
def count_files(report_id: int) -> str:
    report = Report.query.filter_by(id=report_id).first()
    if report:
        if len(os.listdir(f'reports/{report.id}')) == 2:
            report.status = 'Ready'
            db.session.commit()
        return jsonify(len(os.listdir(f'reports/{report.id}')))
    else:
        return "Report not found"


@views.route('/api/merge_files', methods=['POST'])
def merge_reports() -> str:
    auth = request.authorization
    if auth and auth.username == 'admin' and auth.password == 'admin':
        report_id = request.form.get('report_id')
        report = Report.query.filter_by(id=report_id).first()
        if report:
            files = os.listdir(f'reports/{report.id}')
            with open(f'reports/{report.id}/merged.txt', 'w') as outfile:
                for fname in files:
                    with open(f'reports/{report.id}/{fname}') as infile:
                        outfile.write(infile.read())
            with open(f'reports/{report.id}/merged.txt', 'r') as f:
                report.scan_data = f.read()

            db.session.commit()
            convert_pdf(f'reports/{report.id}/merged.txt', f'reports/{report.id}/Generated_Report.pdf')
            return Response(status=200)
        else:
            return Response(status=404)

def convert_pdf(txt_file, pdf_file):
    with open(txt_file, 'r') as f:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for x in f:
            pdf.cell(200, 10, txt=x, ln=1, align='C')
        pdf.output(pdf_file)

