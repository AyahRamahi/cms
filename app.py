from flask import Flask, render_template, request, flash, redirect, url_for
from db import get_courses, get_course_info, get_article, find_user, create_new_user
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from forms import LoginForm, RegisterForm
from user import User
import os
from werkzeug.security import generate_password_hash


app = Flask(__name__)
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'


@app.route('/')
def home():
    # home page
    return render_template('home/index.html')

@app.route('/courses')
def courses():
    # show all available courses
    courses_list = get_courses()
    return render_template('courses/index.html', courses_list = courses_list)

@app.route('/course/<string:course_name>')
def course(course_name):
    # show course for a given name
    course_info = get_course_info(course_name)
    course_content = course_info['content']
    course_description = course_info['description']
    return render_template(
        'course/index.html',
        course_name = course_name,
        course_content = course_content,
        article = course_description
    )

@app.route('/course/<string:course_name>/<string:subject>/<string:article_name>')
def article(course_name, subject, article_name):
    # show article for a given course, subject, and name
    course_info = get_course_info(course_name)
    course_content = course_info['content']
    article = get_article(course_name, subject, article_name)
    return render_template(
        'course/index.html',
        course_name = course_name,
        course_content = course_content,
        article = article
    )

@app.route('/login', methods=["GET","POST"])
def login():
    # log in user
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = find_user(form.username.data)
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['_id'])
            login_user(user_obj)
            return redirect(request.args.get("next") or url_for("profile"))
        flash('Wrong username or password!', category='error')
    return render_template('login/index.html', title='login', form=form)

@app.route('/logout')
def logout():
    # log out user
    logout_user()
    flash('Logged out successfuly!', category='success')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    # show user profile
    return render_template('profile/index.html', username = current_user.username, firstname = 'Alex', lastname = 'Smith')

@app.route('/register', methods=["GET","POST"])
def register():
    # create a new user account
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if find_user(form.username.data):
            flash("Username is already used!", category='error')
            return render_template('register/index.html', title='Register', form=form)

        ack = create_new_user(
            form.first_name,
            form.last_name.data,
            form.username.data,
            form.password.data)
        if ack:
            flash("Registered successfully!", category='success')
            return redirect(url_for('login'))
        flash("Registration is not successful!", category='error')
        
    return render_template('register/index.html', title='Register', form=form)

@loginManager.user_loader
def load_user(username):
    # loads and returns id of the logged in user
    u = find_user(username)
    if not u:
        return None
    return User(u['_id'])


@app.errorhandler(404)
def page_not_found(error):
    # handles the 404 error
    return render_template('page_not_found.html'), 404

if __name__=='__main__':
    app.debug = True
    secret_key = os.urandom(32)
    app.secret_key = secret_key
    app.config['SECRET_KEY'] = secret_key
    app.run()