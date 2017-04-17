#!/usr/bin/env python3

import sys
import collegejump

collegejump.init_app()
with collegejump.app.app_context():
    collegejump.database.import_db(sys.argv[1])
    for table in collegejump.app.db.metadata.sorted_tables:
        print(table)
        for row in collegejump.app.db.engine.execute(table.select()):
            print(row)
