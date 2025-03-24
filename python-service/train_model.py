import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import pickle
import os
import faiss
import re

# ✅ Paths to Save Model, Vectorizers, and Label Encoder
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder.pkl")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss.index")
MERCHANT_FILE = os.path.join(os.path.dirname(__file__), "/Users/vishn/Desktop/SMS-Parser/data/merchant.csv")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "/Users/vishn/Desktop/SMS-Parser/data/synthetic_sms_data.csv")

# ✅ Load Dataset
df = pd.read_csv(DATASET_PATH)
print(f"📥 Loaded dataset with {df.shape[0]} rows.")

# ✅ Fix Missing Values
df = df.dropna(subset=['Message', 'Category'])

# ✅ Normalize Transaction Types
category_map = {
    'upi transaction': 'credit',
    'balance update': 'balance_update',
    'credit': 'credit',
    'debit': 'debit',
    'refund': 'refund',
    'failed transaction': 'failed',
    'fraud': 'fraud'
}
df['Category'] = df['Category'].str.lower().map(category_map)

# ✅ Remove unmapped categories
df = df[df['Category'].notna()]
print(f"✅ Cleaned categories: {df['Category'].unique()}")

# ✅ Extract Amount
def extract_amount(message):
    match = re.search(r'(?i)(?:rs\.?|inr\.?|₹)?\s*([\d,]+\.\d{2})', str(message))
    if match:
        return float(match.group(1).replace(',', ''))
    return None

df['Amount'] = df['Message'].apply(extract_amount)

# ✅ Fraud Detection
fraud_keywords = [
    'OTP', 'suspicious', 'unauthorized', 'blocked', 'fraud',
    'risk', 'unauthenticated', 'transaction blocked', 'hacked'
]

def detect_fraud(message):
    for keyword in fraud_keywords:
        if keyword.lower() in message.lower():
            return 'fraud'
    return None

df['Fraud_Flag'] = df['Message'].apply(detect_fraud)
df.loc[df['Fraud_Flag'] == 'fraud', 'Category'] = 'fraud'

# ✅ Load Merchant Data
merchant_df = pd.read_csv(MERCHANT_FILE)
merchant_names = merchant_df['merchant_name'].str.lower().tolist()

# ✅ Remove Empty Merchant Names
merchant_names = [name for name in merchant_names if name and isinstance(name, str)]

# ✅ Create Merchant Embeddings with FAISS
vectorizer = TfidfVectorizer(max_features=500)
merchant_embeddings = vectorizer.fit_transform(merchant_names).toarray()

# ✅ Normalize Embeddings
norms = np.linalg.norm(merchant_embeddings, axis=1)
merchant_embeddings = merchant_embeddings / norms[:, np.newaxis]

# ✅ Create FAISS Index
index = faiss.IndexFlatIP(merchant_embeddings.shape[1])
index.add(np.array(merchant_embeddings).astype('float32'))
faiss.write_index(index, INDEX_PATH)

# ✅ Fallback Merchant Matching
def find_closest_merchant(message):
    if not message:
        return "Unknown"
    vector = vectorizer.transform([message]).toarray().astype('float32')
    distances, indices = index.search(vector, 1)
    similarity_score = distances[0][0]
    if similarity_score > 0.3:
        return merchant_names[indices[0][0]]
    else:
        return "Unknown"

df['Merchant'] = df['Message'].apply(find_closest_merchant)

# ✅ Extract Reference Number
df['ReferenceNumber'] = df['Message'].str.extract(r'(?:ref|txn\s*id)?\s*([\w\d]+)')

# ✅ Extract Date
def extract_date(message):
    match = re.search(r'(\d{2}/\d{2}/\d{4})|(\d{2}-[A-Za-z]+-\d{2,4})', str(message))
    if match:
        date_str = match.group(0)
        if '/' in date_str:
            day, month, year = date_str.split('/')
        else:
            day, month_str, year = date_str.split('-')
            month = str((pd.to_datetime(month_str + " 1", format="%b %d").month)).zfill(2)
        
        year = f"20{year}" if len(year) == 2 else year
        return f"{day.zfill(2)}-{month.zfill(2)}-{year}"
    return None

df['Date'] = df['Message'].apply(extract_date)

# ✅ Remove Empty Rows Before Vectorizing
df = df.dropna(subset=['Message'])
print(f"✅ Cleaned dataset size: {df.shape}")

# ✅ Vectorize SMS Data Using TF-IDF
message_vectorizer = TfidfVectorizer(max_features=500)
X = message_vectorizer.fit_transform(df['Message']).toarray()

# ✅ Save Message Vectorizer
with open(VECTORIZER_PATH, 'wb') as f:
    pickle.dump(message_vectorizer, f)

# ✅ Encode Labels
le = LabelEncoder()
y = le.fit_transform(df['Category'])

# ✅ Save Label Encoder
with open(LABEL_ENCODER_PATH, 'wb') as f:
    pickle.dump(le, f)

# ✅ Handle Class Imbalance Using SMOTE
if len(np.unique(y)) > 1:
    print(f"✅ Found {len(np.unique(y))} unique classes — Applying SMOTE...")
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)
else:
    print("⚠️ Only one class found — Skipping SMOTE")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Train LightGBM Model
model = lgb.LGBMClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    num_leaves=15,
    min_data_in_leaf=50,
    subsample=0.8,
    class_weight='balanced',
    objective='multiclass',
    force_row_wise=True,
    #colsample_bytree=0.8,
    random_state=42
)

print("🚀 Training LightGBM Model...")
model.fit(X_train, y_train)

# ✅ Save Model
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)

print("✅ LightGBM Model Trained and Saved!")
