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


# ----------------User generation---------------------#
def generate_users(num_users):
    users = []
    for _ in range(num_users):
        user_id = f"u_{uuid.uuid4().hex[:8]}"
        created_days_ago = random.randint(30, 730)  # account age
        created_at = datetime.now(timezone.utc) - \
            timedelta(days=created_days_ago)
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


# ----------------------------Transaction Generation-------------------------#
def generate_transactions(users, num_transactions, fraud_ratio):
    transactions = []
    num_fraud = int(num_transactions * fraud_ratio)
    num_normal = num_transactions - num_fraud

    # Which transaction will be fradulent?
    is_fraud_list = [True] * num_fraud + [False] * num_normal
    random.shuffle(is_fraud_list)

    now = datetime.now(timezone.utc)

    for i in range(num_transactions):
        user = random.choice(users)
        is_fraud = is_fraud_list[i]

        tx_id = f"t_{uuid.uuid4().hex[:8]}"

        # Random timestamp within the last month(30 days)
        days_ago = random.uniform(0, 30)
        tx_time = now - timedelta(days=days_ago)

        if not is_fraud:
            # Normal Transaction
            amount = round(
                max(
                    10.0,
                    np.random.normal(
                        user["avg_transaction_amount"],
                        user["avg_transaction_amount"] * 0.2,
                    ),
                ),
                2,
            )
            device_id = random.choice(user["known_devices"])
            billing_geo = user["home_geo"]
            shipping_geo = user["home_geo"]
            merchant = random.choice(MERCHANT_CATEGORIES)
        else:
            # Fradulent transaction
            fraud_type = random.choice(
                ["amount_spike", "device_location_mismatch", "odd_hours"]
            )

            if fraud_type == "amount_spike":
                # say 5 - 12 times higher than user spending baseline
                amount = round(
                    user["avg_transaction_amount"] *
                    random.uniform(5.0, 12.0), 2
                )
                device_id = random.choice(user["known_devices"])
                billing_geo = user["home_geo"]
                shipping_geo = user["home_geo"]
            elif fraud_type == "device_location_mismatch":
                # Normal amount but, different device + different country/city
                amount = round(random.uniform(500, 5000), 2)
                # unkown device
                device_id = f"device_{random.randint(9000, 9999)}"
                billing_geo = user["home_geo"]
                shipping_geo = random.choice(
                    [c for c in CITIES if c != user["home_geo"]]
                )
            else:
                # Odd hours transactions (2 AM - 4 AM)
                amount = round(
                    user["avg_transaction_amount"] *
                    random.uniform(3.0, 7.0), 2
                )
                device_id = random.choice(user["known_devices"])
                billing_geo = user["home_geo"]
                shipping_geo = user["home_geo"]

                # Foreceful timestamp hour to early morning(2 - 4). Doesn't occur in actual real life systems
                # this is just to show a few examples about unsual timing transactions.
                tx_time = tx_time.replace(
                    hour=random.randint(2, 4), minute=random.randint(0, 59)
                )

            merchant = random.choice(MERCHANT_CATEGORIES)

        # Random IP format
        ip_address = fake.ipv4()

        transactions.append(
            {
                "id": tx_id,
                "user_id": user["id"],
                "amount": amount,
                "merchant_category": merchant,
                "timestamp": tx_time,
                "device_id": device_id,
                "ip_address": ip_address,
                "billing_geo": billing_geo,
                "shipping_geo": shipping_geo,
                "is_fraud": 1 if is_fraud else 0,
            }
        )
    return transactions


def insert_transactions(transactions):
    # this inserts transactions that are generated into PostgreSQL
    conn = get_connection()
    cursor = conn.cursor()
    for t in transactions:
        cursor.execute(
            """
            INSERT INTO transactions (
            id, user_id, amount, merchant_category, timestamp, device_id, ip_address, billing_geo, shipping_geo, is_fraud
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                t["id"],
                t["user_id"],
                t["amount"],
                t["merchant_category"],
                t["timestamp"],
                t["device_id"],
                t["ip_address"],
                t["billing_geo"],
                t["shipping_geo"],
                t["is_fraud"],
            ),
        )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {len(transactions)} transactions.")


if __name__ == "__main__":
    print("Starting data generation...")
    users = generate_users(NUM_USERS)
    insert_users(users)

    transactions = generate_transactions(users, NUM_TRANSACTIONS, FRAUD_RATIO)
    insert_transactions(transactions)
    print("Data generation complete!")
