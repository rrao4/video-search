from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, MetaData

load_dotenv()
database_url = os.getenv("ANN_URL")

engine = create_engine(
    database_url,
    echo=True,        # Optional: log all SQL queries for debugging
)

if __name__ == "__main__":
    metadata = MetaData()
    metadata.reflect(bind=engine)

    with engine.begin() as conn:
        metadata.drop_all(bind=conn)
    print("All tables dropped in the database referenced by ANN_URL.")
