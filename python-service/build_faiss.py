import faiss
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import pickle

# ✅ File Paths
MERCHANT_FILE = os.path.join(os.path.dirname(__file__), "../data/merchant.csv")
INDEX_FILE = os.path.join(os.path.dirname(__file__), "faiss.index")
VECTOR_FILE = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")
MERCHANT_NAMES_FILE = os.path.join(os.path.dirname(__file__), "merchant_names.pkl")

# ✅ Load Merchant Data
print("📥 Loading merchant data...")
merchant_df = pd.read_csv(MERCHANT_FILE)
merchant_names = merchant_df['merchant_name'].str.lower().tolist()

# ✅ Build Vectorizer with Same Settings as Training
vectorizer = TfidfVectorizer(max_features=768)  # Match training size
X = vectorizer.fit_transform(merchant_names).toarray()

# ✅ Ensure FAISS Index Dimension Matches Vectorizer Output Size
dimension = X.shape[1]
print(f"✅ FAISS index dimension: {dimension}")

# ✅ Create FAISS Index
index = faiss.IndexFlatL2(dimension)
index.add(X.astype('float32'))

# ✅ Save Index and Vectorizer
faiss.write_index(index, INDEX_FILE)
with open(VECTOR_FILE, 'wb') as f:
    pickle.dump(vectorizer, f)
with open(MERCHANT_NAMES_FILE, 'wb') as f:
    pickle.dump(merchant_names, f)

print(f"✅ FAISS Index built with {len(merchant_names)} merchants.")
