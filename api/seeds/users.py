from flask_seeder import Seeder, Faker, generator
from werkzeug.security import generate_password_hash

from api import db

#RUN flask seed run

class User(db.Model):
    def __init__(self, email=None, password=None, role=None):
        self.email = email
        self.password = password
        self.role = role

        def __str__(self):
            return "ID: %s, Email: %s, Password: %s, Role: %s" % (self.id, self.email, self.password, self.role)

# All seeders inherit from Seeder
class UserSeeder(Seeder):

      # run() will be called by Flask-Seeder
     def run(self):
          # Create a new Faker and tell it how to create User objects
          faker = Faker(
                cls=User,
                init={
                 "email": generator.Email(),
                 "password": generate_password_hash('password', method='sha256'),
                 "role": generator.Integer(0, 1)

                }
          )

          if not User.query.filter_by(email='admin@0r.lt').first():
              # Create admin user
                admin = User(email='admin@0r.lt', password=generate_password_hash('admin', method='sha256'), role=1)
                db.session.add(admin)

          # Create 5 users
          for user in faker.create(5):
                print("Adding user: %s" % user)
                db.session.add(user)

