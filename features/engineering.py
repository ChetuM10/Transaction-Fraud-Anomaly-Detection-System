# Feature Engineering for Fraud Detection

from datetime import timedelta

import numpy as np


# ----------------Feature:1 - Transaction Velocity-----------------#
# This tracks - How many txs did this user make in the last N minutes?
# If High velocity - then, possible card testing
def compute_transaction_velocity(past_timestamp, current_timestamp, window_minutes=10):
    window_start = current_timestamp - timedelta(minutes=window_minutes)
    count = sum(1 for ts in past_timestamp if window_start <=
                ts < current_timestamp)
    return count


# ---------------Feature:2 - Amount Deviation----------------#
""" How many std deviations is this amt from the user's avg?
    
    Ex: user avg = 2000, std = 500, current = 10000
    z-score = (current - mean)/std
    z-score = (10000 - 2000)/500 = 16.0
    16.0 -> Is suspicious
"""


def compute_amount_deviation(current_amount, past_amounts):
    if len(past_amounts) < 2:
        return 0.0

    mean = np.mean(past_amounts)
    std = np.std(past_amounts)

    if std == 0:
        return 0.0 if current_amount == mean else 5.0

    return round(float((current_amount - mean) / std), 4)


# ---------------------Feature:3 - Geo / Device Mismatch----------------#
def compute_geo_device_mismatch(device_id, shipping_geo, known_devices, home_geo):
    """
    Device new? Shipping address difference?
    Maps Device change and Address mismatch
    """
    is_new_device = 0 if device_id in known_devices else 1
    is_geo_mismatch = 0 if shipping_geo == home_geo else 1
    return is_new_device, is_geo_mismatch


# ---------------------Featrue:4 - Time anomaly---------------------------#
def compute_time_anomaly(tx_hour, past_hours):

    is_odd_hour = 1 if 0 <= tx_hour <= 5 else 0

    if len(past_hours) < 2:
        return is_odd_hour, 0.0

    mean_hour = np.mean(past_hours)
    std_hour = np.std(past_hours)

    if std_hour == 0:
        hour_deviation = float(abs(tx_hour - mean_hour))
    else:
        hour_deviation = round(float(abs(tx_hour - mean_hour) / std_hour), 4)

    return is_odd_hour, hour_deviation


# ---------------------Feature:5 - Category Diff-----------------------------#
def compute_category_diversity(recent_categories):
    """
    How many diff merchant categories did this user hit in the last hour?
    """
    if not recent_categories:
        return 0
    return len(set(recent_categories))


# ---------------------Feature:6 - Combined Feature Vector--------------------#
def build_feature_vector(transaction, user, past_transactions):
    """
    Combines all 5 categories into one dictionary for a single transaction.
    Args:
        transaction: dict with amount, timestamp, device_id, shipping_geo,
            merchant_category
        user: dict with home_geo, known_devices
        past_transactions: list of this user's transaction BEFORE this one
    Returns:
    dict of feature_name -> numerical value

    """

    # Extract lists from past transactions
    past_timestamps = [t["timestamp"] for t in past_transactions]
    past_amounts = [float(t["amount"]) for t in past_transactions]
    past_hours = [t["timestamp"].hour for t in past_transactions]

    # Recent Categories
    one_hour_ago = transaction["timestamp"] - timedelta(hours=1)
    recent_categories = [
        t["merchant_category"]
        for t in past_transactions
        if t["timestamp"] >= one_hour_ago
    ]

    # compute all features
    velocity = compute_transaction_velocity(
        past_timestamps, transaction["timestamp"])

    amount_deviation = compute_amount_deviation(
        float(transaction["amount"]), past_amounts
    )

    is_new_device, is_geo_mismatch = compute_geo_device_mismatch(
        transaction["device_id"],
        transaction["shipping_geo"],
        user["known_devices"],
        user["home_geo"],
    )

    is_odd_hour, hour_deviation = compute_time_anomaly(
        transaction["timestamp"].hour, past_hours
    )

    category_diversity = compute_category_diversity(recent_categories)

    return {
        "velocity_10min": velocity,
        "amount_zscore": amount_deviation,
        "is_new_device": is_new_device,
        "is_geo_mismatch": is_geo_mismatch,
        "is_odd_hour": is_odd_hour,
        "hour_deviation": hour_deviation,
        "category_diversity_1hr": category_diversity,
    }
