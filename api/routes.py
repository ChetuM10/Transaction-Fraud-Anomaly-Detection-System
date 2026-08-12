from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db.connection import get_connection
from models.scorer import FraudScorer

app = FastAPI(
    title="Fraud Detection API",
    description="Scrores transactions against user behavioral baselines.",
    version="0.1.0",
)

scorer = FraudScorer()

#------------ REQUEST / RESPONSE Models ------------#
class TransactionIn(BaseModel):

    id: str
    user_id: str
    amount: float
    merchant_category: str
    timestamp: str
    device_id: str
    ip_address: str
    billing_geo: str
    shipping_geo: str

class FeatureExplanation(BaseModel):
    feature: str
    shap_value: str
    actual_value: str

class ScoreResponse(BaseModel):
    transaction_id: str
    score: float
    decision: str
    top_features: list[FeatureExplanation]

#--------- Database Helpers ---------#
def fetch_user(user_id: str):
    ''' Looks up user's profile from DB '''

    conn = get_connection()
    cursor = conn.cursor()
    curesor.execute(
        "SELECT is, home_geo, know_devices FROM users WHERE id = %s",
        (user_id),
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None
    
    return {"id": row[0], "home_geo": row[1], "known_devices": row[2]}

def fetch_transactions(user_id: str):
    ''' Gets user's transaction history, ordered by time '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, amount, merchant_category, timestamp,
        device_id, ip_address, billing_geo, shipping_geo
        FROM transactions
        WHERE user_id = %s
        ORDER BY timestamp ASC
        """,
        (user_id),
    )

    columns = [
        "id", "user_id", "amount", "merchant_category", "timestamp",
        "device_id", "ip_address", "billing_geo", "shipping_geo",
    ]

    rows = [dict(zip(columns, r)) for r in cursore.fetchall()]
    cursoe.close()
    conn.close()
    return rows