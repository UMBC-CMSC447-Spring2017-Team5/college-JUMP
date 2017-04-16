import csv
import io
import zipfile

from collegejump import app

# Create any absent tables.
def export_db():
    """Export all of the tables in the database as separate CSV files stored in
    aa ZIP file (in memory, in a BytesIO buffer) suitable for later re-import,
    or archiving.
    """
    # Create an in-memory bytes buffer for storing the file.
    archive_buf = io.BytesIO()

    # Create the in-memory zip file inside the buffer
    with zipfile.ZipFile(archive_buf, 'w') as archive:
        # For each table in the database, create a CSV file for it.
        for table in app.db.metadata.sorted_tables:
            table_name = "{}.csv".format(table.name)
            table_buf = io.StringIO()
            table_writer = csv.writer(table_buf)

            # Get all records from the database and marshal them into CSV.
            records = app.db.session.query(table).all()
            table_writer.writerows(records)

            # Write the CSV file into the ZIP file.
            archive.writestr(table_name, table_buf.getvalue())

    # Return to the start of the bytes IO reader.
    archive_buf.seek(0)
    return archive_buf
