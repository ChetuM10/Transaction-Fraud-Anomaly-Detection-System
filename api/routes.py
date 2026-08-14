from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

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
    flag_id: int
    score: float
    decision: str
    top_features: list[FeatureExplanation]


class FlagOut(BaseModel):
    id: int
    transaction_id: id
    score: float
    decision: str
    top_features: list
    outcome: str
    reviewed_by: str | None
    created_at: str
    reviewed_at: str | None

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


def save_flag(transaction_id, score, top_features, decision):
    ''' Inserts a scored transaction into the flag'''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """ 
        INSERT INTO flags (transaction_id, score, top_features, decision)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (transaction_id, score, json.dumps(top_features), decision),
    )
    flag_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return flag_id

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

    # 5 - save flag to DB
    flag_id = save_flag(tx.id, result["score"],
                        result["top_features"], result["decision"])

    return ScoreResponse(
        transaction_id=tx.id,
        flag_id=flag_id,
        score=result["score"],
        decision=result["decision"],
        top_features=result["top_features"],
    )


@app.get("/flags", response_model=list[FlagOut])
def list_flags(decision: str | None = None, outcome: str | None = None):

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, transaction_id, score, decision, top_features, outcome, reviewed_by, created_at, reviewed_at FROM flags"
    conditions = []
    params = []

    if decision:
        conditions.append("decision = %s")
        params.append(decision)
    if outcome:
        conditions.append("outcome = %s")
        params.append(outcome)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY score DESC "

    cursor.execute(query, tuple(params))

    columns = ["id", "transaction_id", "score", "decision", "top_features",
               "outcome", "reviewed_by", "created_at", "reviewed_at"]

    rows = [dict(zip(columns, r)) for r in cursor.fetchall()]

    cursor.close()
    conn.close()

    # convert datetime objects to strings for JSON
    for row in rows:
        row["score"] = float(row["score"])
        row["created_at"] = str(row["created_at"])
        row["reviewed_at"] = str(
            row["reviewed_at"]) if row["reviewed_at"] else None

    return rows


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": scorer.model is not None}
