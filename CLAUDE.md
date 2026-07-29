# CLAUDE.md — Project Ground Truth

> This file is the single source of truth for the Fraud Detection project.
> Never deviate from this unless the user explicitly approves a change.

---

## 1. Project Purpose

A transaction fraud & anomaly detection system for small fintech/marketplace platforms
that can't afford enterprise fraud tools. Scores each transaction against a user's own
behavioral baseline and flags deviations with explanations for human reviewers.

---

## 2. Tech Stack (locked)

| Layer       | Technology                              |
|-------------|-----------------------------------------|
| Backend/ML  | Python, FastAPI, scikit-learn, XGBoost, pandas |
| Database    | PostgreSQL                              |
| Frontend    | React                                   |
| Deployment  | Render / Railway                        |

---

## 3. Database Schema (locked)

### `users`
| Column                 | Type      | Notes                         |
|------------------------|-----------|-------------------------------|
| id                     | PK        |                               |
| created_at             | timestamp |                               |
| avg_transaction_amount | numeric   | Baseline for deviation calc   |
| home_geo               | text      |                               |
| known_devices          | text[]    |                               |

### `transactions`
| Column            | Type      | Notes                     |
|-------------------|-----------|---------------------------|
| id                | PK        |                           |
| user_id           | FK→users  |                           |
| amount            | numeric   |                           |
| merchant_category | text      |                           |
| timestamp         | timestamp |                           |
| device_id         | text      |                           |
| ip_address        | text      |                           |
| billing_geo       | text      |                           |
| shipping_geo      | text      |                           |

### `flags`
| Column         | Type                                    | Notes                        |
|----------------|-----------------------------------------|------------------------------|
| id             | PK                                      |                              |
| transaction_id | FK→transactions                         |                              |
| score          | numeric                                 | Model output probability     |
| top_features   | JSON                                    | SHAP-derived reasons         |
| decision       | enum(auto_approve, auto_block, review)  |                              |
| reviewed_by    | text                                    |                              |
| outcome        | enum(true_positive, false_positive, pending) |                         |
| reviewed_at    | timestamp                               |                              |

### `model_versions`
| Column       | Type      | Notes                                  |
|--------------|-----------|----------------------------------------|
| id           | PK        |                                        |
| trained_at   | timestamp |                                        |
| metrics      | JSON      | pr_auc, precision_at_threshold, etc.   |
| feature_list | text[]    |                                        |
| model_path   | text      | Path to serialized model file          |

### Relationships
```
users ──1:N── transactions ──1:1── flags ──N:1── model_versions
```

---

## 4. API Endpoints (locked)

| Method | Path                  | Purpose                          | Latency    |
|--------|-----------------------|----------------------------------|------------|
| POST   | /score                | Score a transaction in real time  | Low (fast) |
| GET    | /flags                | List flagged transactions         | Normal     |
| POST   | /flags/{id}/review    | Reviewer submits outcome          | Normal     |
| GET    | /model-versions       | List model versions + metrics     | Normal     |

---

## 5. ML Pipeline (locked)

- **Models:** Isolation Forest (unsupervised) + XGBoost (supervised), compared via PR-AUC
- **Features:** velocity, amount deviation from baseline, geo/device mismatch, time-of-day anomaly, category diversity
- **Evaluation:** PR-AUC (not accuracy — imbalanced dataset)
- **Threshold:** tuned based on cost tradeoff, not default 0.5
- **Explainability:** SHAP for top contributing features per prediction
- **Retraining:** periodic, using reviewer-confirmed outcomes from flags table

---

## 6. Frontend Screens (locked)

1. **Flagged Transactions Queue** — table of pending flags, sortable by score
2. **Transaction Detail / Review** — full transaction + user history + SHAP reasons
3. **Review Action** — mark confirmed fraud / false positive
4. **Model Performance Dashboard (stretch)** — PR-AUC, precision/recall over time

---

## 7. Build Order (Milestones)

| #  | Milestone                                               | Status      |
|----|--------------------------------------------------------|-------------|
| 1  | Users/transactions schema + synthetic data generator    | NOT STARTED |
| 2  | Feature engineering functions (pure Python, tested)     | NOT STARTED |
| 3  | Train Isolation Forest + XGBoost, compare with PR-AUC   | NOT STARTED |
| 4  | Threshold tuning + SHAP integration                     | NOT STARTED |
| 5  | FastAPI `/score` endpoint                               | NOT STARTED |
| 6  | `flags` table + `/flags`, `/flags/{id}/review` endpoints| NOT STARTED |
| 7  | React dashboard (queue → detail → review screens)       | NOT STARTED |
| 8  | Model versioning table + lightweight retraining script  | NOT STARTED |
| 9  | Population-stability drift check (optional/future work) | NOT STARTED |

---

## 8. Project Structure (updated as files are created)

```
Fraud_Detection/
├── CLAUDE.md              ← this file
```

---

## 9. Builder Rules (enforced)

- Build ONE file at a time
- Explain BEFORE code: why this file exists, its responsibility, where it fits, dependencies
- Explain AFTER code: layman + technical explanation
- Show project impact after every file
- Update folder tree after every file creation/change
- Summarize and STOP after every implementation — wait for user confirmation
- Never modify architecture/schema/API/structure without explicit user approval
- Never edit files without user asking — user makes changes unless they say otherwise
