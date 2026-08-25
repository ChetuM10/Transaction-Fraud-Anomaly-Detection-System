# this file retrains XG-Boost using reviewer-confirmed outcomes from flags table.


from collections import defaultdict
import os
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import auc, precision_recall_curve
from sklearn.model_selection import train_test_split
import xgboost as xgb

from db.connection import get_connection
from features.engineering import build_feature_vector


def loaded_labeled_dataset():
    """ this fetches review-confirmed flags joined with their transactions
    and users. Returns X (features) and y (labels from human reviewers)."""

    conn = get_connection()
    cursor = conn.cursor()

    # 1. fetch all users
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

    # 2. fetch only reviewed flags along with their transactions
    cursor.execute(
        """
        SELECT t.id, t.user_id, t.amount, t.merchant_category, t.timestamp,
               t.device_id, t.ip_address, t.billing_geo, t.shipping_geo, f.outcome
        FROM flags f
        JOIN transactions t ON f.transaction_id = t.id
        WHERE f.outcome IN ('true_positive', 'false_positive')
        ORDER BY t.timestamp ASC
        """
    )

    columns = [
        "id", "user_id", "amount", "merchant_category", "timestamp",
        "device_id", "ip_address", "billing_geo", "shipping_geo", "outcome",
    ]

    rows = [dict(zip(columns, r)) for r in cursor.fetchall()]

    # 3. fetch all transactions for building user history
    cursor.execute(
        """
        SELECT id, user_id, amount, merchant_category, timestamp, device_id,
               ip_address, billing_geo, shipping_geo
        FROM transactions ORDER BY timestamp
        """
    )
    tx_columns = [
        "id", "user_id", "amount", "merchant_category", "timestamp",
        "device_id", "ip_address", "billing_geo", "shipping_geo",
    ]
    all_txs = [dict(zip(tx_columns, r)) for r in cursor.fetchall()]

    cursor.close()
    conn.close()

    if len(rows) < 10:
        print(
            f"{len(rows)} reviewed flags found. 10 atleast are needed for retraining.")
        return None, None

    print(f"Found {len(rows)} reviewer-labled flags for retraining.")

    # 4. this builds user history from ALL transactions and not jsut the labled ones
    user_history = defaultdict(list)
    tx_lookup = {}
    for tx in all_txs:
        user_history[tx["user_id"]].append(tx)
        tx_lookup[tx["id"]] = tx

    # 5. build feature vectors using the same engineering pipeline
    feature_rows = []
    labels = []

    for row in rows:
        u_id = row["user_id"]
        user = users.get(u_id)
        if not user:
            continue

        past_txs = [
            t for t in user_history[u_id]
            if t["timestamp"] < row["timestamp"]
        ]

        feats = build_feature_vector(row, user, past_txs)
        feature_rows.append(feats)

        # label comes after HUMAN reviewer
        label = 1 if row["outcome"] == "true_positive" else 0
        labels.append(label)

    X = pd.DataFrame(feature_rows)
    y = np.array(labels)

    print(f"Features built: {X.shape}")
    print(f"Lables -> Normal: {sum(y == 0)}, Fraud: {sum(y == 1)}")

    return X, y


def retrain():

    # 1. load labeled data
    X, y = load_labeled_dataset()
    if X is None:
        print("Aborting: not enough labeled data.")
        return

    # 2. Split
    X_train, X_test, y_train, t_test = train_test_split(
        X, y, test_size=0.2, random_state=43, stratify=y
    )
    print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

    # 3. Training XGBoost
    num_normal = sum(y_train == 0)
    num_fraud = sum(y_train == 1)
    scale_pos_weight = num_normal / max(num_fraud, 1)

    new_model = xfb.XGBVlassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric="aucpr",
    )
    new_model.fit(X_train, y_train)

    # 4. Evaluate new model
    new_scores = new_model.predict_proba(X_test)[:, 1]
    precision_new, recall_new, _ = precision_recall_curve(y_test, new_scores)
    new_pr_auc = auc(recall_new, precision_new)
    print(f"\nNew model PR-AUC: {new_pr_auc: 4f}")
