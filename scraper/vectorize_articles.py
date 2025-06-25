import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import openai  # or your preferred LLM API

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
ARTICLES_FILE = os.path.join(DATA_DIR, 'articles.json')
VECTORS_FILE = os.path.join(DATA_DIR, 'article_vectors.npz')
METADATA_FILE = os.path.join(DATA_DIR, 'article_metadata.json')

MODEL_NAME = 'all-MiniLM-L6-v2'

def load_articles():
    with open(ARTICLES_FILE, 'r') as f:
        return json.load(f)

def vectorize_articles(articles):
    model = SentenceTransformer(MODEL_NAME)
    texts = [a['title'] for a in articles]
    vectors = model.encode(texts, show_progress_bar=True)
    return vectors

def save_vectors(vectors, articles):
    np.savez(VECTORS_FILE, vectors=vectors)
    with open(METADATA_FILE, 'w') as f:
        json.dump(articles, f, indent=2)

def generate_rag_response(user_query, retrieved_articles):
    # Combine user query and top article snippets
    context = "\n\n".join([f"{a['title']}: {a.get('summary', '')}" for a, _ in retrieved_articles])
    prompt = f"User question: {user_query}\n\nRelevant information:\n{context}\n\nAnswer the user's question using the information above."
    
    # Call your LLM (example with OpenAI)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def main():
    articles = load_articles()
    vectors = vectorize_articles(articles)
    save_vectors(vectors, articles)
    print(f"Saved {len(vectors)} vectors to {VECTORS_FILE} and metadata to {METADATA_FILE}")

if __name__ == '__main__':
    main() 