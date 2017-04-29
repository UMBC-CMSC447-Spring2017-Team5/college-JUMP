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
    email = fields.StringField('Email Address', [
        validators.required(),
        validators.Email(),
        validators.length(max=models.User.EMAIL_MAX_LENGTH),
    ])
    password = fields.PasswordField('Password')

class WeekForm(FlaskForm):
    """A form for filling out a single week in a semester."""
    header = fields.StringField('Header', [
        validators.required(),
        validators.length(max=models.Week.HEADER_MAX_LENGTH)])
    intro = fields.StringField('Intro', [
        validators.required(),
        validators.length(max=models.Week.INTRO_MAX_LENGTH)])

    new_document = FileField()

    submit = fields.SubmitField('Submit')

class SemesterForm(FlaskForm):
    """A form for filling out an entire semester's syllabus at once."""
    name = fields.StringField('Name', [
        validators.required(),
        validators.length(max=models.Semester.NAME_MAX_LENGTH)])
    order = fields.IntegerField('Order', [validators.required()])

    weeks = fields.FieldList(fields.FormField(WeekForm))

    submit = fields.SubmitField('Submit')
    add_week = fields.SubmitField('Add Week')

class UserInfoForm(FlaskForm):
    name = fields.StringField('Name', [
        validators.required(),
        validators.length(max=models.User.NAME_MAX_LENGTH)])

    email = fields.StringField('Email Address', [
        validators.required(),
        validators.Email(),
        validators.length(max=models.User.EMAIL_MAX_LENGTH)])

    admin = fields.BooleanField('Is Administrator Account?')
    password = fields.PasswordField('Password')

    def to_user_model(self):
        user = models.User(self.email.data.lower(), self.password.data)
        user.name = self.name.data
        user.admin = self.admin.data
        return user

class FirstSetupUserInfoForm(UserInfoForm):
    setup_key = fields.HiddenField()

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


class UserDeleteForm(FlaskForm):
    delete = fields.BooleanField('Mark account for deletion?')

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
