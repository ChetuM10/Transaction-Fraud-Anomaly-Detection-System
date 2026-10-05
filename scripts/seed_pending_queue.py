"""
Seeds the Reviewer Queue with fresh, unreviewed pending flags by scoring
10-15 realistic transactions via POST /score against the live or local API.
"""

import os
import sys
import uuid
import random
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.connection import get_connection

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
NUM_FLAGS = 12

MERCHANT_CATEGORIES = [
    "groceries",
    "electronics",
    "travel",
    "dining",
    "clothing",
    "entertainment",
    "utilities",
]

CITIES = [
    "Mumbai,IN", "Delhi,IN", "Bengaluru,IN", "Hyderabad,IN",
    "Chennai,IN", "Kolkata,IN", "Pune,IN", "Ahmedabad,IN",
    "New York,US", "London,GB", "Singapore,SG", "Dubai,AE",
]


def fetch_sample_users(limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, home_geo, known_devices, avg_transaction_amount
        FROM users
        ORDER BY RANDOM()
        LIMIT %s
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    users = []
    for r in rows:
        users.append({
            "id": r[0],
            "home_geo": r[1],
            "known_devices": r[2] if r[2] else ["dev_default"],
            "avg_transaction_amount": float(r[3]) if r[3] else 100.0,
        })
    return users


def score_fresh_transactions(api_url=API_URL, count=NUM_FLAGS):
    users = fetch_sample_users()
    if not users:
        print("No users found in database. Run generate_data.py first.")
        return []

    print(f"Scoring {count} fresh transactions via {api_url}/score...")
    now = datetime.now(timezone.utc)
    results = []

    for i in range(count):
        user = random.choice(users)
        tx_id = f"tx_live_{uuid.uuid4().hex[:8]}"

        # Alternate risk profiles so Reviewer Queue has auto_block, review, and auto_approve
        scenario = i % 3
        if scenario == 0:  # High risk -> auto_block
            amount = round(user["avg_transaction_amount"] * random.uniform(8.0, 15.0), 2)
            device_id = f"device_unknown_{random.randint(9000, 9999)}"
            shipping_geo = random.choice([c for c in CITIES if c != user["home_geo"]])
        elif scenario == 1:  # Medium risk -> review
            amount = round(user["avg_transaction_amount"] * random.uniform(2.5, 4.0), 2)
            device_id = random.choice(user["known_devices"])
            shipping_geo = random.choice([c for c in CITIES if c != user["home_geo"]])
        else:  # Normal transaction -> auto_approve
            amount = round(max(10.0, random.gauss(user["avg_transaction_amount"], user["avg_transaction_amount"] * 0.2)), 2)
            device_id = random.choice(user["known_devices"])
            shipping_geo = user["home_geo"]

        tx_time = (now - timedelta(minutes=random.randint(1, 45))).isoformat()

        payload = {
            "id": tx_id,
            "user_id": user["id"],
            "amount": amount,
            "merchant_category": random.choice(MERCHANT_CATEGORIES),
            "timestamp": tx_time,
            "device_id": device_id,
            "ip_address": f"{random.randint(10, 200)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
            "billing_geo": user["home_geo"],
            "shipping_geo": shipping_geo,
        }

        req = urllib.request.Request(
            f"{api_url}/score",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"[{i+1}/{count}] Scored {tx_id}: Decision={data['decision']:12} Score={data['score']:.4f} FlagID={data['flag_id']}")
                results.append(data)
        except urllib.error.HTTPError as e:
            print(f"[{i+1}/{count}] Error scoring {tx_id}: HTTP {e.code} - {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"[{i+1}/{count}] Failed scoring {tx_id}: {e}")

    print(f"\nSuccessfully populated Reviewer Queue with {len(results)} fresh scored transactions.")
    return results


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else API_URL
    score_fresh_transactions(api_url=target_url)
