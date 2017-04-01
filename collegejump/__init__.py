from flask import Flask
import subprocess, string

def get_git_revision_hash():
    try:
        s = str(subprocess.check_output(["git", "describe", "--always"]).strip())
        # return format is like b'versionstring'\n
        # so partition between apostrophe character
        s = s.partition('\'')[-1].rpartition('\'')[0]
        return s
    except:
        return "Subprocess Exception"

#try:
#    from collegejump._version import __version__
#except ImportError:
#    print("WARN: no _version.py; is the package installed??")
__version__ = "College JUMP version " + get_git_revision_hash()


app = Flask(__name__)

# Extract version information from the global __version__ set earlier
app.config['VERSION'] = __version__

# Set the database path and other SQLAlchemy options.
# TODO: extract this from a configuration file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from collegejump import views
