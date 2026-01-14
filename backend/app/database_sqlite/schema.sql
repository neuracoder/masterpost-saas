-- SQLite Schema for Masterpost.io - Simplified Architecture
-- Replaces 15+ Supabase tables with just 3 essential tables

-- Users table (simplified authentication)
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    access_code TEXT UNIQUE NOT NULL,
    credits INTEGER DEFAULT 50,
    basic_images_processed INTEGER DEFAULT 0,
    qwen_images_processed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP
);

-- Jobs table (simplified)
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    status TEXT DEFAULT 'uploaded',
    pipeline TEXT,
    total_files INTEGER DEFAULT 0,
    processed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    settings TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES users(email)
);

-- Transactions table (credit purchases)
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    transaction_type TEXT,
    credits_added INTEGER,
    amount_paid REAL,
    stripe_session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES users(email)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_email ON jobs(email);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_transactions_email ON transactions(email);
