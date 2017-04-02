from flask import Flask
import subprocess, string

import collegejump.scmtools

try:
    from collegejump._version import __version__
except ImportError:
    print("WARN: no _version.py; is the package installed? using SCM instead")
    __version__ = collegejump.scmtools.get_scm_version()

app = Flask(__name__)

# Extract version information from the global __version__ set earlier
app.config['VERSION'] = __version__

# Set the database path and other SQLAlchemy options.
# TODO: extract this from a configuration file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from collegejump import views
