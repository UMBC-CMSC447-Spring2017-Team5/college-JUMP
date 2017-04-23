import csv
import io
import zipfile
import sqlalchemy_utils

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

def import_db(archive_path_or_buf):
    """DESTROY THE OLD DATABASE and import all of the tables in an archive as
    prepared by `export_db()`."""

    app.db.create_all()

    connection = app.db.engine.connect()
    transaction = connection.begin()

    # Open the in-memory zip file.
    with zipfile.ZipFile(archive_path_or_buf, 'r') as archive:
        # For each table in the database, check if there is a CSV file
        # associated.
        for table in app.db.metadata.sorted_tables:
            table_name = "{}.csv".format(table.name)
            try:
                with archive.open(table_name, 'r') as table_buf:
                    app.logger.debug("Opened %r for import", table_name)
                    table_buf_str = io.TextIOWrapper(table_buf, encoding='utf-8')
                    table_reader = csv.DictReader(table_buf_str,
                                                  fieldnames=[c.name for c in table.columns])


                    # Some tables need special treatment, and cannot dump the
                    # rows directly back into the database. If so, the model
                    # will have `transform_csv_row` as a classmethod.
                    model = sqlalchemy_utils.get_class_by_table(app.db.Model, table)
                    if hasattr(model, 'transform_csv_row'):
                        app.logger.debug("Using row transformer from model %r for %s",
                                         model, table.name)
                        transform = model.transform_csv_row
                    else:
                        # No-op
                        transform = lambda row: row

                    app.logger.warning("Deleting all rows of %s", table.name)
                    connection.execute(table.delete())

                    for row in table_reader:
                        app.logger.debug("Importing row into %s: %r", table.name, row)
                        row = transform(row)
                        connection.execute(table.insert(values=row))
            except:
                transaction.rollback()
                raise

    transaction.commit()
    return
