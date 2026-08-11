import os

import joblib
import numpy as np
import shap

from features.engineering import build_feature_vector

# these define when a certain action should take place
THRESHOLD_AUTO_APPROVE = 0.30
THRESHOLD_AUTO_BLOCK = 0.70

FEATURE_NAMES = [
    "velocity_10min",
    "amount_zscore",
    "is_new_device",
    "is_geo_mismatch",
    "is_odd_hour",
    "hour_deviation",
    "category_diversity_1hr",
]


class FraudScorer:
    """First loads svaed model, then scores transactions"""

    def __init__(self):
        model_path = os.path.join(
            os.path.dirname(__file__), "saved_models", "best_model.joblib"
        )
        self.model = joblib.load(model_path)
        self.explainer = shap.TreeExplainer(self.model)
        print("FraudScorer loaded Successfully.")

    def score(self, transaction, user, past_transactions):

        # first load 7-feature vector
        features = build_feature_vector(transaction, user, past_transactions)
        feature_array = np.array([[features[f] for f in FEATURE_NAMES]])

        # second - get fraud probability (0.0 - 1.0)
        fraud_prob = float(self.model.predict_proba(feature_array)[0, 1])

        # third - apply threshold-based decision
        if fraud_prob < THRESHOLD_AUTO_APPROVE:
            decision = "auto_approve"
        elif fraud_prob > THRESHOLD_AUTO_BLOCK:
            decision = "auto_block"
        else:
            decision = "review"

        # fourth - get SHAP explanation
        top_features = self.explain(feature_array, features)

        return {
            "score": round(fraud_prob, 4),
            "decision": decision,
            "top_features": top_features,
        }

        # -----------------------    S H A P  Implementation   ---------------------------#

    def explain(self, feature_array, features):

        shap_values = self.explainer.shap_values(feature_array)

        explanations = []
        for i, name in enumerate(FEATURE_NAMES):
            explanations.append(
                {
                    "feature": name,
                    "shap_value": round(float(shap_values[0][i]), 4),
                    "actual_value": features[name],
                }
            )

        # sort by highest value first(in descendinG order)
        explanations.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        # Return top 3 most impactful features
        return explanations[:3]


if __name__ == "__main__":
    from db.connection import get_connection

    print("Loading Score...")
    scorer = FraudScorer()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(""" 
        SELECT u.id, u.home_geo, u.known_devices
        FROM users u
        JOIN transactions t ON t.user_id = u.id
        GROUP BY u.id
        HAVING COUNT(t.id) >= 10
        ORDER BY RANDOM()
        LIMIT 1
    """)
    row = cursor.fetchone()
    user = {"id": row[0], "home_geo": row[1], "known_devices": row[2]}

    cursor.execute(
        """ 
        SELECT id, user_id, amount, merchant_category, timestamp, device_id,
                ip_address, billing_geo, shipping_geo
        FROM transactions
        WHERE user_id = %s
        ORDER BY timestamp ASC
    """,
        (user["id"],),
    )

    columns = [
        "id",
        "user_id",
        "amount",
        "merchant_category",
        "timestamp",
        "device_id",
        "ip_address",
        "billing_geo",
        "shipping_geo",
    ]
    txs = [dict(zip(columns, r)) for r in cursor.fetchall()]
    cursor.close()
    conn.close()

    # score the last transaction using all previous ones as history
    last_tx = txs[-1]
    past = txs[:-1]

    print(f"\nScoring Transaction: {last_tx['id']}")
    print(f"    Amount: {last_tx['amount']}")
    print(f"    Device: {last_tx['device_id']}")
    print(f"    Time: {last_tx['timestamp']}")

    result = scorer.score(last_tx, user, past)

    print("\n-------Result-------")
    print(f"    Fraud Score: {result['score']}")
    print(f"    Decision: {result['decision']}")
    print("    Top Reasons:")
    for reason in result["top_features"]:
        print(
            f"    {reason['feature']} {reason['actual_value']} (SHAP: {reason['shap_value']})"
        )
