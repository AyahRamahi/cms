
# CMS Nano Lab
An online platform used to host online content/courses.

## Usage
* Clone this repo.
* Install Python 3.
* Install the requirmenets using this command: `pip install -r requirements.txt` (it is adviced to use a virtualenv).
* Run the project using: `python app.py`.
* In the terminal, you will see a URL for the locally hosted website, click on it and you can see the website.

## Tools
* Flask
* MongoDB (Pymongo)
* Flask-Login
* Flask WTForms
* Bootstrap

## Services
* Browse courses and their content
* Login and register users
* Mark articles as complete
* Progress bars for courses on users profiles
* Users can edit their info
* Add comments to articles and delete them

## Files
* static: has all static files including images, videos, .js, .css, and favicon.
* templates: has all templates (html files.
* app.py: has all the routes that are  used in the website.
* db.py: has all function used in app.py to communicate with the database.
* form.py: has 3 forms (login, register, editProfile) required by WTForms.
* user.py: has the user class, required by Flask-Login.
* requirements.txt: generated using `pip freeze > requirements.txt`, and used to install and keep packages required by the project.
* .gitignore: used to ignore specific files from being uploaded to GitHub with each push.
* README.md: this document.