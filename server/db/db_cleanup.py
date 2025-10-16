#!/usr/bin/env python3
"""
Database cleanup script.
Can be run from the db directory with: python3 db_cleanup.py
"""

import sys
from pathlib import Path

# Add the server directory to the Python path so we can import from it
# This is the clean way to handle imports when running from a subdirectory
current_dir = Path(__file__).resolve().parent
server_dir = current_dir.parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))

# Now we can import using the server as the base path
# Note: load_dotenv() is called automatically when app.py is imported
from app import create_app
from extensions import db

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        # Drop all tables defined in Flask-SQLAlchemy models
        db.drop_all()
        print("All tables dropped in the database.")
