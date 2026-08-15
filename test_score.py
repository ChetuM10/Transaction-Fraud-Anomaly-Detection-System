from models.scorer import FraudScorer, FEATURE_NAMES
from features.engineering import build_feature_vector
from api.routes import fetch_user, fetch_past_transactions
from datetime import datetime
import numpy as np

# ---------------- TRANSACTION ----------------
scorer = FraudScorer()

transaction = {

    "id": "tx_score_30",
    "user_id": "u_b35dd205",
    "amount": 11000.00,                      # Normal amount
    "merchant_category": "groceries",
    "timestamp": datetime.fromisoformat("2025-08-12T14:30:00"),
    "device_id": "device_unknown_9999",      # 🚩 New device
    "ip_address": "192.168.1.1",
    "billing_geo": "Pune,IN",
    "shipping_geo": "Pune,IN",

}

# ---------------- GET USER DATA ----------------

user = fetch_user(transaction["user_id"])

if not user:
    print("User not found")
    exit()

past_transactions = fetch_past_transactions(transaction["user_id"])

# ---------------- BUILD FEATURES ----------------

features = build_feature_vector(
    transaction,
    user,
    past_transactions
)

print("\n========== FEATURES ==========")

for name in FEATURE_NAMES:
    print(f"{name:35} : {features[name]}")

# ---------------- MODEL INPUT ----------------

feature_array = np.array([
    [features[name] for name in FEATURE_NAMES]
])

# ---------------- FRAUD SCORE ----------------

fraud_probability = float(
    scorer.model.predict_proba(feature_array)[0, 1]
)

print("\n========== MODEL RESULT ==========")
print("Fraud probability:", fraud_probability)

# ---------------- DECISION ----------------

if fraud_probability < 0.30:
    decision = "auto_approve"
elif fraud_probability > 0.80:
    decision = "auto_block"
else:
    decision = "review"

print("Decision:", decision)

# ---------------- SHAP EXPLANATION ----------------

shap_values = scorer.explainer.shap_values(feature_array)

print("\n========== SHAP EXPLANATION ==========")

explanations = []

for i, name in enumerate(FEATURE_NAMES):
    value = float(shap_values[0][i])

    explanations.append(
        (name, value, features[name])
    )

explanations.sort(
    key=lambda x: abs(x[1]),
    reverse=True
)

for name, shap_value, actual_value in explanations:
    print(
        f"{name:35} "
        f"SHAP={shap_value:+.4f} "
        f"actual={actual_value}"
    )
