import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import re

# Load your filtered dataset
DATASET_PATH = "D:\\GK\\Keesa\\SMS-Parser\\data\\SMS-Banking-Transactions_Filtered12 - SMS-Banking-Transactions_Filtered12.csv"
df = pd.read_csv(DATASET_PATH)
df = df.dropna(subset=['Message', 'Category'])

# Prepare vectorizer input
messages = df['Message'].astype(str).tolist()

# Recreate vectorizer
vectorizer = TfidfVectorizer(max_features=500)
vectorizer.fit(messages)

# Save path
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")
with open(VECTORIZER_PATH, 'wb') as f:
    pickle.dump(vectorizer, f)

print("✅ Vectorizer saved to", VECTORIZER_PATH)
