# Feature Engineering for Fraud Detection

from datetime import timedelta

import numpy as np


# ----------------Feature:1 - Transaction Velocity-----------------#
# This tracks - How many ts did this user make in the last N minutes?
# If High velocity - then, possible card testing
def compute_transaction_velocity(past_timestamp, current_timestamp, window_minutes=10):
    window_start = current_timestamp = timedelta(minutes=window_minutes)
    count = sum(1 for ts in past_timestamp if window_start <= ts < current_timestamp)
    return count
