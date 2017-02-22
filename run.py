#!env/bin/python3

import argparse
import logging
import subprocess
import sys

def main(args):
    from app import app

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
    app.run(host=args.host, port=args.port, debug=args.debug)

# Decode command line arguments using argparse
def parse(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=8080, type=int)
    parser.add_argument('--debug', action='store_true', default=True)
    return parser.parse_args(argv)

# If running this as a script, execute the main function. This is just a
# good-practice Python idiom.
if __name__ == '__main__':
    sys.exit(main(parse(None)))
