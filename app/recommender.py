from embedding_utils import get_embedding, get_all_embeddings
from db_utils import fetch_product_by_name, fetch_all_products
from sklearn.metrics.pairwise import cosine_similarity

def get_recommendations(product_name, top_n=5):
    target = fetch_product_by_name(product_name)
    if not target:
        return []

    target_embedding = get_embedding(target['description'])
    all_products = fetch_all_products()
    all_embeddings = get_all_embeddings()

    similarities = cosine_similarity([target_embedding], all_embeddings)[0]
    sorted_indices = similarities.argsort()[::-1]

    recommendations = []
    for idx in sorted_indices:
        if all_products[idx]['id'] != target['id']:
            recommendations.append(all_products[idx])
        if len(recommendations) == top_n:
            break
    return recommendations
