-- MASTERPOST.IO V2.0 - SUPABASE SCHEMA
-- Execute this FIRST in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. USER PROFILES TABLE
CREATE TABLE public.user_profiles (
    id uuid REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email text UNIQUE NOT NULL,
    full_name text,
    plan text NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'business')),
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'cancelled')),
    stripe_customer_id text,
    stripe_subscription_id text,
    onboarding_completed boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. PLAN FEATURES TABLE
CREATE TABLE public.plan_features (
    plan text PRIMARY KEY,
    max_images_per_month integer NOT NULL,
    max_images_per_zip integer NOT NULL,
    qwen_api_access boolean DEFAULT false,
    watermark_required boolean DEFAULT true,
    api_access boolean DEFAULT false,
    priority_processing boolean DEFAULT false,
    price_usd decimal(10,2) DEFAULT 0.00,
    description text NOT NULL,
    features_json jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Insert plan configurations
INSERT INTO public.plan_features (plan, max_images_per_month, max_images_per_zip, qwen_api_access, watermark_required, api_access, priority_processing, price_usd, description, features_json) VALUES
('free', 10, 10, false, true, false, false, 0.00, 'Basic image processing with watermark',
 '{"processing_quality": "standard", "concurrent_jobs": 1, "support_level": "community"}'),
('pro', 500, 500, true, false, false, true, 49.00, 'Professional AI processing without watermark',
 '{"processing_quality": "high", "concurrent_jobs": 3, "support_level": "priority", "api_calls_per_month": 1000}'),
('business', 1500, 1500, true, false, true, true, 119.00, 'Enterprise features with API access',
 '{"processing_quality": "premium", "concurrent_jobs": 5, "support_level": "dedicated", "api_calls_per_month": 5000, "white_label": true}');

-- 3. USER USAGE TRACKING TABLE
CREATE TABLE public.user_usage (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    year integer NOT NULL,
    month integer NOT NULL,
    images_processed integer DEFAULT 0 NOT NULL,
    qwen_api_calls integer DEFAULT 0 NOT NULL,
    jobs_created integer DEFAULT 0 NOT NULL,
    successful_jobs integer DEFAULT 0 NOT NULL,
    failed_jobs integer DEFAULT 0 NOT NULL,
    total_processing_time_seconds integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id, year, month)
);

-- 4. JOBS TABLE
CREATE TABLE public.jobs (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    status text DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'completed_with_errors', 'failed', 'cancelled')) NOT NULL,
    pipeline text NOT NULL CHECK (pipeline IN ('amazon', 'instagram', 'ebay')),
    processing_method text DEFAULT 'local' CHECK (processing_method IN ('local', 'qwen')) NOT NULL,
    total_files integer DEFAULT 0 NOT NULL,
    processed_files integer DEFAULT 0 NOT NULL,
    failed_files integer DEFAULT 0 NOT NULL,
    is_zip_upload boolean DEFAULT false,
    original_filename text,
    settings jsonb DEFAULT '{}',
    processing_started_at timestamp with time zone,
    processing_completed_at timestamp with time zone,
    estimated_completion_at timestamp with time zone,
    error_message text,
    processing_logs text[],
    metadata jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. JOB FILES TABLE
CREATE TABLE public.job_files (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_id uuid REFERENCES public.jobs(id) ON DELETE CASCADE NOT NULL,
    original_name text NOT NULL,
    saved_name text NOT NULL,
    file_size bigint,
    processing_status text DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')) NOT NULL,
    processing_method text DEFAULT 'local' CHECK (processing_method IN ('local', 'qwen')),
    processing_time_seconds decimal(10,3),
    error_message text,
    input_path text,
    output_path text,
    metadata jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. API KEYS TABLE
CREATE TABLE public.api_keys (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    key_name text NOT NULL,
    api_key text UNIQUE NOT NULL,
    key_prefix text NOT NULL,
    last_used_at timestamp with time zone,
    requests_count integer DEFAULT 0 NOT NULL,
    rate_limit_per_hour integer DEFAULT 100 NOT NULL,
    allowed_origins text[],
    scopes text[] DEFAULT array['upload', 'process', 'status', 'download'],
    is_active boolean DEFAULT true,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. BILLING TRANSACTIONS TABLE
CREATE TABLE public.billing_transactions (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.user_profiles(id) ON DELETE CASCADE NOT NULL,
    stripe_payment_intent_id text,
    stripe_invoice_id text,
    amount_usd decimal(10,2) NOT NULL,
    currency text DEFAULT 'USD',
    plan text NOT NULL,
    billing_period_start date NOT NULL,
    billing_period_end date NOT NULL,
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'succeeded', 'failed', 'cancelled', 'refunded')) NOT NULL,
    failure_reason text,
    receipt_url text,
    invoice_pdf text,
    metadata jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 8. SYSTEM CONFIGURATION TABLE
CREATE TABLE public.system_config (
    key text PRIMARY KEY,
    value text NOT NULL,
    description text,
    data_type text DEFAULT 'string' CHECK (data_type IN ('string', 'number', 'boolean', 'json')),
    is_secret boolean DEFAULT false,
    category text DEFAULT 'general',
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_by uuid REFERENCES public.user_profiles(id)
);

-- Insert system configuration
INSERT INTO public.system_config (key, value, description, data_type, category) VALUES
('qwen_api_endpoint', 'https://qwen-api.example.com/v1/image-edit', 'Qwen Image Edit API endpoint', 'string', 'api'),
('qwen_rate_limit_per_minute', '60', 'API calls per minute limit', 'number', 'api'),
('maintenance_mode', 'false', 'Enable maintenance mode', 'boolean', 'system'),
('watermark_text', 'Processed by Masterpost.io', 'Watermark text for free plan', 'string', 'processing'),
('max_file_size_mb', '100', 'Maximum file size in MB', 'number', 'upload'),
('concurrent_jobs_limit', '10', 'Maximum concurrent processing jobs', 'number', 'processing'),
('zip_extraction_timeout_minutes', '5', 'Timeout for ZIP extraction', 'number', 'processing'),
('cleanup_old_jobs_days', '30', 'Days to keep completed jobs', 'number', 'cleanup'),
('notification_email', 'admin@masterpost.io', 'Admin notification email', 'string', 'notifications'),
('stripe_webhook_secret', '', 'Stripe webhook endpoint secret', 'string', 'billing');

-- 9. PERFORMANCE ANALYTICS TABLE
CREATE TABLE public.performance_metrics (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    metric_name text NOT NULL,
    metric_value decimal(15,6) NOT NULL,
    metric_unit text DEFAULT 'count',
    dimensions jsonb DEFAULT '{}',
    timestamp timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 10. AUDIT LOG TABLE
CREATE TABLE public.audit_logs (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES public.user_profiles(id) ON DELETE SET NULL,
    action text NOT NULL,
    resource_type text NOT NULL,
    resource_id text,
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    user_agent text,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX idx_user_profiles_plan ON public.user_profiles(plan);
CREATE INDEX idx_user_profiles_status ON public.user_profiles(status);
CREATE INDEX idx_user_usage_user_monthly ON public.user_usage(user_id, year, month);
CREATE INDEX idx_user_usage_monthly_stats ON public.user_usage(year, month);
CREATE INDEX idx_jobs_user_status ON public.jobs(user_id, status);
CREATE INDEX idx_jobs_status_created ON public.jobs(status, created_at);
CREATE INDEX idx_jobs_user_created ON public.jobs(user_id, created_at DESC);
CREATE INDEX idx_jobs_processing_method ON public.jobs(processing_method);
CREATE INDEX idx_job_files_job_id ON public.job_files(job_id);
CREATE INDEX idx_job_files_status ON public.job_files(processing_status);
CREATE INDEX idx_api_keys_user_active ON public.api_keys(user_id, is_active);
CREATE INDEX idx_api_keys_prefix ON public.api_keys(key_prefix);
CREATE INDEX idx_billing_user_status ON public.billing_transactions(user_id, status);
CREATE INDEX idx_billing_stripe_payment ON public.billing_transactions(stripe_payment_intent_id);
CREATE INDEX idx_billing_period ON public.billing_transactions(billing_period_start, billing_period_end);
CREATE INDEX idx_performance_metrics_name_timestamp ON public.performance_metrics(metric_name, timestamp DESC);
CREATE INDEX idx_performance_metrics_timestamp ON public.performance_metrics(timestamp DESC);
CREATE INDEX idx_audit_logs_user_action ON public.audit_logs(user_id, action);
CREATE INDEX idx_audit_logs_resource ON public.audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_timestamp ON public.audit_logs(created_at DESC);