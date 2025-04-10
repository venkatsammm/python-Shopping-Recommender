from sentence_transformers import SentenceTransformer
from db_utils import fetch_all_products

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text, normalize_embeddings=True)

def get_all_embeddings():
    products = fetch_all_products()
    descriptions = [p['description'] for p in products]
    return model.encode(descriptions, normalize_embeddings=True)
