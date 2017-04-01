from flask_bcrypt import Bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

from collegejump import app

db = app.db

bcrypt = Bcrypt(app)

class User(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    email     = db.Column(db.String(128), unique=True)
    _password = db.Column(db.String(128)) # Bcrypt string, not plaintext

    def __init__(self, email, plaintext):
        self.email = email
        self.password = plaintext # applies hash automatically

    def __repr__(self):
        return '<User %r>' % self.username

    # Using @hybrid_property, the `password` element acts just like a "real"
    # element, but is modified and accessed using these functions
    # automatically. This is the getter.
    @hybrid_property
    def password(self):
        return self._password

    # This is the setter for the password property, which is used automatically
    # when accessing the property like a regular variable.
    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def check_password(self, plaintext):
        """Check whether an entered plaintext password matches the stored hashed
        copy. Returns True or False."""
        return bcrypt.check_password_hash(self.password, plaintext)
