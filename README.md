# Transaction Fraud & Anomaly Detection System

A transaction scoring service that flags suspicious activity by comparing each transaction against the user's own historical behavior — not static rules. Flagged transactions are surfaced in a React dashboard where analysts can confirm or dismiss them.

---

## Problem

Static rules like "flag if amount > 5000" generate too many false positives and miss fraud that stays under the threshold. This system builds a per-user baseline and flags deviations from it.

---

## What's Actually Built

- **Backend API** (FastAPI) — scores incoming transactions, saves flags to a database, and serves the frontend
- **ML pipeline** — trains Isolation Forest and XGBoost on synthetic transaction data, picks the better model by PR-AUC
- **Feature engineering** — 7 behavioral signals computed from user history per transaction
- **SHAP explanations** — top 3 reasons for each flag, shown to analysts
- **React dashboard** — review queue, flag detail panel, KPI overview
- **Human-in-the-loop** — analysts mark flags as confirmed fraud or false positive; `/reload-model` hot-swaps the model after retraining without restarting the server

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| ML | XGBoost, scikit-learn, SHAP |
| Database | PostgreSQL, psycopg2 |
| Frontend | React, TypeScript, Vite, Tailwind CSS |

---

## The 7 Behavioral Features (`features/engineering.py`)

Each transaction is converted to a 7-number vector before hitting the model:

1. `velocity_10min` — how many transactions this user made in the last 10 minutes
2. `amount_zscore` — how many standard deviations this amount is from the user's average
3. `is_new_device` — 1 if the device has never been seen on this account, 0 otherwise
4. `is_geo_mismatch` — 1 if shipping location differs from the user's home location
5. `is_odd_hour` — 1 if the transaction happened between 12 AM and 5 AM
6. `hour_deviation` — how far the transaction time is from the user's normal hours
7. `category_diversity_1hr` — how many different merchant categories the user hit in the last hour

---

## API Endpoints (`api/routes.py`)

| Method | Endpoint | What it does |
|---|---|---|
| POST | `/score` | Scores a transaction and saves the flag |
| GET | `/flags` | Lists flags, supports `?decision=` and `?outcome=` filters |
| POST | `/flags/{id}/review` | Analyst submits `true_positive` or `false_positive` verdict |
| GET | `/model-versions` | Lists trained model versions and their metrics |
| POST | `/reload-model` | Reloads the model from disk after retraining — no server restart needed |
| GET | `/health` | Basic health check |

The API also serves the compiled React dashboard at `/`.

---

## Setup

### Requirements

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Backend

```bash
git clone https://github.com/ChetuM10/Transaction-Fraud-Anomaly-Detection-System.git
cd Transaction-Fraud-Anomaly-Detection-System

python -m venv .venv
.\.venv\Scripts\Activate     # Windows

pip install -r requirements.txt

# Create and initialize the database
psql -U postgres -c "CREATE DATABASE fraud_detection;"
psql -U postgres -d fraud_detection -f db/schema.sql

# Generate synthetic data and train the model
py scripts/generate_data.py
py -m models.train
```

### Run locally

```bash
# Backend (port 8000)
py -m uvicorn api.routes:app --reload --port 8000

# Frontend dev server (port 5173)
cd frontend
npm install
npm run dev
```

Swagger docs: `http://localhost:8000/docs`
Dashboard (dev): `http://localhost:5173`
Dashboard (via backend): `http://localhost:8000`

### Render deployment

Build command:
```
cd frontend && npm install && npm run build && cd .. && pip install -r requirements.txt
```
Start command:
```
uvicorn api.routes:app --host 0.0.0.0 --port $PORT
```

---

## Project Status

- [x] Database schema + synthetic data generator
- [x] 7-feature behavioral engineering
- [x] Train Isolation Forest + XGBoost, compare with PR-AUC
- [x] Threshold tuning + SHAP integration
- [x] FastAPI scoring endpoint
- [x] Flags table + review endpoints
- [x] React dashboard (queue, detail, review, KPI overview)
- [ ] Model versioning table + retraining script (not yet built)
