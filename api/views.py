from flask import Blueprint, render_template
import celery.states as states
from flask import Response
from flask import url_for, jsonify
from .worker import celery

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("home.html")


@views.route('/test')
def start():
    return "working"


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
