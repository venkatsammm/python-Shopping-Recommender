import streamlit as st
from recommender import get_recommendations
from db_utils import fetch_all_products

st.title("🛍️ Product Recommender")

products = fetch_all_products()
product_names = [prod['name'] for prod in products]

selected_product = st.selectbox("Choose a product:", product_names)

if selected_product:
    recommendations = get_recommendations(selected_product)
    st.subheader("🔍 Similar Products")
    for item in recommendations:
        st.image(item['image_url'], width=150)
        st.write(f"**{item['name']}** — {item['category']}")
        st.write(item['description'][:150] + "...")
        st.markdown("---")
