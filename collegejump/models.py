from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from collegejump import app

db = app.db

bcrypt = Bcrypt(app)

mentorships = db.Table('mentee_mentors', db.metadata,
        db.Column('mentee_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('mentor_id', db.Integer, db.ForeignKey('user.id'))
        )

enrollment = db.Table('enrollment', db.metadata,
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('semester_id', db.Integer, db.ForeignKey('semester.id'))
        )

week_assignments = db.Table('week_assignments', db.metadata,
        db.Column('semester_id', db.Integer),
        db.Column('week_number', db.Integer),
        db.Column('assignment_id', db.Integer, db.ForeignKey('assignment.id')),
        db.ForeignKeyConstraint(
            ['semester_id', 'week_number'],
            ['week.semester_id', 'week.week_number']
        ))

week_documents = db.Table('week_documents', db.metadata,
        db.Column('semester_id', db.Integer),
        db.Column('week_number', db.Integer),
        db.Column('document_id', db.Integer, db.ForeignKey('document.id')),
        db.ForeignKeyConstraint(
            ['semester_id', 'week_number'],
            ['week.semester_id', 'week.week_number']
        ))

class User(db.Model, UserMixin):
    NAME_MAX_LENGTH = 128
    EMAIL_MAX_LENGTH = 128

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(NAME_MAX_LENGTH))
    email     = db.Column(db.String(EMAIL_MAX_LENGTH), unique=True)
    _password = db.Column(db.String(128)) # Bcrypt string, not plaintext

    admin     = db.Column(db.Boolean)

    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    mentees   = db.relationship('User', backref=db.backref('mentor', remote_side=[id]))

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

    @staticmethod
    @app.login_manager.user_loader
    def load_user(user_email):
        return User.query.filter_by(email=user_email).first()

class Announcement(db.Model):
    TITLE_MAX_LENGTH = 128
    CONTENT_MAX_LENGTH = 1000

    id        = db.Column(db.Integer, primary_key=True)
    title     = db.Column(db.String(TITLE_MAX_LENGTH))
    content   = db.Column(db.String(CONTENT_MAX_LENGTH))
    timestamp = db.Column(db.DateTime())

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author    = db.relationship('User')

class Semester(db.Model):
    """A semester is a collection of weeks meant to make up the content of the
    website during a whole semester."""
    NAME_MAX_LENGTH = 16

    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(NAME_MAX_LENGTH))
    order = db.Column(db.Integer, unique=True) # for ordering semesters

class Week(db.Model):
    HEADER_MAX_LENGTH = 64
    INTRO_MAX_LENGTH  = 1024

    # Weeks are identified as (semester, week number) uniquely.
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), primary_key=True)
    week_number = db.Column(db.Integer, primary_key=True)

    header = db.Column(db.String(HEADER_MAX_LENGTH))
    intro  = db.Column(db.String(INTRO_MAX_LENGTH))

    semester = db.relationship('Semester',
            backref=db.backref('weeks', order_by=week_number))

    assignments = db.relationship('Assignment', secondary=week_assignments)
    documents   = db.relationship('Document',   secondary=week_documents)

class Assignment(db.Model):
    NAME_MAX_LENGTH = 64

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(NAME_MAX_LENGTH))
    questions = db.Column(db.Text) # a JSON blob

class Document(db.Model):
    NAME_MAX_LENGTH = 64

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(NAME_MAX_LENGTH))
    data = db.Column(db.LargeBinary)
