from flask_wtf import FlaskForm
from wtforms import fields, validators
import flask

from collegejump import models

class RedirectForm(FlaskForm):
    next = fields.HiddenField()

    def redirect(self, endpoint='front_page', **values):
        next = self.next.data or flask.url_for(endpoint)
        #if is_safe_url(self.next.data):
        return flask.redirect(next)

class LoginForm(RedirectForm):
    email = fields.StringField('Email Address', [
        validators.required(),
        validators.Email(),
        validators.length(max=models.User.EMAIL_MAX_LENGTH),
    ])
    password = fields.PasswordField('Password')
