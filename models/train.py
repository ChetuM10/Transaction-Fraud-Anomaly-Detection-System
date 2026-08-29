"""
Trains Isolation Forest and XGBoost, compares PR-AUC and saves the best model.
How to run: python -m models.train
"""

from collections import defaultdict
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import auc, precision_recall_curve
from sklearn.model_selection import train_test_split
import xgboost as xgb

from db.connection import get_connection
from features.engineering import build_feature_vector


def load_dataset_from_db():
    """Fetches all users and transaction,
    creates X (features) and y (labels)."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1 Fetch all users into a dictionary for quick lookup
    cursor.execute(
        "SELECT id, avg_transaction_amount, home_geo, known_devices FROM users"
    )
    users = {}
    for row in cursor.fetchall():
        users[row[0]] = {
            "id": row[0],
            "avg_transaction_amount": float(row[1]),
            "home_geo": row[2],
            "known_devices": row[3],
        }

    # 2. Fetch all transactions ordered by timestamp
    cursor.execute(""" 
        SELECT id, user_id, amount, merchant_category, timestamp,
        device_id, ip_address, billing_geo, shipping_geo, is_fraud
        FROM transactions
        ORDER BY timestamp ASC    
    """)
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
        "is_fraud"
    ]
    raw_txs = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    print(
        f"Loaded {len(users)} users and {len(raw_txs)} transactions from PostgreSQL.")

    # -------------------------------------------------------------------------#
    # 3. Group transactions by user to build past history sequentially
    user_history = defaultdict(list)
    feature_rows = []
    labels = []

    for tx in raw_txs:
        u_id = tx["user_id"]
        user = users[u_id]
        past_txs = user_history[u_id]

        # this logic computes the 7 feature seignals for this transaction using past history
        feats = build_feature_vector(tx, user, past_txs)
        feature_rows.append(feats)

        # determine truth label directly from ground truth database
        is_fraud = tx["is_fraud"]

        labels.append(is_fraud)

        # add the current transaction to user's history
        user_history[u_id].append(tx)

    X = pd.DataFrame(feature_rows)
    y = np.array(labels)

    print(f"Feature extraction of 'X' complete: shape {X.shape}")
    print(
        f"Fraud ratio -> Normal: {sum(y == 0)}, Fraud: {sum(y == 1)} ({round(np.mean(y) * 100, 2)}% fraud)"
    )

    return X, y


def train_and_evaluate():
    """Trains both, compares by PR-AUC, saves the best model"""

    # 1 Load Dataset
    X, y = load_dataset_from_db()

    # 2 Spplit into 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nTrain set: {len(X_train)} rows | Test set: {len(X_test)} rows.")
    results = {}

    # ----------------------Isolation Forest--------------------------#
    print("\n---------Training Isolation Forest---------")
    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
    )
    iso_forest.fit(X_train)

    # converting to scores
    # keep this in review - maybe needs change
    # higher = more suspicious
    iso_scores = -iso_forest.decision_function(X_test)

    # PR-AUC
    precision_iso, recall_iso, _ = precision_recall_curve(y_test, iso_scores)
    pr_auc_iso = auc(recall_iso, precision_iso)
    results["isolation_forest"] = {
        "model": iso_forest,
        "pr_auc": pr_auc_iso,
    }
    print(f"Isolation Forest PR-AUC: {pr_auc_iso: .4f}")

    # ---------------------------------------------------------------------- #
    print("\n--------- Training XGBoost ---------")

    # Count normal and fraud transactions
    num_normal = sum(y_train == 0)
    num_fraud = sum(y_train == 1)

    # Give more importance to fraud since it is less common
    scale_pos_weight = num_normal / max(num_fraud, 1)

    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="aucpr",
    )

    # Train the model
    xgb_model.fit(X_train, y_train)

    # Get fraud probability for each test transaction
    xgb_scores = xgb_model.predict_proba(X_test)[:, 1]

    # Compute PR-AUC
    precision_xgb, recall_xgb, _ = precision_recall_curve(y_test, xgb_scores)
    pr_auc_xgb = auc(recall_xgb, precision_xgb)
    results["xgboost"] = {
        "model": xgb_model,
        "pr_auc": pr_auc_xgb,
    }
    print(f"XGBoost PR-AUC: {pr_auc_xgb:.4f}")

    # ──────────── Compare & Save Best Model ────────────
    print("\n--------- Comparison ---------")
    print(f"  Isolation Forest PR-AUC: {pr_auc_iso:.4f}")
    print(f"  XGBoost PR-AUC:          {pr_auc_xgb:.4f}")

    best_name = max(results, key=lambda k: results[k]["pr_auc"])
    best_model = results[best_name]["model"]
    best_score = results[best_name]["pr_auc"]

    print(f"\nWinner: {best_name} (PR-AUC: {best_score:.4f})")

    # Save the winning model to disk
    save_dir = os.path.join(os.path.dirname(__file__), "saved_models")
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, "best_model.joblib")
    joblib.dump(best_model, model_path)
    print(f"Model saved to: {model_path}")

    return results


if __name__ == "__main__":
    train_and_evaluate()
