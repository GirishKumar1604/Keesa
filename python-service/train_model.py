import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os
import re

# ✅ File paths
DATASET_PATH = "D:\\GK\\Keesa\\SMS-Parser\\data\\SMS-Banking-Transactions_Filtered12 - SMS-Banking-Transactions_Filtered12.csv"
MODEL_PATH = "model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"

# ✅ Load Dataset
df = pd.read_csv(DATASET_PATH)
df = df.dropna(subset=['Message', 'Category'])

# ✅ Normalize Categories
category_map = {
    'UPI Transaction': 'credit',
    'Balance Update': 'balance_update',
    'Credit': 'credit',
    'Debit': 'debit',
    'Refund': 'refund',
    'Failed Transaction': 'failed',
    'Fraud': 'fraud'
}
df['Category'] = df['Category'].map(category_map)

# ✅ Amount extraction
def extract_amount(msg):
    match = re.search(r'(?i)(?:rs\.?|inr\.?|₹)?\s*([\d,]+\.\d{2})', msg)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

df['Amount'] = df['Message'].apply(extract_amount)

# ✅ Add fraud detection flag
fraud_keywords = ['OTP', 'suspicious', 'unauthorized', 'blocked', 'fraud', 'risk', 'unauthenticated', 'hacked']
def detect_fraud(msg):
    return 'fraud' if any(k.lower() in msg.lower() for k in fraud_keywords) else None

df['Fraud_Flag'] = df['Message'].apply(detect_fraud)
df.loc[df['Fraud_Flag'] == 'fraud', 'Category'] = 'fraud'

# ✅ Balance the data
max_samples = df['Category'].value_counts().max()
balanced_df = pd.concat([
    df[df['Category'] == cat].sample(max_samples, replace=True)
    for cat in df['Category'].dropna().unique()
])

# ✅ TF-IDF Vectorization
vectorizer = TfidfVectorizer(max_features=500)
X = vectorizer.fit_transform(balanced_df['Message']).toarray()
y = balanced_df['Category']

# ✅ Encode y
y_encoded, label_mapping = pd.factorize(y)
print("💡 Label Mapping:", dict(enumerate(label_mapping)))

# ✅ Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# ✅ Train XGBoost model
model = xgb.XGBClassifier(
    objective='multi:softmax',
    num_class=len(label_mapping),
    eval_metric='mlogloss',
    use_label_encoder=False,
    random_state=42
)
model.fit(X_train, y_train)

# ✅ Evaluate
y_pred = model.predict(X_test)
print("📊 Classification Report:\n", classification_report(y_test, y_pred, target_names=label_mapping))

# ✅ Save model and vectorizer
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)

with open(VECTORIZER_PATH, 'wb') as f:
    pickle.dump(vectorizer, f)

print("✅ Model & vectorizer saved.")
