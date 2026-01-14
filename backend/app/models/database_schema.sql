-- MASTERPOST.IO V2.0 DATABASE SCHEMA
-- Arquitectura híbrida con planes y control de costos

-- Users table with subscription plans
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    plan VARCHAR(20) DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'business')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'cancelled')),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Plan limits and features
CREATE TABLE plan_features (
    plan VARCHAR(20) PRIMARY KEY,
    max_images_per_month INTEGER NOT NULL,
    max_images_per_zip INTEGER NOT NULL,
    qwen_api_access BOOLEAN DEFAULT FALSE,
    watermark_required BOOLEAN DEFAULT TRUE,
    api_access BOOLEAN DEFAULT FALSE,
    priority_processing BOOLEAN DEFAULT FALSE,
    price_usd DECIMAL(10,2) DEFAULT 0.00,
    description TEXT
);

-- Insert plan features
INSERT INTO plan_features VALUES
('free', 10, 10, FALSE, TRUE, FALSE, FALSE, 0.00, 'Basic image processing with watermark'),
('pro', 500, 500, TRUE, FALSE, FALSE, TRUE, 49.00, 'Professional AI processing without watermark'),
('business', 1500, 1500, TRUE, FALSE, TRUE, TRUE, 119.00, 'Enterprise features with API access');

-- Monthly usage tracking
CREATE TABLE user_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    images_processed INTEGER DEFAULT 0,
    qwen_api_calls INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, year, month)
);

-- Enhanced jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(30) DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'completed_with_errors', 'failed', 'cancelled')),
    pipeline VARCHAR(20) NOT NULL CHECK (pipeline IN ('amazon', 'instagram', 'ebay')),
    processing_method VARCHAR(20) DEFAULT 'local' CHECK (processing_method IN ('local', 'qwen')),
    total_files INTEGER DEFAULT 0,
    processed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    is_zip_upload BOOLEAN DEFAULT FALSE,
    original_filename VARCHAR(255),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- File tracking for each job
CREATE TABLE job_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    original_name VARCHAR(255) NOT NULL,
    saved_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    processing_method VARCHAR(20) DEFAULT 'local',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API keys for Business plan users
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    last_used_at TIMESTAMP,
    requests_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Billing and transaction history
CREATE TABLE billing_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    stripe_payment_intent_id VARCHAR(255),
    amount_usd DECIMAL(10,2) NOT NULL,
    plan VARCHAR(20) NOT NULL,
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System configuration
CREATE TABLE system_config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert system configuration
INSERT INTO system_config VALUES
('qwen_api_endpoint', 'https://qwen-api.example.com/v1/image-edit', 'Qwen Image Edit API endpoint'),
('qwen_rate_limit_per_minute', '60', 'API calls per minute limit'),
('maintenance_mode', 'false', 'Enable maintenance mode'),
('watermark_text', 'Processed by Masterpost.io', 'Watermark text for free plan'),
('max_file_size_mb', '100', 'Maximum file size in MB');

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_plan ON users(plan);
CREATE INDEX idx_user_usage_monthly ON user_usage(user_id, year, month);
CREATE INDEX idx_jobs_user_status ON jobs(user_id, status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_job_files_job_id ON job_files(job_id);
CREATE INDEX idx_api_keys_user_active ON api_keys(user_id, is_active);

-- Functions for usage tracking
CREATE OR REPLACE FUNCTION update_user_usage(
    p_user_id UUID,
    p_images_count INTEGER DEFAULT 1,
    p_qwen_calls INTEGER DEFAULT 0
) RETURNS VOID AS $$
DECLARE
    current_year INTEGER := EXTRACT(YEAR FROM CURRENT_DATE);
    current_month INTEGER := EXTRACT(MONTH FROM CURRENT_DATE);
BEGIN
    INSERT INTO user_usage (user_id, year, month, images_processed, qwen_api_calls)
    VALUES (p_user_id, current_year, current_month, p_images_count, p_qwen_calls)
    ON CONFLICT (user_id, year, month)
    DO UPDATE SET
        images_processed = user_usage.images_processed + p_images_count,
        qwen_api_calls = user_usage.qwen_api_calls + p_qwen_calls,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to check usage limits
CREATE OR REPLACE FUNCTION check_usage_limit(p_user_id UUID) RETURNS TABLE(
    can_process BOOLEAN,
    remaining_images INTEGER,
    plan_limit INTEGER
) AS $$
DECLARE
    user_plan VARCHAR(20);
    plan_limit INTEGER;
    current_usage INTEGER;
    current_year INTEGER := EXTRACT(YEAR FROM CURRENT_DATE);
    current_month INTEGER := EXTRACT(MONTH FROM CURRENT_DATE);
BEGIN
    -- Get user plan
    SELECT plan INTO user_plan FROM users WHERE id = p_user_id;

    -- Get plan limit
    SELECT max_images_per_month INTO plan_limit
    FROM plan_features WHERE plan = user_plan;

    -- Get current usage
    SELECT COALESCE(images_processed, 0) INTO current_usage
    FROM user_usage
    WHERE user_id = p_user_id AND year = current_year AND month = current_month;

    -- Return results
    RETURN QUERY SELECT
        (current_usage < plan_limit) as can_process,
        (plan_limit - current_usage) as remaining_images,
        plan_limit;
END;
$$ LANGUAGE plpgsql;