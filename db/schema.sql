/*         Tables: users, transactions         */
-- users table stpres each user's profile
CREATE TABLE if NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    avg_transaction_amount NUMERIC(12, 2) DEFAULT (0.00),
    home_geo VARCHAR(50),
    known_devices TEXT [] DEFAULT '{}'
);
-- Transactions table: log for every transaction
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES users (id),
    amount NUMERIC(12, 2) NOT NULL,
    merchant_category VARCHAR(50),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    device_id VARCHAR(100),
    ip_address VARCHAR(45),
    billing_geo VARCHAR(100),
    shipping_geo VARCHAR(100)
);

-- Flags Table: stores transactions for review

CREATE Table IF NOT EXISTS flags (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) NOT NULL REFERENCES transactions(id),
    score NUMERIC(5, 4) NOT NULL,
    top_features JSONB NOT NULL,
    decision VARCHAR(20) NOT NULL CHECK (
        decision IN ('auto_approve', 'auto_block', 'review')
    ),
    reviewed_by VARCHAR(100),
    outcome VARCHAR(20) DEFAULT 'pending' CHECK (
        outcome IN ('true_positive', 'false_positive', 'pending')
    ),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMP
);

-- MOdel versions: tracks trained model for sudit and rollback
CREATE TABLE IF NOT EXISTS model_versions (
    id SERIAL PRIMARY KEY,
    trained_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metrics JSONB NOT NULL,
    feature_list TEXT[] NOT NULL,
    model_path VARCHAR(255) NOT NULL
);