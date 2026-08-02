# Feature Engineering for Fraud Detection

from datetime import timedelta

import numpy as np


# ----------------Feature:1 - Transaction Velocity-----------------#
# This tracks - How many ts did this user make in the last N minutes?
# If High velocity - then, possible card testing
def compute_transaction_velocity(past_timestamp, current_timestamp, window_minutes=10):
    window_start = current_timestamp - timedelta(minutes=window_minutes)
    count = sum(1 for ts in past_timestamp if window_start <= ts < current_timestamp)
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


# ---------------------Featrue:4 - Time anamoly---------------------------#
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
