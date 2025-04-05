import os
import re
import faiss
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

# === Config Paths ===
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss.index")
MERCHANT_FILE = os.path.join(os.path.dirname(__file__), "../data/merchant.csv")

# === Parameters ===
SIMILARITY_THRESHOLD = 0.35
LABEL_MAP = {0: 'credit', 1: 'fraud', 2: 'balance_update', 3: 'refund', 4: 'failed'}

# === App Initialization ===
app = Flask(__name__)

# === Load ML Model ===
print("📥 Loading XGBoost model...")
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("✅ Loaded XGBoost Model!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    model = None

# === Load Vectorizer ===
print("📥 Loading TF-IDF vectorizer...")
try:
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    print("✅ Loaded TF-IDF Vectorizer!")
except Exception as e:
    print(f"❌ Failed to load vectorizer: {e}")
    vectorizer = None

# === Load FAISS Index ===
print("📥 Loading FAISS index...")
try:
    index = faiss.read_index(INDEX_PATH)
    print("✅ Loaded FAISS Index!")
except Exception as e:
    print(f"❌ Failed to load FAISS index: {e}")
    index = faiss.IndexFlatL2(1)  # Dummy fallback

# === Load Merchant Names ===
print("📥 Loading merchants...")
try:
    merchant_df = pd.read_csv(MERCHANT_FILE)
    merchant_names = merchant_df['merchant_name'].str.lower().tolist()
    print(f"✅ Loaded {len(merchant_names)} merchants.")
except Exception as e:
    print(f"❌ Failed to load merchant names: {e}")
    merchant_names = []

# === Utility Functions ===

def extract_amount(message):
    match = re.search(r'(?i)(?:rs\.?|inr\.?|₹)?\s*([\d,]+\.\d{2})', message)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

def clean_text(text):
    if isinstance(text, str):
        return text.strip().lower()
    return str(text)

# === API Endpoint ===

@app.route('/predict', methods=['POST'])
def predict():
    try:
        print("🔧 Step 1: Getting JSON data...")
        data = request.get_json(force=True)
        print(f"📦 Raw Data: {data}")

        sms = data.get("sms", "").strip()
        if not sms:
            print("❌ No SMS provided or empty.")
            return jsonify({"success": False, "error": "No SMS provided"}), 400

        print(f"📩 SMS received: {sms}")

        # Step 2: Vectorization
        print("🔧 Step 2: Vectorizing SMS...")
        input_vector = vectorizer.transform([sms]).toarray()
        print(f"📊 Vector shape: {input_vector.shape}")

        # Step 3: XGBoost Prediction
        print("🔧 Step 3: Running XGBoost prediction...")
        prediction = model.predict(input_vector)[0]
        prediction_label = LABEL_MAP.get(prediction, "unknown")
        print(f"🔮 Prediction: {prediction} → {prediction_label}")

        # Step 4: FAISS Similarity
        print("🔧 Step 4: FAISS similarity search...")
        try:
            if index.ntotal == 0:
                raise ValueError("FAISS index is empty!")

            distances, indices = index.search(input_vector.astype("float32"), 1)
            similarity_score = distances[0][0]

            if similarity_score < SIMILARITY_THRESHOLD:
                print(f"⚠️ Similarity too low ({similarity_score:.4f}) — merchant unknown")
                merchant_match = "Unknown"
            else:
                merchant_match = merchant_names[indices[0][0]]
                print(f"✅ Merchant Match: {merchant_match} (score: {similarity_score:.4f})")
        except Exception as faiss_error:
            print(f"❌ FAISS Error: {faiss_error}")
            merchant_match = "Unknown"

        # Step 5: Extract amount
        print("🔧 Step 5: Extracting amount...")
        amount = extract_amount(sms)
        print(f"💰 Amount: {amount}")

        # Step 6: Final Response
        print("🔧 Step 6: Building response...")
        result = {
            "amount": amount,
            "transactionType": clean_text(prediction_label),
            "merchant": clean_text(merchant_match),
            "referenceNumber": "1234567890"  # Placeholder
        }

        print(f"✅ Final Output: {result}")
        return jsonify({"success": True, "data": result})

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# === Run Flask App ===
if __name__ == "__main__":
    app.run(port=5001, debug=True)
