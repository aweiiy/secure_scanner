from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():

    data=request.form
    email = data.get('email')
    return render_template("login.html", data=email)

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
            flash("Successfully created the account", category='success')

        return render_template("register.html", data=email)
    else:
        return render_template("register.html")

@auth.route('/logout')
def logout():
    return "Logout successful"
