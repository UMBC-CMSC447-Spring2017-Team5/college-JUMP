import subprocess
import string
import os
import binascii
from functools import wraps
import markdown

from flask import Flask, request, abort, Markup
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect

# Flask convention is to use `app`
app = Flask(__name__) # pylint: disable=invalid-name
Bootstrap(app)
app.bcrypt = Bcrypt()
app.db = SQLAlchemy()

app.login_manager = LoginManager()
app.login_manager.login_view = 'login_page'

def init_app():
    app.bcrypt.init_app(app)
    app.db.init_app(app)
    app.login_manager.init_app(app)
    CSRFProtect(app)

try:
    from collegejump._version import __version__
except ImportError:
    app.logger.warning("WARN: no _version.py; is the package installed? using SCM instead")
    import collegejump.scmtools
    __version__ = collegejump.scmtools.get_scm_version()

# Make the version easily accessible
app.config['VERSION'] = __version__

# Make a random SECRET_KEY. See #26.
app.config['SECRET_KEY'] = binascii.hexlify(os.urandom(32)).decode('utf-8')

# Set SQLAlchemy options that'll never change
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set the repository links here, so they're less hard-coded elsewhere
app.config['REPOSITORY_HOME'] = 'https://github.com/UMBC-CMSC447-Spring2017-Team5/college-JUMP'
app.config['REPOSITORY_ISSUES'] = app.config['REPOSITORY_HOME'] + '/issues'

# Register a function to run before other requests.
@app.before_first_request
def prepare_after_init():
    from collegejump import models

    app.db.create_all()

    # If there are no admins in the database, create and store SETUP_KEY for
    # creating the first admin.
    if models.User.query.filter_by(admin=True).count() == 0:
        app.config['SETUP_KEY'] = binascii.hexlify(os.urandom(16)).decode('utf-8')
        app.logger.info("No admins in database, created setup key: %s",
                        app.config['SETUP_KEY'])

# Register a handy template filter
@app.template_filter('markdown')
def markdown_filter(data):
    return Markup(markdown.markdown(data))

# Register an admin_required handler, for ensuring that users are logged-in
# admins when they access certain pages.
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()
        elif not current_user.admin:
            return abort(401)
        return func(*args, **kwargs)
    return decorated_view

# We import the views here so that the application still mostly works even if
# the main() function isn't ever run.
import collegejump.views # pylint: disable=wrong-import-position
