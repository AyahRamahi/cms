from werkzeug.security import check_password_hash
from db import is_user_enrolled, enroll_user, is_article_completed

class User():
    """
    A class used to represent a user
    ...

    Attributes
    ----------
    username : str
        the username of the user
    first_name : str
        the first name of the user
    last_name : str
        the last name of the user

    Methods
    -------
    is_authenticated()
        Returns if the user is logged in or not

    is_active()
        Returns if the user is currently active on the website or not

    get_id()
        Returns the username of the user

    get_full_name()
        Returns the first and last names of the user as one string

    get_first_name()
        Returns the first name of the user

    get_last_name()
        Returns the last name of the user

    is_enrolled(course_name)
        Returns True if the user is enrolled in the course with the given name

    enroll(course_name)
        Enrolls the user in the course with the given name, where it adds the course to the ongoing_courses array of the user

    is_completed_article(id)
        Returns True if the article is marked as complete by the user
    
    validate_login(password_hash, password)
        Validates if the given password's hash is the same as the one in the database
    """
    def __init__(self, username, first_name, last_name):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return self.username
    
    def get_full_name(self):
        return (str(self.first_name) + " " + str(self.last_name))

    def get_first_name(self):
        return str(self.first_name)

    def get_last_name(self):
        return str(self.last_name)

    def is_enrolled(self, course_name):
        return is_user_enrolled(self.username, course_name)
    
    def enroll(self, course_name):
        return enroll_user(self.username, course_name)

    def is_completed_article(self, id):
        return is_article_completed(self.username, id)

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)