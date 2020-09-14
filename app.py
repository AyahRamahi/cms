from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from db import *
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from forms import LoginForm, RegisterForm, EditProfileForm
from user import User
import os
from werkzeug.security import generate_password_hash
import json

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
@login_required
def course(course_name):
    # show course for a given name
    if not current_user.is_enrolled(course_name):
        current_user.enroll(course_name)
    course_info = get_course_info(course_name)
    course_content = course_info['content']
    course_description = course_info['description']
    return render_template(
        'course/index.html',
        course_name = course_name,
        course_content = course_content,
        article = course_description
    )

@app.route('/course/<string:course_name>/<string:subject>/<string:article_name>', methods=["GET","POST"])
@login_required
def article(course_name, subject, article_name):
    # show article for a given course, subject, and name and submit a comment about it
    if request.method == 'POST':
        comment = request.form['comment']
        if current_user.is_authenticated:
            ack = add_comment(course_name, subject, article_name, current_user.get_id(), current_user.get_full_name(), comment)
            if not ack:
                flash("Could not add your comment", category='error')

    course_info = get_course_info(course_name)
    course_content = course_info['content']
    article = get_article(course_name, subject, article_name)
    comments = get_comments(course_name, subject, article_name)
    return render_template(
        'course/index.html',
        course_name = course_name,
        subject = subject,
        course_content = course_content,
        article_name = article_name,
        article = article,
        comments = comments
    )

@app.route('/course/<string:course_name>/<string:subject>/<string:article_name>/remove_comment/<string:id>')
@login_required
def remove_comment(course_name, subject, article_name, id):
    # delete a comment from an article
    delete_comment(course_name, subject, article_name, id)
    return redirect(request.referrer)

@app.route('/courses/course/mark_as_completed/<string:course_name>/<string:id>', methods=["GET", "POST"])
@login_required
def mark_as_completed(id, course_name):
    # mark an article as completed
    if(is_article_completed(current_user.get_id(), id)):
        remove_article_from_completed(current_user.get_id(), id, course_name)
    else:
        mark_article_completed(current_user.get_id(), id, course_name)
    return jsonify({
        "state":"success",
    })



@app.route('/auth/register', methods=["GET","POST"])
def register():
    # register a user
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        if find_user(form.username.data):
            flash("Username is already used!", category='error')
            return render_template('register/index.html', title='Register', form=form)

        ack = create_new_user(
            form.first_name.data,
            form.last_name.data,
            form.username.data,
            form.password.data)
        if ack:
            flash("Registered successfully!", category='success')
            return redirect(url_for('login'))
        flash("Registration is not successful!", category='error')
        
    return render_template('auth/register/index.html', title='Register', form=form)

@app.route('/auth/login', methods=["GET","POST"])
def login():
    # login a user
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        # TODO: read admin username and password from config file (or sth else)
        admin_password = "admin"
        # login admin
        if form.username.data == "admin":
            if form.password.data == admin_password:
                user_obj = User("admin", "", "")
                login_user(user_obj)
                return redirect(url_for("admin_home"))
            flash('Wrong username or password!', category='error')
        else:
            user = find_user(form.username.data)
            if user and User.validate_login(user['password'], form.password.data):
                user_obj = User(user['_id'], user['first_name'], user['last_name'])
                login_user(user_obj)
                return redirect(request.args.get("next") or url_for("profile"))
            flash('Wrong username or password!', category='error')
    return render_template('auth/login/index.html', title='login', form=form)


@app.route('/profile')
@login_required
def profile():
    # show user profile
    username = current_user.username
    name = current_user.get_full_name()
    ongoing_courses = get_ongoing_courses(username)
    for course in ongoing_courses:
        total_count = get_course_articles_count(course['course_name'])
        if course['finished_articles_count'] == total_count:
            completed_course(username, course['course_name'])
            ongoing_courses.remove(course)
        else:
            course['finished_articles_count'] = int(course['finished_articles_count'] / total_count * 100)
    completed_courses = get_completed_courses(username)
    return render_template('profile/index.html', username = username, name = name, ongoing_courses = ongoing_courses, completed_courses = completed_courses)

@app.route('/editProfile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    # show edit profile form to allow user to make changes
    form = EditProfileForm()
    first_name = current_user.get_first_name()
    last_name = current_user.get_last_name()
    if request.method == 'POST' and form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        change_name(current_user.get_id(), first_name, last_name)
        return redirect(request.args.get("next") or url_for("profile"))
    return render_template('editProfile/index.html', form=form, first_name=first_name, last_name=last_name)

@app.route("/admin_home")
@login_required
def admin_home():
    courses_list = get_courses()
    return render_template("admin/courses/index.html", courses_list = courses_list)

@app.route("/admin_home/edit_course/<string:course_name>")
@login_required
def edit_course(course_name):
    course_info = get_course_info(course_name)
    course_content = course_info['content']
    course_description = course_info['description']
    return render_template("/admin/edit_course/index.html", course_name = course_name, course_content = course_content, course_description = course_description)

@app.route("/admin_home/edit_article/<string:course_name>/<string:subject>/<string:article_name>" , methods=["GET", "POST"])
#@login_required
def edit_article(course_name, subject, article_name):
    print(course_name, subject, article_name)
    if request.method == 'POST':
        # changing name of article needs updating course content
        edit_article_content(course_name, subject, article_name, request.form['content'])
        return redirect(url_for('edit_course', course_name=course_name))
    article_content = get_article_content(course_name, subject, article_name)
    return render_template("/admin/edit_article/index.html", course_name=course_name, subject=subject, article_name=article_name, article_content=article_content)

@app.route("/admin_home/edit_course/new_subject/<string:course_name>", methods=["POST"])
@login_required
def new_subject(course_name):
    # TODO: prevent having 2 subjects with same name in a course
    new_subject_name = request.form["new-subject-name"]
    add_new_course_subject(course_name, new_subject_name)
    return redirect(url_for('edit_course', course_name=course_name))

@app.route("/admin_home/edit_course/delete_subject/<string:course_name>/<string:subject>")
@login_required
def delete_subject(course_name, subject):
    delete_course_subject(course_name, subject)
    return redirect(url_for('edit_course', course_name=course_name))

@loginManager.user_loader
def load_user(username):
    # loads and returns id of the logged in user
    u = find_user(username)
    if not u:
        if username == "admin":
            return User("admin", "", "")
        return None
    return User(u['_id'], u['first_name'], u['last_name'])

@app.errorhandler(404)
def page_not_found(error):
    # handles the 404 error
    return render_template('page_not_found.html'), 404

if __name__=='__main__':
    app.debug = True
    app.secret_key = os.urandom(32)
    app.run()