# 🛍️ Intelligent Product Recommender System

## 📌 Project Overview

The **Intelligent Product Recommender System** analyzes product descriptions using **NLP embeddings** and compares them using **Cosine Similarity** to suggest semantically similar items.

It uses:

- 🧠 **NLP-based Embeddings** – to understand descriptions beyond simple keyword matching  
- 🧮 **Cosine Similarity** – to compute similarity between products  
- 🗄️ **SQL** – to store and fetch product data  
- 🖼️ **Streamlit** – to display everything in a sleek, interactive UI

---

## 🚀 Tech Stack

| Layer             | Framework / Tool            |
|------------------|-----------------------------|
| Web UI           | Streamlit                   |
| ML Similarity    | Cosine Similarity           |
| NLP              | Sentence Transformers       |
| Database         | SQLite / PostgreSQL         |
| Language         | Python                      |

---

## 🛠️ Installation & Setup

## bash
# Clone the repository
git clone https://github.com/yourusername/product-recommender-system.git
cd product-recommender-system

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
