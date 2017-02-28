from flask import Flask

try:
    from collegejump._version import __version__
except ImportError:
    print("WARN: no version.py; is the package installed??")
    __version__ = "development"

app = Flask(__name__)
app.config['VERSION'] = __version__

from collegejump import views
