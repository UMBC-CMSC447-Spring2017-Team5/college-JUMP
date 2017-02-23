#!env/bin/python3

import argparse
import logging
import subprocess
import sys

import werkzeug
from werkzeug.wsgi import DispatcherMiddleware

def main(args):
    from collegejump import app

    # Prepare logging.
    level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    app.logger.setLevel(level)

    version = {}
    try:
        version["string"] = subprocess.check_output(
                ['git', 'describe', '--always', '--dirty=+']).decode('UTF-8').strip()

        # Note that the version was from the version control system
        version["from_vcs"] = True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        app.logger.warn("Could not get version info: {}".format(repr(e)))
        pass

    app.logger.info("Starting College JUMP Website version '{}'" \
            .format(version.get("string")))
    app.config["VERSION"] = version

    # If the application is prefixed, such as behind a web proxy, then we need
    # middleware to rewrite urls. Otherwise, do no such rewriting.
    if args.prefix:
        app.config["APPLICATION_ROOT"] = args.prefix
        app.wsgi_app = werkzeug.wsgi.DispatcherMiddleware(
                werkzeug.utils.redirect(app.config["APPLICATION_ROOT"], 301),
                {app.config["APPLICATION_ROOT"]: app.wsgi_app})
    else:
        app.config["APPLICATION_ROOT"] = '/'

    app.run(host=args.host, port=args.port, debug=args.debug)

# Decode command line arguments using argparse
def parse(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8088, type=int)
    parser.add_argument('--prefix', default=None)
    parser.add_argument('--debug', action='store_true', default=True)
    return parser.parse_args(argv)

# If running this as a script, execute the main function. This is just a
# good-practice Python idiom.
if __name__ == '__main__':
    sys.exit(main(parse(None)))
