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
def create_user(username, email, password_hash, gender):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO users (username, email, password_hash, gender)
            VALUES (:username, :email, :password_hash, :gender)
        """), {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "gender": gender
        })

def get_user_by_email(email):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
        row = result.fetchone()
        return dict(row._mapping) if row else None
def get_user_by_username(username):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM users WHERE username = :username
        """), {"username": username})
        return result.fetchone()
def fetch_product_category(product_id):
    """
    Alternative implementation if categories are stored directly in the products table.
    """
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT category FROM products WHERE id = :product_id"),
            {"product_id": product_id}
        )
        row = result.fetchone()
        return row[0] if row else None