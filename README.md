# Transaction Fraud & Anomaly Detection System

A machine learning system that detects fraudulent transactions by comparing activity against each user's historical behavioral baseline. It features real-time SHAP explainability, an interactive human-analyst review dashboard, and an automated feedback retraining loop.

---

## 1. Overview & Problem

### The Problem

Traditional fraud detection systems at smaller fintech companies rely heavily on static, hardcoded rules (such as `amount > 5000` or `country != home_country`). These rules fail in two major ways:

1. **High False Positive Rates:** A legitimate user making a rare high-value purchase gets blocked unnecessarily, causing customer friction.
2. **Blind to Behavioral Shifts:** Fraudsters operating below hard limits (e.g., draining small amounts from an unusual device at 3 AM) pass through unnoticed.

### The Solution

Instead of static rules, this system constructs a personalized behavioral profile for each user (historical average spend, known devices, typical transaction hours, and geographic history). Every incoming transaction is scored dynamically using machine learning, explainability vectors (TreeSHAP) are generated in real time, and human analysts can confirm or dismiss flags to continuously retrain and improve the model.

---

## 2. Technical File-Level Flow Diagram

The diagram below illustrates how each file in the codebase communicates across the data, backend, frontend, and retraining pipelines:

```
                      INCOMING TRANSACTION PAYLOAD
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │         api/routes.py                │
               │ (FastAPI Router & Endpoint Handlers) │
               └──────────────────┬───────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  │ Fetch User Profile & History  │
                  ▼                               ▼
       ┌─────────────────────┐         ┌─────────────────────┐
       │  db/connection.py   │         │  models/scorer.py   │
       │ (PostgreSQL Driver) │         │ (FraudScorer Class) │
       └──────────┬──────────┘         └──────────┬──────────┘
                  │                               │
                  │ Reads DB                      │ Calls Feature Engine
                  ▼                               ▼
       ┌─────────────────────┐         ┌────────────────────────┐
       │   PostgreSQL DB     │         │ features/engineering.py│
       │ (users/transactions)│         │ (7 Behavioral Signals) │
       └─────────────────────┘         └──────────┬─────────────┘
                                                  │
                                                  ▼
                                       ┌────────────────────────┐
                                       │ models/saved_models/   │
                                       │   best_model.joblib    │
                                       │ (Trained XGBoost)      │
                                       └──────────┬─────────────┘
                                                  │
                                                  ▼
                                       ┌────────────────────────┐
                                       │    TreeSHAP Engine     │
                                       │ (Top 3 Impact Reasons) │
                                       └──────────┬─────────────┘
                                                  │
                                                  ▼
                                       ┌────────────────────────┐
                                       │   POST /flags (Saved)  │
                                       └──────────┬─────────────┘
                                                  │
                                                  ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                             FRONTEND UI LAYER                               │
 │                                                                             │
 │    ┌─────────────────────────┐           ┌─────────────────────────────┐    │
 │    │ frontend/api/client.ts  │ ◄───────► │    frontend/src/App.tsx     │    │
 │    │  (Type-Safe API Courier)│           │   (Tab & State Manager)     │    │
 │    └────────────┬────────────┘           └──────────────┬──────────────┘    │
 │                 │                                       │                   │
 │                 ▼                                       ▼                   │
 │    ┌─────────────────────────┐           ┌─────────────────────────────┐    │
 │    │ queue/FlagsTable.tsx    │           │ overview/OverviewDashboard  │    │
 │    │ (Filterable Flag Queue) │           │ (KPI Cards & Volume Chart)  │    │
 │    └────────────┬────────────┘           └─────────────────────────────┘    │
 │                 │                                                           │
 │                 ▼                                                           │
 │    ┌─────────────────────────┐           ┌─────────────────────────────┐    │
 │    │ queue/ReviewPanel.tsx   │ ────────► │    queue/ShapChart.tsx      │    │
 │    │ (Analyst Decision Modal)│           │   (Recharts Visualization)  │    │
 │    └────────────┬────────────┘           └─────────────────────────────┘    │
 └─────────────────┼───────────────────────────────────────────────────────────┘
                   │
                   │ Human Verdict: Confirm Fraud (TP) / False Positive (FP)
                   ▼
       ┌───────────────────────┐
       │     PostgreSQL DB     │
       │  flags table updated  │
       └───────────┬───────────┘
                   │
                   │ Periodic Retraining
                   ▼
       ┌───────────────────────┐
       │   models/retrain.py   │
       │  (Continuous Learning │
       │    & PR-AUC Gating)   │
       └───────────┬───────────┘
                   │
                   │ If New PR-AUC > Active Model PR-AUC
                   ▼
       ┌───────────────────────┐
       │   model_versions DB   │
       │ (Audit Trail & Deploy)│
       └───────────────────────┘
```

---

## 3. Tech Stack

| Layer                  | Technology                           | Key Details                                                      |
| ---------------------- | ------------------------------------ | ---------------------------------------------------------------- |
| **Backend Framework**  | Python 3.10+, FastAPI, Uvicorn       | Async ASGI server, Pydantic validation, CORS middleware          |
| **Machine Learning**   | XGBoost, Scikit-Learn                | Supervised classification, `scale_pos_weight` imbalance handling |
| **Explainability**     | SHAP (SHapley Additive exPlanations) | Exact local feature contribution vectors via `TreeExplainer`     |
| **Database**           | PostgreSQL 14+, `psycopg2`           | Relational schema with JSONB metadata and foreign key integrity  |
| **Frontend Framework** | React 18, TypeScript, Vite           | Strict type safety, single-page client architecture              |
| **Styling & Icons**    | Tailwind CSS v4, Lucide React        | Glassmorphic dark theme, responsive grid layouts                 |
| **Data Visualization** | Recharts                             | Interactive SVG horizontal bar charts & decision distributions   |

---

## 4. The 7 Behavioral Feature Signals (`features/engineering.py`)

Every transaction is converted into a 7-dimensional behavioral feature vector computed against that user's historical baseline:

1. **`amount_zscore`**: How many standard deviations the transaction amount deviates from the user's historical spend average.
2. **`is_new_device`**: Binary indicator (1 if the device has never been used by this user before, else 0).
3. **`is_geo_mismatch`**: Binary indicator (1 if the shipping location differs from the user's home location, else 0).
4. **`hour_deviation`**: How far the transaction time deviates from the user's normal active hours.
5. **`velocity_10min`**: How many transactions this user attempted in just the last 10 minutes (detects rapid card testing).
6. **`is_odd_hour`**: Binary indicator (1 if the transaction happened late at night between 12 AM and 5 AM, else 0).
7. **`category_diversity_1hr`**: Count of different merchant categories the user purchased from in the last hour.

---

## 5. API Endpoints (`api/routes.py`)

| Method | Endpoint                  | Description                                                                                                                       |
| ------ | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `POST` | `/score`                  | Ingests transaction JSON, queries user history, builds features, runs XGBoost + SHAP, and saves flag to DB.                       |
| `GET`  | `/flags`                  | Fetches scored transactions with optional filters (`?decision=auto_block&outcome=pending`).                                       |
| `POST` | `/flags/{flag_id}/review` | Submits human analyst verdict (`true_positive` / `false_positive`), records timestamp and reviewer name. Prevents double-reviews. |
| `GET`  | `/model-versions`         | Lists all trained model iterations, training dates, metrics (PR-AUC), and artifact paths.                                         |
| `GET`  | `/health`                 | Health check verifying database connectivity and model memory allocation.                                                         |

---

## 6. Significance & Business Impact

1. **Explainable AI (XAI) for Regulatory Compliance:** Financial compliance requires organizations to explain _why_ an automated system declined or flagged a customer transaction. SHAP values translate black-box gradient boosting outputs into readable, defensible root causes.
2. **PR-AUC Optimization for Severe Class Imbalance:** Fraud datasets typically exhibit severe class imbalance (~1–3% positive fraud rate). Standard accuracy metrics give a false sense of security (a model predicting 100% normal transactions can achieve 98% accuracy). Evaluating on Precision-Recall AUC ensures the system prioritizes true positive detection without overwhelming analysts with false alarms.
3. **Audit Trail & Rollback Governance:** The `model_versions` registry ensures every deployed model binary has an immutable record of its training parameters, exact feature list, and evaluation metrics, eliminating undocumented production deployments.
4. **Operational Triage Efficiency:** Three-tiered automated decisioning (**Auto-Approve**, **Needs Review**, **Auto-Block**) reduces manual review workload by routing only borderline, ambiguous transactions to human investigators.

---

## 7. Setup & Execution Guide

### 1. Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 2. Backend Installation & Database Setup

```bash
# Clone the repository
git clone https://github.com/ChetuM10/Transaction-Fraud-Anomaly-Detection-System.git
cd Transaction-Fraud-Anomaly-Detection-System

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate    # Windows (or source .venv/bin/activate on Linux/macOS)

# Install Python packages
pip install fastapi uvicorn scikit-learn xgboost shap pandas numpy psycopg2-binary python-dotenv joblib

# Create and initialize database
psql -U postgres -c "CREATE DATABASE fraud_detection;"
psql -U postgres -d fraud_detection -f db/schema.sql

# Generate synthetic behavioral dataset and train initial model
py -m data.generator
py -m models.train
```

### 3. Running the Servers

**Backend API (Port 8000):**

```bash
py -m uvicorn api.routes:app --reload --port 8000
```

_Interactive Swagger docs available at `http://localhost:8000/docs`._

**Frontend Dashboard (Port 5173):**

```bash
cd frontend
npm install
npm run dev
```

_Dashboard available at `http://localhost:5173`._

### 4. Running Feedback Retraining

Once analysts have submitted 10+ reviews in the dashboard:

```bash
py -m models.retrain
```

---

## 8. Future Advancements & Research Roadmap

1. **Population Stability Index (PSI) & Concept Drift Monitoring:** Implement automated drift checks that compare inference feature distributions over rolling 7-day windows against baseline training distributions to catch emerging macroeconomic shifts or seasonal spending changes before model degradation occurs.
2. **Graph Neural Networks (GNNs) for Fraud Rings:** Incorporate graph embeddings (e.g., GraphSAGE) to uncover multi-account syndicates sharing identical device fingerprints, card tokens, or IP subnets across disparate user identities.
3. **Streaming Ingestion with Apache Kafka / Redis Streams:** Transition from synchronous REST scoring to high-throughput message streaming to handle tens of thousands of transactions per second with sub-10ms latency.
4. **Automated Shadow Deployment (A/B Testing):** Deploy newly retrained candidate models in shadow mode (scoring live traffic without making blocking decisions) to validate performance on production distributions prior to active traffic promotion.
5. **PII Masking & Tokenization:** Incorporate client-side hashing and format-preserving encryption (FPE) for IP addresses, geolocation coordinates, and device identifiers to meet strict data privacy frameworks (GDPR, PCI-DSS).
