#!env/bin/python3

import argparse
import logging
import os
import sys

import werkzeug

# pylint: disable=line-too-long
GCAL_LINK = 'https://calendar.google.com/calendar/embed?src=umbc.edu_p0a471t6hmiam37dqk97kgefqs%40group.calendar.google.com&ctz=America/New_York'

def main(args):
    # We cannot import app outside of this function, to avoid circular imports.
    from collegejump import app, init_app, __version__

    if args.version:
        app.logger.info(__version__)
        return 0

    # Prepare logging.
    level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"))
    app.logger.addHandler(stdout_handler)
    app.logger.setLevel(level)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
        os.path.join(os.getcwd(), args.db))
    app.config["VERSION"] = __version__

    app.secret_key = os.urandom(24)

    if args.gcal:
        app.config['COLLEGEJUMP_GCAL_LINK'] = args.gcal

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
        app.logger.info("Starting College JUMP Website version '%s'", __version__)
        app.run(host=args.host, port=args.port, debug=args.debug)

# Decode command line arguments using argparse


def parse(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8088, type=int)
    parser.add_argument('--prefix', default=None)
    parser.add_argument('--db', default='local.db')
    parser.add_argument('--gcal', default=GCAL_LINK)

    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--version', action='store_true')

    return parser.parse_args(argv)

# If running this as a script, execute the main function. This is just a
# good-practice Python idiom.
if __name__ == '__main__':
    sys.exit(main(parse(None)))
