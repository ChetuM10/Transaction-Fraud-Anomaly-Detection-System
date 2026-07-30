# Generates users and transactions for testing (5% fraud transactions i've added)

import random
import uuid
from datetime import datetime, timedelta, timezone

import numpy as np
from faker import Faker

from db.connection import get_connection

fake = Faker("en_IN")

NUM_USERS = 200
NUM_TRANSACTIONS = 5000
FRAUD_RATIO = 0.05  # means 5% transactions will be fraudulent

CITIES = [
    "Mumbai,IN",
    "Delhi,IN",
    "Bengaluru,IN",
    "Chennai,IN",
    "Hyderabad,IN",
    "Pune,IN",
    "Kolkata,IN",
    "Ahmedabad,IN",
    "Jaipur,IN",
    "Lucknow,IN",
]

MERCHANT_CATEGORIES = [
    "electronics",
    "groceries",
    "fashion",
    "food_delivery",
    "travel",
    "entertainment",
    "healthcare",
    "education",
    "gift_cards",
    "jewelry",
]

DEVICES = [f"device_{i:04}" for i in range(1, 51)]  # 50 possible devices


# User generation
def generate_users(num_users):
    users = []
    for _ in range(num_users):
        user_id = f"u_{uuid.uuid4().hex[:8]}"
        created_days_ago = random.randint(30, 730)  # account age
        created_at = datetime.now(timezone.utc) - timedelta(days=created_days_ago)
        avg_amount = round(random.uniform(200, 15000), 2)  # spend range
        home_geo = random.choice(CITIES)
        num_devices = random.randint(1, 3)
        known_devices = random.sample(DEVICES, num_devices)

        users.append(
            {
                "id": user_id,
                "created_at": created_at,
                "avg_transaction_amount": avg_amount,
                "home_geo": home_geo,
                "known_devices": known_devices,
            }
        )
    return users


# inserting generated users into the db
def insert_users(users):
    conn = get_connection()
    cursor = conn.cursor()
    for u in users:
        cursor.execute(
            """
            INSERT INTO users (id, created_at, avg_transaction_amount, home_geo,
            known_devices)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                u["id"],
                u["created_at"],
                u["avg_transaction_amount"],
                u["home_geo"],
                u["known_devices"],
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {len(users)} users.")
