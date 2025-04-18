import requests
from sqlalchemy import create_engine, text
import bcrypt

# PostgreSQL connection string
POSTGRES_URL = "postgresql://neondb_owner:npg_6OSdFr7WoiwN@ep-still-violet-a53t7hro-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(POSTGRES_URL)

# Create products table
create_products_table_sql = """
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT,
    price REAL,
    image_url TEXT,
     
);
"""

# Create users table
create_users_table_sql = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    gender TEXT CHECK (gender IN ('male', 'female', 'other'))
);
"""

# Fetch product data from DummyJSON API
response = requests.get("https://dummyjson.com/products?limit=50")
data = response.json()

# Handle response structure
if isinstance(data, dict) and "products" in data:
    products = data["products"]
elif isinstance(data, list):
    products = data
else:
    print("⚠️ Unexpected API response structure.")
    products = []

# Create tables and insert data
with engine.begin() as conn:
    # Create tables
    conn.execute(text(create_products_table_sql))
    conn.execute(text(create_users_table_sql))

    # Insert products
    for product in products:
        insert_sql = text("""
            INSERT INTO products (name, description, category, price, image_url)
            VALUES (:name, :description, :category, :price, :image_url)
            ON CONFLICT DO NOTHING;
        """)
        conn.execute(insert_sql, {
            "name": product["title"],
            "description": product["description"],
            "category": product["category"],
            "price": product["price"],
            "image_url": product["thumbnail"]
        })

print("✅ Tables created and product data inserted.")
