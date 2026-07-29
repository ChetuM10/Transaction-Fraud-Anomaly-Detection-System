# Transaction Fraud & Anomaly Detection System

A real-time fraud detection service that scores transactions against each user's behavioral baseline — not static rules — and flags anomalies with human-readable explanations for reviewer action.

## Problem

Small fintech platforms and marketplaces can't afford enterprise fraud tools like Sift or Stripe Radar. Most rely on hand-written rules ("flag if amount > X") which miss new fraud patterns and generate excessive false positives.

## Solution

A scoring service that builds a behavioral profile per user (typical amount, location, device, frequency) and flags transactions that deviate significantly — with an explanation of *why* it was flagged, so a human reviewer can act quickly.

## Architecture

```
Checkout → FastAPI Scoring API → Feature Engineering → Model + SHAP → Score + Reasons
                  ↕                                                        ↓
             PostgreSQL                                              Flags Table
            (users, transactions)                                        ↓
                                                                  React Dashboard
                                                                  (review + feedback)
```

## Key Features

- **Behavioral baseline scoring** — compares each transaction against the user's own history, not one-size-fits-all rules
- **Dual model comparison** — Isolation Forest (unsupervised) vs XGBoost (supervised), evaluated with PR-AUC
- **Explainable flags** — SHAP-powered explanations ("amount is 4x user's average", "new device") for every flagged transaction
- **Reviewer dashboard** — queue, detail view, and outcome marking (true/false positive)
- **Feedback loop** — reviewer outcomes feed back into model evaluation and retraining

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend / ML | Python, FastAPI, scikit-learn, XGBoost, SHAP |
| Database | PostgreSQL |
| Frontend | React |
| Deployment | Render / Railway |

## Database Schema

```
users ──1:N── transactions ──1:1── flags ──N:1── model_versions
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/score` | Score a transaction in real time |
| GET | `/flags` | List flagged transactions |
| POST | `/flags/{id}/review` | Submit reviewer outcome |
| GET | `/model-versions` | List model versions + metrics |

## Project Roadmap

- [x] Database schema + synthetic data generator
- [ ] Feature engineering (velocity, amount deviation, geo/device mismatch, time-of-day)
- [ ] Model training + PR-AUC evaluation
- [ ] Threshold tuning + SHAP integration
- [ ] FastAPI scoring endpoint
- [ ] Flags table + review endpoints
- [ ] React reviewer dashboard
- [ ] Model versioning + retraining script

## Setup

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate    # Windows

# Install dependencies
pip install psycopg2-binary pandas numpy faker python-dotenv

# Create database
psql -U postgres -c "CREATE DATABASE fraud_detection;"

# Run schema
psql -U postgres -d fraud_detection -f db/schema.sql
```

## License

MIT
