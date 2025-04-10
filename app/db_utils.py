# File: app/db_utils.py

from sqlalchemy import create_engine, text
import os
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()

# Replace with your actual Postgres URL or store in .env
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://neondb_owner:npg_6OSdFr7WoiwN@ep-still-violet-a53t7hro-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
engine: Engine = create_engine(POSTGRES_URL)


def fetch_all_products():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products"))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]


def fetch_product_by_name(name):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products WHERE name = :name"), {"name": name})
        row = result.fetchone()
        return dict(row._mapping) if row else None
