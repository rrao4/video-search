# run with `python3 -m db.db_init` from project root
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from db.db_tables import Base

load_dotenv()
database_url = os.getenv("ANN_URL")

engine = create_engine(
    database_url,
    echo=True,        # Optional: log all SQL queries for debugging
)

if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))  # pgvector extension name is 'vector'
    Base.metadata.create_all(bind=engine) # Create all tables in video_tables.py and user_tables.py
    print("Tables created.")
