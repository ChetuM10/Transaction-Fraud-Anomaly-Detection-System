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
