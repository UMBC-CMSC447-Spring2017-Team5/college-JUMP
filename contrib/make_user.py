#!/usr/bin/env python3

import argparse
import collegejump
import os
import sys

def main(args):
    collegejump.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
        os.path.join(os.getcwd(), args.db))

    collegejump.init_app()
    with collegejump.app.app_context():
        collegejump.app.db.create_all()

        user = collegejump.models.User(args.email, args.passwd)
        user.name = args.name
        user.admin = args.admin

        collegejump.app.db.session.add(user)
        collegejump.app.db.session.commit()

        print("{!r} created".format(user))

    return 0

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('email')
    parser.add_argument('passwd')
    parser.add_argument('--admin', action='store_true')
    parser.add_argument('--db', default='local.db')
    return parser.parse_args()

if __name__ == "__main__":
    sys.exit(main(parse()))
