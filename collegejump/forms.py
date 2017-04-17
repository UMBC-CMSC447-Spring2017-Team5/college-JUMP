from flask_wtf import FlaskForm
from wtforms import fields, validators
import flask

from collegejump import models


class RedirectForm(FlaskForm):
    returnto = fields.HiddenField()

    def redirect(self, endpoint='front_page'):
        returnto = self.returnto.data or flask.url_for(endpoint)
        # if is_safe_url(self.returnto.data):
        return flask.redirect(returnto)


class LoginForm(RedirectForm):
    email = fields.StringField('Email Address', [
        validators.required(),
        validators.Email(),
        validators.length(max=models.User.EMAIL_MAX_LENGTH),
    ])
    password = fields.PasswordField('Password')


class UserInfoForm(RedirectForm):
    name = fields.StringField('Name', [
        validators.required(),
        validators.length(max=models.User.NAME_MAX_LENGTH)])

    email = fields.StringField('Email Address', [
        validators.required(),
        validators.Email(),
        validators.length(max=models.User.EMAIL_MAX_LENGTH)])

    admin = fields.BooleanField('Is Administrator Account?')
    password = fields.PasswordField('Password')
