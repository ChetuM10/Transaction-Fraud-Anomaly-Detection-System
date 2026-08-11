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
        elif fraud_prob > THRESHOLD_AUTO_APPROVE:
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
