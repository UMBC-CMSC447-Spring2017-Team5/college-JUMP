from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from collegejump import app

mentorships = app.db.Table('mentee_mentors', app.db.metadata,
                           app.db.Column('mentee_id', app.db.Integer,
                                         app.db.ForeignKey('user.id')),
                           app.db.Column('mentor_id', app.db.Integer,
                                         app.db.ForeignKey('user.id'))
                           )

enrollment = app.db.Table('enrollment', app.db.metadata,
                          app.db.Column('user_id', app.db.Integer,
                                        app.db.ForeignKey('user.id')),
                          app.db.Column('semester_id', app.db.Integer,
                                        app.db.ForeignKey('semester.id'))
                          )

week_assignments = app.db.Table('week_assignments', app.db.metadata,
                                app.db.Column('semester_id', app.db.Integer),
                                app.db.Column('week_number', app.db.Integer),
                                app.db.Column('assignment_id', app.db.Integer,
                                              app.db.ForeignKey('assignment.id')),
                                app.db.ForeignKeyConstraint(
                                    ['semester_id', 'week_number'],
                                    ['week.semester_id', 'week.week_number']
                                ))

week_documents = app.db.Table('week_documents', app.db.metadata,
                              app.db.Column('semester_id', app.db.Integer),
                              app.db.Column('week_number', app.db.Integer),
                              app.db.Column('document_id', app.db.Integer,
                                            app.db.ForeignKey('document.id')),
                              app.db.ForeignKeyConstraint(
                                  ['semester_id', 'week_number'],
                                  ['week.semester_id', 'week.week_number']
                              ))


class User(app.db.Model, UserMixin):
    NAME_MAX_LENGTH = 128
    EMAIL_MAX_LENGTH = 128

    id = app.db.Column(app.db.Integer, primary_key=True)

    name = app.db.Column(app.db.String(NAME_MAX_LENGTH))
    email = app.db.Column(app.db.String(EMAIL_MAX_LENGTH), unique=True)
    # Bcrypt string, not plaintext
    _password = app.db.Column(app.db.String(128))

    admin = app.db.Column(app.db.Boolean)

    mentor_id = app.db.Column(
        app.db.Integer, app.db.ForeignKey('user.id'), nullable=True)
    mentees = app.db.relationship(
        'User', backref=app.db.backref('mentor', remote_side=[id]))

    def __init__(self, email, plaintext):
        self.email = email
        self.password = plaintext  # applies hash automatically

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


class Announcement(app.db.Model):
    TITLE_MAX_LENGTH = 128
    CONTENT_MAX_LENGTH = 1000

    id = app.db.Column(app.db.Integer, primary_key=True)
    title = app.db.Column(app.db.String(TITLE_MAX_LENGTH))
    content = app.db.Column(app.db.String(CONTENT_MAX_LENGTH))
    timestamp = app.db.Column(app.db.DateTime())

    author_id = app.db.Column(app.db.Integer, app.db.ForeignKey('user.id'))
    author = app.db.relationship('User')


class Semester(app.db.Model):
    """A semester is a collection of weeks meant to make up the content of the
    website during a whole semester."""
    NAME_MAX_LENGTH = 16

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(NAME_MAX_LENGTH))
    # for ordering semesters
    order = app.db.Column(app.db.Integer, unique=True)


class Week(app.db.Model):
    HEADER_MAX_LENGTH = 64
    INTRO_MAX_LENGTH = 1024

    # Weeks are identified as (semester, week number) uniquely.
    semester_id = app.db.Column(
        app.db.Integer, app.db.ForeignKey('semester.id'), primary_key=True)
    week_number = app.db.Column(app.db.Integer, primary_key=True)

    header = app.db.Column(app.db.String(HEADER_MAX_LENGTH))
    intro = app.db.Column(app.db.String(INTRO_MAX_LENGTH))

    semester = app.db.relationship('Semester',
                                   backref=app.db.backref('weeks', order_by=week_number))

    assignments = app.db.relationship('Assignment', secondary=week_assignments)
    documents = app.db.relationship('Document',   secondary=week_documents)


class Assignment(app.db.Model):
    NAME_MAX_LENGTH = 64

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(NAME_MAX_LENGTH))
    questions = app.db.Column(app.db.Text)  # a JSON blob


class Document(app.db.Model):
    NAME_MAX_LENGTH = 64

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(NAME_MAX_LENGTH))
    data = app.db.Column(app.db.LargeBinary)
