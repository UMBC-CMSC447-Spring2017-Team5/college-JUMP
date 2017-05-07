from urllib.parse import  urlparse, urljoin
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from wtforms import fields, validators, widgets, ValidationError
import flask

from collegejump import app, models

def is_safe_url(target):
    ref_url = urlparse(flask.request.host_url)
    test_url = urlparse(urljoin(flask.request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


class UserField(fields.StringField):
    """Field for specifying a user by email. Automatically ensures that user is
    present in the database, and allows access to the user model as `field.user()`.
    """

    # Override __init__ to add the Email validator after any other validators.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usermodel = None

    # pylint: disable=unused-argument
    def post_validate(self, form, validation_stopped):
        # As the final stage in validation, transform the given email into a
        # looked-up user. This is guaranteed to run after all other validators.
        # If lookup fails, raise a validation error, which will be caught and
        # displayed.

        # If validation was stopped, do not look up the user.
        if not validation_stopped:
            try:
                self.usermodel = models.User.query.filter_by(email=self.data.lower()).one()
            except NoResultFound as e:
                raise ValidationError("No user with email {!r} found".format(self.data.lower()))

    def user(self):
        return self.usermodel

class RedirectForm(FlaskForm):
    returnto = fields.HiddenField()

    def redirect(self, endpoint='front_page'):
        returnto = self.returnto.data or flask.url_for(endpoint)
        if is_safe_url(returnto):
            return flask.redirect(returnto)
        return flask.redirect(flask.url_for('front_page'))


class LoginForm(RedirectForm):
    email = fields.StringField('Email', [
        validators.required(),
        validators.Email(),
        validators.length(max=models.User.EMAIL_MAX_LENGTH)],
                               description="Email addresses  are case INSENSITIVE.")

    password = fields.PasswordField('Password',
                                    description="Never share tell your password with anyone.")

    submit = fields.SubmitField('Submit')

class WeekForm(FlaskForm):
    """A form for filling out a single week in a semester."""
    header = fields.StringField(
        'Header',
        [validators.required(), validators.length(max=models.Week.HEADER_MAX_LENGTH)],
        description=" Students will see this title on their side-bar next to its \
        corresponding week.")
    intro = fields.StringField(
        'Intro',
        [validators.required(), validators.length(max=models.Week.INTRO_MAX_LENGTH)],
        widget=widgets.TextArea(),
        description=" The intro is the content of the assignement for this week.\
    Use this guide to learn how to manipulate Markdown to write content to this field:\
    https://daringfireball.net/projects/markdown/basics")

    new_document = FileField()

    submit = fields.SubmitField('Submit')
    delete = fields.SubmitField('Delete')

class SemesterForm(FlaskForm):
    """A form for filling out an entire semester's syllabus at once."""
    name = fields.StringField('Name', [
        validators.required(),
        validators.length(max=models.Semester.NAME_MAX_LENGTH)])
    order = fields.IntegerField('Order', [validators.required()],
                                description="Counting order \
                                determines the order semesters are displayed \
    on the syllabus poge and assignement sidebar.")

    submit = fields.SubmitField('Submit')
    delete = fields.SubmitField('Delete')

class UserInfoForm(FlaskForm):
    name = fields.StringField('Name', [
        validators.required(),
        validators.length(max=models.User.NAME_MAX_LENGTH)],
                              description="Enter full legal name.")

    email = fields.StringField('Email Address', [
        validators.required(),
        validators.Email(),
        validators.length(max=models.User.EMAIL_MAX_LENGTH)],
                          description="Email addresses are case INSENSITIVE.")

    password = fields.PasswordField('Password')
    admin = fields.BooleanField('Administrator Account?',
                                description="Check to make the account an administror.")

    mentor = UserField('Mentor Email', [validators.optional()])

    # List semesters for the student to be enrolled in, with multiple allowed.
    # The choices need to be updated before rendering.
    semesters_enrolled = fields.SelectMultipleField('Semesters Enrolled', choices=[], coerce=int,
                                                    description="Select semesters to enroll the \
                                                    student in. Select multiple semesters by \
                                                    clicking and draging the mouse over a group of\
                                                    choices.")

    submit = fields.SubmitField('Submit')
    delete = fields.SubmitField('Delete')

    def populate_semesters(self):
        """Populate options for semester enrollment. Must be called after instantiation and before
        rendering.
        """
        # Sometimes, fields get deleted for tweaking. Make sure the one we're
        # operating one is not, otherwise do nothing.
        if self.semesters_enrolled is not None:
            self.semesters_enrolled.choices = [(s.id, s.name) for s \
                    in models.Semester.query.order_by('order')]

    def to_user_model(self, user=None):
        """Create a new user model, or fill out data in an existing one."""
        if user is None:
            user = models.User(self.email.data,
                               self.password.data,
                               self.name.data,
                               admin=(self.admin.data if self.admin else False))
        else:
            if self.email:
                user.email = self.email.data.lower()
            if self.password and self.password.data: # optional when not creating uesr
                user.password = self.password.data
            user.name = self.name.data
            if self.admin:
                user.admin = self.admin.data

        if self.mentor and self.mentor.user():
            user.mentors = [self.mentor.user()]
        user.semesters = list(self.get_semesters_enrolled())
        return user

    def get_semesters_enrolled(self):
        if self.semesters_enrolled is not None:
            return (models.Semester.query.get(sid) for sid in self.semesters_enrolled.data)
        return []

class FirstSetupUserInfoForm(UserInfoForm):
    setup_key = fields.StringField('Setup Key', [
        validators.required(),
        validators.Regexp('[a-zA-Z0-9]{32}',
                          message='Must resemble 4eb27b69ddc1d1b8866c0beb4de3d643'),
    ])

    # pylint: disable=no-self-argument,no-self-use
    def validate_setup_key(form, field):
        """In-line validator to check that setup_token matches the one generated
        on startup, and to ensure that one was generated at all. This is called
        automatically as part of the form.validate() process.
        """
        if 'SETUP_KEY' not in app.config:
            raise ValidationError('No SETUP_KEY in use by the application')
        elif field.data != app.config['SETUP_KEY']:
            # NOTE: This kind of comparison might be subject to timing attacks, where
            # an attacker submits random strings and compares how long it takes
            # to return that they fail in order to deduce the correct string.
            # This should be changed to a suitable method of comparison, such as
            # comparison by hash.
            raise ValidationError('Provided SETUP_KEY does not match application SETUP_KEY')


class AnnouncementForm(FlaskForm):
    title = fields.StringField('Title', [
        validators.required(),
        validators.length(max=models.Announcement.TITLE_MAX_LENGTH)],
                               description="Enter a descriptive title \
                               for the new anouncement here.")

    content = fields.StringField('Content', [
        validators.required(),
        validators.length(max=models.Announcement.CONTENT_MAX_LENGTH)],
                                 widget=widgets.TextArea(),
                                 description="Enter content for the announcement.\
                               All content entered \
        here will be viewable on the home page by all users - including guests. \
        Use this guide to learn how to manipulate Markdown to write content to this field: \
        https://daringfireball.net/projects/markdown/basics")

    submit = fields.SubmitField('Submit')
    preview = fields.SubmitField('Preview')
    delete = fields.SubmitField('Delete')

class DatabaseUploadForm(FlaskForm):
    zipfile = FileField(validators=[FileRequired()])
