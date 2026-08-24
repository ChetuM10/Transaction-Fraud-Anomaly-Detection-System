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
        "SELECT id, avg_tansaction_amount, home_geo, known_devices FROM users"
    )
    users = {}
    for row in cursor.fetchall():
        users[row[0]] = {
            "id": row[0],
            "avg_tansaction_amount": float(row[1]),
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
