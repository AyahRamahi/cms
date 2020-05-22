from werkzeug.security import check_password_hash


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
    get_username()
        Returns the username of the user
    
    is_authenticated()
        Returns if the user is logged in or not

    is_active()
        Returns if the user is currently active on the website or not

    is_anonymous()
        Returns if the user is logged in as anonymous or not

    get_id()
        Returns the ID of the user
    
    validate_login(password_hash, password)
        Validates if the given password's hash is the same as the one in the database
    """

    def __init__(self, username):
        """
        Parameters
        ----------
        username : str
            The username of the user
        """
        self.username = username
        self.first_name = None
        self.last_name = None

    def get_username(self):
        """Returns the username of the user."""
        return username

    def is_authenticated(self):
        """Returns if the user is logged in or not."""
        return True

    def is_active(self):
        """Returns if the user is currently active on the website or not"""
        return True

    def is_anonymous(self):
        """Returns if the user is logged in as anonymous or not"""
        return False

    def get_id(self):
        """Returns the ID of the user."""
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        """Validates if the given password's hash is the same as the one in the database

        Parameters
        ----------
        password_hash : str
            The hashed password saved in the database
        password : str
            The password eneterd by the user during login 
        """
        return check_password_hash(password_hash, password)