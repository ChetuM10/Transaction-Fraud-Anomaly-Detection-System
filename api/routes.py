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

# ------------ REQUEST / RESPONSE Models ------------#


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
    shap_value: float
    actual_value: float


class ScoreResponse(BaseModel):
    transaction_id: str
    score: float
    decision: str
    top_features: list[FeatureExplanation]

# --------- Database Helpers ---------#


def fetch_user(user_id: str):
    ''' Looks up user's profile from DB '''

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, home_geo, known_devices FROM users WHERE id = %s",
        (user_id,)
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    return {"id": row[0], "home_geo": row[1], "known_devices": row[2]}


def fetch_past_transactions(user_id: str):
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
        (user_id,)
    )

    columns = [
        "id", "user_id", "amount", "merchant_category", "timestamp",
        "device_id", "ip_address", "billing_geo", "shipping_geo",
    ]

    rows = [dict(zip(columns, r)) for r in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows

# ---------------- Endpoints ----------------#


@app.post("/score", response_model=ScoreResponse)
def score_transaction(tx: TransactionIn):
    ''' Looks up the user, fetches their history and runs the FraudScorer'''
    # 1 - look up the user
    user = fetch_user(tx.user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User {tx.user_id} not found.")

    # 2 - get past tranasctions
    past_transactions = fetch_past_transactions(tx.user_id)

    # 3 - convert incoming request to a dict
    from datetime import datetime

    tx_dict = {
        "id": tx.id,
        "user_id": tx.user_id,
        "amount": tx.amount,
        "merchant_category": tx.merchant_category,
        "timestamp": datetime.fromisoformat(tx.timestamp),
        "device_id": tx.device_id,
        "ip_address": tx.ip_address,
        "billing_geo": tx.billing_geo,
        "shipping_geo": tx.shipping_geo,
    }

    # 4 - score
    result = scorer.score(tx_dict, user, past_transactions)

    return ScoreResponse(
        transaction_id=tx.id,
        score=result["score"],
        decision=result["decision"],
        top_features=result["top_features"],
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": scorer.model is not None}
