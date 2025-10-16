"""
Database initialization script.
Can be run from the db directory with: python3 db_init.py
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Add the server directory to the Python path so we can import from it
current_dir = Path(__file__).resolve().parent
server_dir = current_dir.parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))

from app import create_app
from extensions import db

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        # Create the vector extension first
        with db.engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))  # pgvector extension name is 'vector'
        
        # Create all tables defined in Flask-SQLAlchemy models
        db.create_all()
        print("Tables created.")
