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
        device_id, ip_address, billing_geo, shipping_geo
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
    ]
    raw_txs = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    print(f"Loaded {len(users)} users and {len(raw_txs)} transactions from PostgreSQL.")

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

        # determines truth label (1=fraud, 0=normal) based on set rules
        amount = float(tx["amount"])
        user_avg = user["avg_transaction_amount"]
        is_new_device = 1 if tx["device_id"] not in user["known_devices"] else 0
        is_geo_mismatch = 1 if tx["shipping_geo"] != user["home_geo"] else 0
        is_odd_hour = 1 if 2 <= tx["timestamp"].hour <= 4 else 0

        is_fraud = 0
        if (
            amount >= 4.5 * user_avg
            or (is_new_device == 1 and is_geo_mismatch == 1)
            or (is_odd_hour == 1 and amount >= 2.5 * user_avg)
        ):
            is_fraud = 1

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
