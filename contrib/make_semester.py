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

        semester = collegejump.models.Semester(args.name, args.order)

        collegejump.app.db.session.add(semester)
        collegejump.app.db.session.commit()

        print("{!r} created".format(semester))

    return 0

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('order', type=int)
    parser.add_argument('--db', default='local.db')
    return parser.parse_args()

if __name__ == "__main__":
    sys.exit(main(parse()))
