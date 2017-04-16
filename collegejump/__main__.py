#!env/bin/python3

import argparse
import getpass
import logging
import os
import sys

import werkzeug
from werkzeug.wsgi import DispatcherMiddleware

def main(args):
    # We cannot import app outside of this function, to avoid circular imports.
    from collegejump import app, init_app, __version__

    if(args.version):
        print(__version__)
        return 0

    # Prepare logging.
    level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    app.logger.setLevel(level)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
            os.path.join(os.getcwd(), args.db))
    app.config["VERSION"] = __version__

    app.secret_key = os.urandom(24)

    # If the application is prefixed, such as behind a web proxy, then we need
    # middleware to rewrite urls. Otherwise, do no such rewriting.
    if args.prefix:
        app.config["APPLICATION_ROOT"] = args.prefix
        app.wsgi_app = werkzeug.wsgi.DispatcherMiddleware(
                werkzeug.utils.redirect(app.config["APPLICATION_ROOT"], 301),
                {app.config["APPLICATION_ROOT"]: app.wsgi_app})
    else:
        app.config["APPLICATION_ROOT"] = '/'

    # We initailize the applications once configuration options are set.
    init_app()

    # Gain app context for all other operations.
    with app.app_context():
        print("Starting College JUMP Website version '{}'".format(__version__))
        app.db.create_all()
        app.run(host=args.host, port=args.port, debug=args.debug)

# Decode command line arguments using argparse
def parse(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8088, type=int)
    parser.add_argument('--prefix', default=None)
    parser.add_argument('--db', default='local.db')
    parser.add_argument('--debug', action='store_true', default=True)
    parser.add_argument('--version', action='store_true')

    return parser.parse_args(argv)

# If running this as a script, execute the main function. This is just a
# good-practice Python idiom.
if __name__ == '__main__':
    sys.exit(main(parse(None)))
