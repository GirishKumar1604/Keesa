import faiss
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import pickle
import os
import re

# ✅ Paths to models and index
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss.index")
MERCHANT_NAMES_PATH = os.path.join(os.path.dirname(__file__), "merchant_names.pkl")
SIMILARITY_THRESHOLD = 0.35

# ✅ Flask app setup
app = Flask(__name__)

# ✅ Load ML Model
print("📥 Loading ML Model...")
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# ✅ Load Vectorizer
print("📥 Loading Vectorizer...")
with open(VECTORIZER_PATH, 'rb') as f:
    vectorizer = pickle.load(f)

# ✅ Load FAISS Index
print("📥 Loading FAISS Index...")
index = faiss.read_index(INDEX_PATH)

# ✅ Load Merchant Names
print("📥 Loading Merchant Names...")
with open(MERCHANT_NAMES_PATH, 'rb') as f:
    merchant_names = pickle.load(f)

# ✅ Fix for Extracting Transaction Amount
def extract_amount(message):
    match = re.search(r'(?i)(?:rs\.?|inr\.?|₹)?\s*([\d,]+\.\d{2})', message)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

# ✅ Fix for Input Vector Shape Mismatch
def validate_input_vector(input_vector):
    if input_vector.shape[1] != index.d:
        raise ValueError(f"Vector shape mismatch: Expected {index.d}, got {input_vector.shape[1]}")
    return input_vector.astype('float32')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        sms = request.json.get('sms')
        if not sms:
            return jsonify({"success": False, "error": "No SMS provided"}), 400
        
        print(f"📩 Incoming SMS: {sms}")

        # ✅ Vectorize Input SMS
        input_vector = vectorizer.transform([sms]).toarray()
        input_vector = pd.DataFrame(input_vector, columns=vectorizer.get_feature_names_out())

        # ✅ Predict Transaction Type
        prediction = model.predict(input_vector)[0]

        # ✅ FAISS Search for Merchant Match
        distances, indices = index.search(input_vector.to_numpy().astype('float32'), 1)
        similarity_score = distances[0][0]

        # ✅ Fix FAISS Output Index Mismatch
        if similarity_score > SIMILARITY_THRESHOLD:
            merchant_index = indices[0][0]
            print(f"🔍 FAISS Returned Index: {merchant_index}")
            if 0 <= merchant_index < len(merchant_names):
                merchant_match = merchant_names[merchant_index]
            else:
                merchant_match = "Unknown"
            print(f"✅ Merchant Match: {merchant_match} (Score: {similarity_score:.2f})")
        else:
            merchant_match = "Unknown"
            print(f"❌ Similarity too low: {similarity_score:.2f}")

        # ✅ Extract Amount
        amount = extract_amount(sms)

        # ✅ Construct Response
        result = {
            "amount": amount if amount else None,
            "transactionType": int(prediction), 
            "merchant": merchant_match,
            "referenceNumber": "1234567890"
        }

        print(f"✅ Prediction Result: {result}")
        return jsonify({"success": True, "data": result})

    except ValueError as e:
        print(f"❌ Value Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

    except Exception as e:
        print(f"❌ Error in prediction: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ✅ Run Flask App
if __name__ == '__main__':
    app.run(port=5001, debug=True)
