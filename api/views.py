from flask import Blueprint, render_template
import celery.states as states
from flask import Response, request
from flask import url_for, jsonify

from .models import Report
from .worker import celery
from flask_login import login_required, current_user
from . import db


views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/reports')
@login_required
def reports():
    return render_template("reports.html", user=current_user, reports=current_user.reports)

@views.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@views.route('/api/genereate_report', methods=['POST'])
@login_required
def generate_report():
    data = request.form
    website_name = data.get('website')
    db.session.add(Report(name=website_name, location="test", user_id=current_user.id))
    db.session.commit()
    task = celery.send_task('tasks.generate_report', args=[website_name], kwargs={})
    return f"<a href='{url_for('views.taskstatus', task_id=task.id)}'>check status of {website_name} report </a>"

@views.route('/api/taskstatus/<task_id>')
@login_required
def taskstatus(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return res.state
    else:
        return str(res.result)



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
