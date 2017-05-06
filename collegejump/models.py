import datetime
import io
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from collegejump import app

# pylint: disable=invalid-name
mentorships = app.db.Table('mentee_mentors', app.db.metadata,
                           app.db.Column('mentee_id', app.db.Integer,
                                         app.db.ForeignKey('user.id')),
                           app.db.Column('mentor_id', app.db.Integer,
                                         app.db.ForeignKey('user.id')))

enrollment = app.db.Table('enrollment', app.db.metadata,
                          app.db.Column('user_id', app.db.Integer,
                                        app.db.ForeignKey('user.id')),
                          app.db.Column('semester_id', app.db.Integer,
                                        app.db.ForeignKey('semester.id')))

week_assignments = app.db.Table('week_assignments', app.db.metadata,
                                app.db.Column('week_id',
                                              app.db.Integer,
                                              app.db.ForeignKey('week.id')),
                                app.db.Column('assignment_id',
                                              app.db.Integer,
                                              app.db.ForeignKey('assignment.id')))

week_documents = app.db.Table('week_documents', app.db.metadata,
                              app.db.Column('week_id',
                                            app.db.Integer,
                                            app.db.ForeignKey('week.id')),
                              app.db.Column('document_id',
                                            app.db.Integer,
                                            app.db.ForeignKey('document.id')))


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

    semesters = app.db.relationship('Semester', secondary=enrollment)

    def __init__(self, email, plaintext, name=None, admin=False):
        self.name = name
        self.email = email.lower()
        self.password = plaintext  # applies hash automatically
        self.admin = admin

    def __repr__(self):
        return '<User {!r}>'.format(self.email)

    # Using @hybrid_property, the `password` element acts just like a "real"
    # element, but is modified and accessed using these functions
    # automatically. This is the getter.
    @hybrid_property
    def password(self): # pylint: disable=method-hidden
        return self._password

    # This is the setter for the password property, which is used automatically
    # when accessing the property like a regular variable.
    @password.setter
    def _set_password(self, plaintext):
        self._password = app.bcrypt.generate_password_hash(plaintext)

    def check_password(self, plaintext):
        """Check whether an entered plaintext password matches the stored hashed
        copy. Returns True or False."""
        return app.bcrypt.check_password_hash(self.password, plaintext)

    @staticmethod
    @app.login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @classmethod
    def transform_csv_row(cls, row):
        row['_password'] = row['_password'].lstrip('b\'').rstrip('\'')
        return row

class Announcement(app.db.Model):
    TITLE_MAX_LENGTH = 128
    CONTENT_MAX_LENGTH = 1000

    id = app.db.Column(app.db.Integer, primary_key=True)
    title = app.db.Column(app.db.String(TITLE_MAX_LENGTH))
    content = app.db.Column(app.db.String(CONTENT_MAX_LENGTH))
    timestamp = app.db.Column(app.db.DateTime())

    author_id = app.db.Column(app.db.Integer, app.db.ForeignKey('user.id'))
    author = app.db.relationship('User')

    def __init__(self, author_email, title, content, timestamp=None):
        self.author = User.query.filter_by(email=author_email).one()
        self.title = title
        self.content = content

        if timestamp is None:
            timestamp = datetime.datetime.now()
        self.timestamp = timestamp

    def __repr__(self):
        return '<Announcement {!r}>'.format(self.title)

    @classmethod
    def transform_csv_row(cls, row):
        row['timestamp'] = datetime.datetime.strptime(row['timestamp'],
                                                      "%Y-%m-%d %H:%M:%S.%f")
        return row

class Semester(app.db.Model):
    """A semester is a collection of weeks meant to make up the content of the
    website during a whole semester."""
    NAME_MAX_LENGTH = 32

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(NAME_MAX_LENGTH))
    # for ordering semesters
    order = app.db.Column(app.db.Integer, unique=True)

    def __init__(self, name, order):
        self.name = name
        self.order = order

    def __repr__(self):
        return '<Semester {!r}>'.format(self.name)

class Week(app.db.Model):
    HEADER_MAX_LENGTH = 64
    INTRO_MAX_LENGTH = 1024

    # Weeks are identified as (semester, week number) uniquely.
    id = app.db.Column(app.db.Integer, primary_key=True)
    semester_id = app.db.Column(app.db.Integer, app.db.ForeignKey('semester.id'))
    week_num = app.db.Column(app.db.Integer)

    header = app.db.Column(app.db.String(HEADER_MAX_LENGTH))
    intro = app.db.Column(app.db.String(INTRO_MAX_LENGTH))

    semester = app.db.relationship('Semester',
                                   backref=app.db.backref('weeks', order_by=week_num))

    assignments = app.db.relationship('Assignment', secondary=week_assignments)
    documents = app.db.relationship('Document', secondary=week_documents)

    __table_args__ = tuple(app.db.UniqueConstraint('semester_id', 'week_num'))

    def __init__(self, semester_id, week_num, header, intro):
        self.semester_id = semester_id
        self.week_num = week_num
        self.header = header
        self.intro = intro

    def __repr__(self):
        return '<Week {!r} in {!r}>'.format(self.week_num, self.semester.name)

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

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __repr__(self):
        return '<Document {!r}>'.format(self.name)

    def file_like(self):
        """Return a file-like representation of the data of this file."""
        return io.BytesIO(self.data)
