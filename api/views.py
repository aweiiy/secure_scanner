import os

from flask import Blueprint, render_template, redirect, flash
import celery.states as states
from flask import Response, request
from flask import url_for, jsonify

from .models import Report
from .worker import celery
from flask_login import login_required, current_user
from . import db
import validators


views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/reports')
@login_required
def reports():
    return render_template("reports.html", user=current_user, reports=current_user.reports)


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
        db.session.commit()
        os.mkdir(f'reports/{report.id}')
        flash("Report generation started", category='success')
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
                return render_template("report.html", user=current_user, report=report, task_id=report.task_id)
            else:
                flash("Report is not ready yet", category='error')
                return render_template("report.html", user=current_user, report=report, task_id=report.task_id)



@views.route('/reports/check_status/', methods=['POST'])
def taskstatus():
    task_id = request.form.get('task_id')
    res = celery.AsyncResult(task_id)
    if res.state == states.SUCCESS:
        return jsonify({'status': 'Ready to download'})
    else:
        return jsonify({'status': 'PENDING'})



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






@views.route('/add/<int:param1>/<int:param2>')
def add(param1: int, param2: int) -> str:
    task = celery.send_task('tasks.add', args=[param1, param2], kwargs={})
    response = f"<a href='{url_for('views.check_task', task_id=task.id)}'>check status of {task.id} </a>"
    return response


@views.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return res.state
    else:
        return str(res.result)


@views.route('/health_check')
def health_check() -> Response:
    return jsonify("OK")


@views.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id: int) -> str:
    report = Report.query.filter_by(id=report_id).first()
    if report:
        if report.user_id == current_user.id:
            db.session.delete(report)
            db.session.commit()
            os.rmdir(f'reports/{report.id}')
            flash("Report deleted", category='success')
            return redirect(url_for('views.reports'))
        else:
            return "You do not have permission to delete this report"
    else:
        return "Report not found"


@views.route('/api/count_files', methods=['POST'])
def count_files():
    if request.authorization.username == 'admin' and request.authorization.password == 'admin':
        data = request.form
        report_id = data.get('report_id')
        report = Report.query.get(report_id)
        if report:
            return jsonify({'count': len(os.listdir(f'reports/{report.id}'))})
        else:
            return jsonify({'count': 0})
    else:
        return jsonify({'count': 0})