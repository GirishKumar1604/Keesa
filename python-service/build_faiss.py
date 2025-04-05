# build_faiss.py
import faiss
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# ✅ File paths
MERCHANT_FILE = os.path.join(os.path.dirname(__file__), "../data/merchant.csv")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss.index")

# ✅ Load merchant names
print("📥 Loading merchants...")
df = pd.read_csv(MERCHANT_FILE)
merchant_names = df['merchant_name'].fillna("").str.lower().tolist()
print(f"✅ Loaded {len(merchant_names)} merchants.")

# ✅ Create TF-IDF embeddings
print("🧠 Generating TF-IDF embeddings...")
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(merchant_names)

# ✅ Convert to dense numpy array
embeddings = X.toarray().astype("float32")

# ✅ Save vectorizer
with open(VECTORIZER_PATH, "wb") as f:
    pickle.dump(vectorizer, f)
print(f"✅ Vectorizer saved to {VECTORIZER_PATH}")

# ✅ Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, INDEX_PATH)
print(f"✅ FAISS index saved to {INDEX_PATH}")
