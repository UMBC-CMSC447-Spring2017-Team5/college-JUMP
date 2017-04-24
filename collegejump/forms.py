from urllib.parse import  urlparse, urljoin
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import fields, validators, widgets
import flask

from collegejump import models

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
