from urllib.parse import  urlparse, urljoin
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from wtforms import fields, validators, widgets
from wtforms.validators import StopValidation, ValidationError
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
            except NoResultFound:
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
    email = fields.StringField('Email',
                               filters=[lambda s: s.lower() if s else s],
                               validators = [
                                   validators.required(),
                                   validators.Email(),
                                   validators.length(max=models.User.EMAIL_MAX_LENGTH)],
                               description="Email addresses are case insensitive.")

    password = fields.PasswordField('Password', [validators.required()],
                                    description="Never share your password with anyone.")

    submit = fields.SubmitField('Submit')

    user_model = None

    # pylint: disable=no-self-argument,no-self-use
    def validate_email(form, field):
        """One-off validator to ensure that the given user exists."""
        # Get the user and store it, for convenience.
        try:
            form.user_model = models.User.query.filter_by(email=field.data).one()
        except NoResultFound:
            raise StopValidation('No user with that email exists')

    # pylint: disable=no-self-argument,no-self-use
    def validate_password(form, field):
        """One-off validator to ensure that the password matches. This always
        runs after the email validator, so if it passed, we can assume `_user`
        is filled.
        """
        if form.user_model is not None:
            if not form.user_model.check_password(field.data):
                raise ValidationError('Incorrect password')

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

    assignment_name = fields.StringField('Assignment Name', [
        validators.optional(),
        validators.length(max=models.Assignment.NAME_MAX_LENGTH)])

    assignment_instructions = fields.TextAreaField(
        'Assignment Instructions',
        [validators.optional(), validators.length(max=models.Assignment.INSTRUCTIONS_MAX_LENGTH)],
        description="Students will be presented with a text box, and their \
                responses sent to their mentors.")

    new_document = FileField(description="Add one file for download by students. "
                                         "Multiple files may be added by submitting "
                                         "this form multiple times.")

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
    on the syllabus page and assignment sidebar.")

    submit = fields.SubmitField('Submit')
    delete = fields.SubmitField('Delete')

    # pylint: disable=no-self-argument,no-self-use
    def validate_order(form, field):
        """One-off validator to ensure that the given order is unique to this
        semester, and no other exists in the database.
        """
        # If the data matches the object used to construct the form, do not search the database.
        if field.data == field.object_data:
            return

        # Retrieve a matching semester, if there is one. If NoResultFound, then
        # there's no issue.
        try:
            other = models.Semester.query.filter_by(order=field.data).one()
            raise ValidationError('The semester {!r} has the same order'.format(other.name))
        except NoResultFound:
            pass

class UserForm(FlaskForm):
    name = fields.StringField('Name', [
        validators.required(),
        validators.length(max=models.User.NAME_MAX_LENGTH)],
                              description="Enter full legal name.")

    email = fields.StringField('Email Address',
                               filters=[lambda s: s.lower() if s else s],
                               validators=[
                                   validators.required(),
                                   validators.Email(),
                                   validators.length(max=models.User.EMAIL_MAX_LENGTH)],
                               description="Email addresses are case INSENSITIVE.")

    password = fields.PasswordField('Password')
    admin = fields.BooleanField('Administrator Account?',
                                description="Check to make the account an administror.")

    mentors = fields.StringField('Mentor Emails',
                                 filters=[lambda s: s.lower().replace(' ','') if s else s],
                                 validators=[validators.optional()],
                                 description="List of mentor emails, comma separated")

    # List semesters for the student to be enrolled in, with multiple allowed.
    # The choices need to be updated before rendering.
    semesters_enrolled = fields.SelectMultipleField('Semesters Enrolled', choices=[], coerce=int,
                                                    description="Select semesters to enroll the \
                                                    student in. Select multiple semesters by \
                                                    clicking and draging the mouse over a group of\
                                                    choices.")

    submit = fields.SubmitField('Submit')
    delete = fields.SubmitField('Delete')

    def __init__(self, *args, require_password=True, **kwargs):
        super().__init__(*args, **kwargs)

        if require_password:
            self.password.validators.append(validators.required())
            self.password.flags.required = True
        else:
            self.password.validators.append(validators.optional())
            self.password.flags.required = False

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
                user.email = self.email.data
            if self.password and self.password.data: # optional when not creating uesr
                user.password = self.password.data
            user.name = self.name.data
            if self.admin:
                user.admin = self.admin.data

        if self.mentors and self.mentors.data:
            user.mentors = [models.User.query.filter_by(email=mentor_email).one()
                            for mentor_email in self.mentors.data.split(',')]

        user.semesters = list(self.get_semesters_enrolled())
        return user

    def get_semesters_enrolled(self):
        if self.semesters_enrolled is not None:
            return (models.Semester.query.get(sid) for sid in self.semesters_enrolled.data)
        return []

    # pylint: disable=no-self-argument,no-self-use
    def validate_email(form, field):
        """One-off validator to ensure that the given email is unique to this
        user, and no other exists in the database.
        """
        # If the data matches the object used to construct the form, do not search the database.
        if field.data == field.object_data:
            return

        # Build the query to check existence.
        exists_query = models.User.query.filter_by(email=field.data).exists()
        # Execute the query and select only the True/False result
        exists = app.db.session.query(exists_query).scalar()
        if exists:
            raise ValidationError('Another user has that email address')

    # pylint: disable=no-self-argument,no-self-use
    def validate_mentors(form, field):
        """One-off validator to ensure that each of the list of given emails
        exists, and is not the entered email.
        """
        for mentor_email in field.data.split(','):
            # Check that this email is not the same as this user.
            if mentor_email == form.email.data or mentor_email == form.email.object_data:
                raise ValidationError('A user cannot be their own mentor')

            # Build the query to check existence.
            exists_query = models.User.query.filter_by(email=mentor_email).exists()
            # Execute the query and select only the True/False result
            exists = app.db.session.query(exists_query).scalar()
            if not exists:
                raise ValidationError('No user exists with email {}'.format(mentor_email))

class FirstSetupUserInfoForm(UserForm):
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
                               for the new announcement here.")

    content = fields.StringField('Content', [
        validators.required(),
        validators.length(max=models.Announcement.CONTENT_MAX_LENGTH)],
                                 widget=widgets.TextArea(),
                                 description="Enter content for the announcement.\
                               Markdown enabled. Use \
        <a href=https://daringfireball.net/projects/markdown/basics>this guide</a> \
        to learn more.")

    submit = fields.SubmitField('Submit')
    preview = fields.SubmitField('Preview')
    delete = fields.SubmitField('Delete')

class AnswerForm(FlaskForm):
    response = fields.TextAreaField('Response')
    submit = fields.SubmitField('Submit')

class FeedbackForm(RedirectForm):
    feedback = fields.TextAreaField('Feedback')
    submit = fields.SubmitField('Submit')

class DatabaseUploadForm(FlaskForm):
    zipfile = FileField(validators=[FileRequired()])
