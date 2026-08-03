"""This is to verify the feature engineering functions against the DB."""

from db.connection import get_connection
from features.engineering import build_feature_vector


def fetch_user_with_transactions():
    conn = get_connection()
    cursor = conn.cursor()

    # Find a user with enough transaction history
    cursor.execute(""" 
    SELECT u.id, u.home_geo, u.known_devices
    FROM users u
    JOIN transactions t ON t.user_id = u.id
    GROUP BY u.id
    HAVING COUNT(t.id) >= 10
    ORDER BY RANDOM()
    LIMIT 1
    """)
    user_row = cursor.fetchone()

    if not user_row:
        print("No user with enough transactions found. Run generate_data.py first.")
        cursor.close()
        conn.close()
        return None, None

    user = {
        "id": user_row[0],
        "home_geo": user_row[1],
        "known_devices": user_row[2],
    }

    # get this user's transactions sorted by time
    cursor.execute(
        """ 
    SELECT id, user_id, amount, merchant_category, timestamp, device_id,
    ip_address, billing_geo, shipping_geo
    FROM transactions
    WHERE user_id = %s
    ORDER BY timestamp ASC
    """,
        (user["id"],),
    )

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
    transactions = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return user, transactions


def main():
    print("Fetching a sample user and theire transactions...\n")
    user, transactions = fetch_user_with_transactions()

    if not user:
        return

    print(f"User: {user['id']}")
    print(f"Home: {user['home_geo']}")
    print(f"Devices: {user['known_devices']}")
    print(f"Total transaction: {len(transactions)}")
    print("_" * 60)

    # Test features on the last 5 transactions
    test_indices = [-5, -4, -3, -2, -1]

    for idx in test_indices:
        tx = transactions[idx]
        past = transactions[: len(transactions) + idx]

        features = build_feature_vector(tx, user, past)
        print(f"\nTransaction: {tx['id']}")
        print(f"  Amount: {tx['amount']}")
        print(f"  Device: {tx['device_id']}")
        print(f"  Shipping: {tx['shipping_geo']}")
        print(f"  Time: {tx['timestamp']}")
        print(f"  Category: {tx['merchant_category']}")
        print("  Features:")

        for name, value in features.items():
            print(f" {name}: {value}")
        print("_" * 60)


if __name__ == "__main__":
    main()
