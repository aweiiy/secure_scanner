from flask import Flask, render_template
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from flask_seeder import FlaskSeeder


db = SQLAlchemy()

def page_not_found(e):
  return render_template('404.html'), 404

def create_app():
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    app.config['SECRET_KEY'] = 'testavimas'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    db.init_app(app)

    seeder = FlaskSeeder()
    seeder.init_app(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login to access this feature"
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from api.models import User
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth
    from api.admin import admin

    app.register_blueprint(admin)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')



    from . import models

    with app.app_context():
        db.create_all()
        user = models.User(email='admin@0r.lt', password=generate_password_hash('admin', method='sha256'), role=1)
        if not models.User.query.filter_by(email=user.email).first():
            db.session.add(user)
            db.session.commit()

    return app
