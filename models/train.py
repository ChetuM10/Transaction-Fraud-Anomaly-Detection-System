"""
Trains Isolation Forest and XGBoost, compares PR-AUC and saves the best model.
How to run: python -m models.train
"""

import os
from collections import defaultdict
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_recall_curve, auc
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
