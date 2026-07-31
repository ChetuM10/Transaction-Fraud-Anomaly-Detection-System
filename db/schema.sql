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