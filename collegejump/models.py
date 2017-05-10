import datetime
import io
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from collegejump import app

# pylint: disable=invalid-name
mentorships = app.db.Table('mentorships', app.db.metadata,
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

    mentors = app.db.relationship('User',
                                  secondary=mentorships,
                                  primaryjoin=mentorships.c.mentee_id==id,
                                  secondaryjoin=mentorships.c.mentor_id==id,
                                  backref='mentees')

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

    def interested_semesters(self):
        """Return a generator for all semesters in descending order in which the
        user is 'interested.' That is, ones in which they are enrolled, ones in
        which a mentee of their is enrolled, or all of them (if they are an
        administrator).
        """
        if self.admin:
            # If the user is an admin, show all semesters.
            return Semester.query.order_by(Semester.order.desc())

        elif not self.mentees:
            # If the user is a student, show just the enrolled semesters.
            return sorted(self.semesters, key=lambda s: s.order, reverse=True)

        # If the user is a mentor, include themselves and their students as
        # persons of interest, then query on those semesters.
        poi = [self] + self.mentees
        poi_ids = [p.id for p in poi]
        return app.db.session.query(Semester) \
                             .join(enrollment) \
                             .filter(enrollment.c.user_id.in_(poi_ids)) \
                             .order_by(Semester.order.desc())

    def submissions_for_feedback(self, assignment):
        """Return a generator for all submissions on the assignment in
        descending order of timestamp which the user has permission to give
        feedback on. For mentors, this is any submission their mentees have
        made. For admins, this is all submissions.
        """
        if self.admin:
            return sorted(assignment.submissions, key=lambda s: s.timestamp, reverse=True)

        mentee_ids = [m.id for m in self.mentees]
        return app.db.session.query(Submission) \
                             .filter_by(assignment=assignment) \
                             .filter(Submission.author_id.in_(mentee_ids)) \
                             .order_by(Submission.timestamp.desc())

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

    assignments = app.db.relationship('Assignment', secondary=week_assignments, uselist=True)
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
    INSTRUCTIONS_MAX_LENGTH = 4096

    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(NAME_MAX_LENGTH))
    instructions = app.db.Column(app.db.String(INSTRUCTIONS_MAX_LENGTH))
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

class Submission(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)

    text = app.db.Column(app.db.Text)
    timestamp = app.db.Column(app.db.DateTime())

    author_id = app.db.Column(app.db.Integer, app.db.ForeignKey('user.id'))
    author = app.db.relationship('User')

    assignment_id = app.db.Column(app.db.Integer, app.db.ForeignKey('assignment.id'))
    assignment = app.db.relationship('Assignment', backref='submissions')

class Feedback(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)

    text = app.db.Column(app.db.Text)
    timestamp = app.db.Column(app.db.DateTime())

    submission_id = app.db.Column(app.db.Integer, app.db.ForeignKey('submission.id'))
    submission = app.db.relationship('Submission', backref='all_feedback')

    author_id = app.db.Column(app.db.Integer, app.db.ForeignKey('user.id'))
    author = app.db.relationship('User')
