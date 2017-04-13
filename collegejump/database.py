from flask_sqlalchemy import SQLAlchemy
import csv
import io
import zipfile

from collegejump import app

# SQLAlchemy database connection is exposed via this element.
app.db = SQLAlchemy(app)

# Load the model definitions
from collegejump import models

# Create any absent tables.
app.db.create_all()

def export_db(db):
    """Export all of the tables in the database as separate CSV files stored in
    aa ZIP file (in memory, in a BytesIO buffer) suitable for later re-import,
    or archiving.
    """

    print("Exporting database")

    # Create an in-memory bytes buffer for storing the file.
    archive_buf = io.BytesIO()

    # Create the in-memory zip file inside the buffer
    with zipfile.ZipFile(archive_buf, 'w') as archive:
        # For each table in the database, create a CSV file for it.
        for t in db.metadata.sorted_tables:
            table_name = "{}.csv".format(t.name)
            table_buf = io.StringIO()
            table_writer = csv.writer(table_buf)

            # Get all records from the database and marshal them into CSV.
            records = db.session.query(t).all()
            table_writer.writerows(records)

            # Write the CSV file into the ZIP file.
            archive.writestr(table_name, table_buf.getvalue())

    # Return to the start of the bytes IO reader.
    archive_buf.seek(0)
    return archive_buf

def import_db(db, archive_path_or_buf):
    """Import the tables from the zip archive, as prepared by `export_db()`,
    while REPLACING EXISTING TABLES.
    """

    print("Importing database")

    # Open the zip archive.
    with zipfile.ZipFile(archive_path_or_buf, 'r') as archive:
        # For each table in the database, check if there is a CSV file
        # associated.
        for t in db.metadata.sorted_tables:
            table_name = "{}.csv".format(t.name)
            try:
                table_buf = archive.read(table_name)
            except:
                # If the table CSV doesn't exist, skip it.
                print("Table '{}' missing in archive, skipping import".format(t))
                continue

            table_reader = csv.reader(table_buf)
            raise NotImplementedError
