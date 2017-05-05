from urllib.parse import  urlparse, urljoin
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import fields, validators, widgets, ValidationError
import flask

from collegejump import app, models

def is_safe_url(target):
    ref_url = urlparse(flask.request.host_url)
    test_url = urlparse(urljoin(flask.request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


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
        validators.length(max=models.User.EMAIL_MAX_LENGTH),
    ])
    password = fields.PasswordField('Password')
    submit = fields.SubmitField('Submit')

class WeekForm(FlaskForm):
    """A form for filling out a single week in a semester."""
    header = fields.StringField(
        'Header',
        [validators.required(), validators.length(max=models.Week.HEADER_MAX_LENGTH)])
    intro = fields.StringField(
        'Intro',
        [validators.required(), validators.length(max=models.Week.INTRO_MAX_LENGTH)])

    new_document = FileField()

    submit = fields.SubmitField('Submit')

class SemesterForm(FlaskForm):
    """A form for filling out an entire semester's syllabus at once."""
    name = fields.StringField('Name', [
        validators.required(),
        validators.length(max=models.Semester.NAME_MAX_LENGTH)])
    order = fields.IntegerField('Order', [validators.required()])

    submit = fields.SubmitField('Submit')
    delete = fields.SubmitField('Delete')

class UserInfoForm(FlaskForm):
    name = fields.StringField('Name', [
        validators.required(),
        validators.length(max=models.User.NAME_MAX_LENGTH)])

    password = fields.PasswordField('Password')
    submit = fields.SubmitField('Submit')

    def to_user_model(self):
        user = models.User(self.password.data, self.name.data)  
        return user
        
class UserInfoAdminForm(UserInfoForm):
    
    email = fields.StringField('Email Address', [
        validators.required(),
        validators.Email(),
        validators.length(max=models.User.EMAIL_MAX_LENGTH)])
        
    admin = fields.BooleanField('Is Administrator Account?')

    # List semesters for the student to be enrolled in, with multiple allowed.
    # The choices need to be updated before rendering.
    semesters_enrolled = fields.SelectMultipleField('Semesters Enrolled', choices=[], coerce=int)

    delete = fields.SubmitField('Delete')

    def populate_semesters(self):
        """Populate options for semester enrollment. Must be called after instantiation and before
        rendering.
        """
        self.semesters_enrolled.choices = [(s.id, s.name) for s \
                in models.Semester.query.order_by('order')]

    def to_user_model(self):
        user = models.User(self.email.data,
                           self.password.data,
                           self.name.data,
                           admin=self.admin.data)
        user.semesters = list(self.get_semesters_enrolled())
        return user

    def get_semesters_enrolled(self):
        return (models.Semester.query.get(sid) for sid in self.semesters_enrolled.data)

class FirstSetupUserInfoForm(UserInfoAdminForm):
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
        validators.length(max=models.Announcement.TITLE_MAX_LENGTH)])
    content = fields.StringField('Content', [
        validators.required(),
        validators.length(max=models.Announcement.CONTENT_MAX_LENGTH)],
                                 widget=widgets.TextArea())

    submit = fields.SubmitField('Submit')
    preview = fields.SubmitField('Update Preview')

class DatabaseUploadForm(FlaskForm):
    zipfile = FileField(validators=[FileRequired()])
