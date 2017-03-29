from flask_sqlalchemy import SQLAlchemy

from collegejump import app

# SQLAlchemy database connection is exposed via this element.
app.db = SQLAlchemy(app)

# Load the model definitions
from collegejump import models

# Create any absent tables.
app.db.create_all()
