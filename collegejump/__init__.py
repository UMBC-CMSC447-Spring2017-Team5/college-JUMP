from flask import Flask

__version__ = None
try:
    from collegejump._version import __version__
except ImportError:
    print("WARN: no _version.py; is the package installed??")
    __version__ = "development"

app = Flask(__name__)
app.config['VERSION'] = __version__

from collegejump import views
