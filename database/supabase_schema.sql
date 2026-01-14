-- =====================================================
-- MASTERPOST.IO V2.0 - COMPLETE SUPABASE SCHEMA
-- Production-ready database with authentication & RLS
-- =====================================================

-- Enable required extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- =====================================================
-- 1. USERS PROFILE TABLE (extends Supabase auth.users)
-- =====================================================

create table public.user_profiles (
    id uuid references auth.users(id) on delete cascade primary key,
    email text unique not null,
    full_name text,
    plan text not null default 'free' check (plan in ('free', 'pro', 'business')),
    status text not null default 'active' check (status in ('active', 'suspended', 'cancelled')),
    stripe_customer_id text,
    stripe_subscription_id text,
    onboarding_completed boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- =====================================================
-- 2. PLAN FEATURES TABLE (static configuration)
-- =====================================================

create table public.plan_features (
    plan text primary key,
    max_images_per_month integer not null,
    max_images_per_zip integer not null,
    qwen_api_access boolean default false,
    watermark_required boolean default true,
    api_access boolean default false,
    priority_processing boolean default false,
    price_usd decimal(10,2) default 0.00,
    description text not null,
    features_json jsonb default '{}',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Insert plan configurations
insert into public.plan_features (plan, max_images_per_month, max_images_per_zip, qwen_api_access, watermark_required, api_access, priority_processing, price_usd, description, features_json) values
('free', 10, 10, false, true, false, false, 0.00, 'Basic image processing with watermark',
 '{"processing_quality": "standard", "concurrent_jobs": 1, "support_level": "community"}'),
('pro', 500, 500, true, false, false, true, 49.00, 'Professional AI processing without watermark',
 '{"processing_quality": "high", "concurrent_jobs": 3, "support_level": "priority", "api_calls_per_month": 1000}'),
('business', 1500, 1500, true, false, true, true, 119.00, 'Enterprise features with API access',
 '{"processing_quality": "premium", "concurrent_jobs": 5, "support_level": "dedicated", "api_calls_per_month": 5000, "white_label": true}');

-- =====================================================
-- 3. USER USAGE TRACKING TABLE
-- =====================================================

create table public.user_usage (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles(id) on delete cascade not null,
    year integer not null,
    month integer not null,
    images_processed integer default 0 not null,
    qwen_api_calls integer default 0 not null,
    jobs_created integer default 0 not null,
    successful_jobs integer default 0 not null,
    failed_jobs integer default 0 not null,
    total_processing_time_seconds integer default 0 not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    unique(user_id, year, month)
);

-- =====================================================
-- 4. JOBS TABLE (main processing jobs)
-- =====================================================

create table public.jobs (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles(id) on delete cascade not null,
    status text default 'uploaded' check (status in ('uploaded', 'processing', 'completed', 'completed_with_errors', 'failed', 'cancelled')) not null,
    pipeline text not null check (pipeline in ('amazon', 'instagram', 'ebay')),
    processing_method text default 'local' check (processing_method in ('local', 'qwen')) not null,
    total_files integer default 0 not null,
    processed_files integer default 0 not null,
    failed_files integer default 0 not null,
    is_zip_upload boolean default false,
    original_filename text,
    settings jsonb default '{}',
    processing_started_at timestamp with time zone,
    processing_completed_at timestamp with time zone,
    estimated_completion_at timestamp with time zone,
    error_message text,
    processing_logs text[],
    metadata jsonb default '{}',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- =====================================================
-- 5. JOB FILES TABLE (individual files in jobs)
-- =====================================================

create table public.job_files (
    id uuid default uuid_generate_v4() primary key,
    job_id uuid references public.jobs(id) on delete cascade not null,
    original_name text not null,
    saved_name text not null,
    file_size bigint,
    processing_status text default 'pending' check (processing_status in ('pending', 'processing', 'completed', 'failed')) not null,
    processing_method text default 'local' check (processing_method in ('local', 'qwen')),
    processing_time_seconds decimal(10,3),
    error_message text,
    input_path text,
    output_path text,
    metadata jsonb default '{}',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- =====================================================
-- 6. API KEYS TABLE (for Business plan users)
-- =====================================================

create table public.api_keys (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles(id) on delete cascade not null,
    key_name text not null,
    api_key text unique not null,
    key_prefix text not null, -- First 8 characters for display
    last_used_at timestamp with time zone,
    requests_count integer default 0 not null,
    rate_limit_per_hour integer default 100 not null,
    allowed_origins text[],
    scopes text[] default array['upload', 'process', 'status', 'download'],
    is_active boolean default true,
    expires_at timestamp with time zone,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- =====================================================
-- 7. BILLING TRANSACTIONS TABLE
-- =====================================================

create table public.billing_transactions (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles(id) on delete cascade not null,
    stripe_payment_intent_id text,
    stripe_invoice_id text,
    amount_usd decimal(10,2) not null,
    currency text default 'USD',
    plan text not null,
    billing_period_start date not null,
    billing_period_end date not null,
    status text default 'pending' check (status in ('pending', 'processing', 'succeeded', 'failed', 'cancelled', 'refunded')) not null,
    failure_reason text,
    receipt_url text,
    invoice_pdf text,
    metadata jsonb default '{}',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- =====================================================
-- 8. SYSTEM CONFIGURATION TABLE
-- =====================================================

create table public.system_config (
    key text primary key,
    value text not null,
    description text,
    data_type text default 'string' check (data_type in ('string', 'number', 'boolean', 'json')),
    is_secret boolean default false,
    category text default 'general',
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_by uuid references public.user_profiles(id)
);

-- Insert system configuration
insert into public.system_config (key, value, description, data_type, category) values
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

-- =====================================================
-- 9. PERFORMANCE ANALYTICS TABLE
-- =====================================================

create table public.performance_metrics (
    id uuid default uuid_generate_v4() primary key,
    metric_name text not null,
    metric_value decimal(15,6) not null,
    metric_unit text default 'count',
    dimensions jsonb default '{}',
    timestamp timestamp with time zone default timezone('utc'::text, now()) not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- =====================================================
-- 10. AUDIT LOG TABLE
-- =====================================================

create table public.audit_logs (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles(id) on delete set null,
    action text not null,
    resource_type text not null,
    resource_id text,
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    user_agent text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- User profiles indexes
create index idx_user_profiles_email on public.user_profiles(email);
create index idx_user_profiles_plan on public.user_profiles(plan);
create index idx_user_profiles_status on public.user_profiles(status);

-- Usage tracking indexes
create index idx_user_usage_user_monthly on public.user_usage(user_id, year, month);
create index idx_user_usage_monthly_stats on public.user_usage(year, month);

-- Jobs indexes
create index idx_jobs_user_status on public.jobs(user_id, status);
create index idx_jobs_status_created on public.jobs(status, created_at);
create index idx_jobs_user_created on public.jobs(user_id, created_at desc);
create index idx_jobs_processing_method on public.jobs(processing_method);

-- Job files indexes
create index idx_job_files_job_id on public.job_files(job_id);
create index idx_job_files_status on public.job_files(processing_status);

-- API keys indexes
create index idx_api_keys_user_active on public.api_keys(user_id, is_active);
create index idx_api_keys_prefix on public.api_keys(key_prefix);

-- Billing indexes
create index idx_billing_user_status on public.billing_transactions(user_id, status);
create index idx_billing_stripe_payment on public.billing_transactions(stripe_payment_intent_id);
create index idx_billing_period on public.billing_transactions(billing_period_start, billing_period_end);

-- Performance metrics indexes
create index idx_performance_metrics_name_timestamp on public.performance_metrics(metric_name, timestamp desc);
create index idx_performance_metrics_timestamp on public.performance_metrics(timestamp desc);

-- Audit logs indexes
create index idx_audit_logs_user_action on public.audit_logs(user_id, action);
create index idx_audit_logs_resource on public.audit_logs(resource_type, resource_id);
create index idx_audit_logs_timestamp on public.audit_logs(created_at desc);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$ language plpgsql;

-- Apply updated_at trigger to relevant tables
create trigger update_user_profiles_updated_at before update on public.user_profiles for each row execute function update_updated_at_column();
create trigger update_user_usage_updated_at before update on public.user_usage for each row execute function update_updated_at_column();
create trigger update_jobs_updated_at before update on public.jobs for each row execute function update_updated_at_column();
create trigger update_job_files_updated_at before update on public.job_files for each row execute function update_updated_at_column();
create trigger update_billing_transactions_updated_at before update on public.billing_transactions for each row execute function update_updated_at_column();
create trigger update_system_config_updated_at before update on public.system_config for each row execute function update_updated_at_column();

-- Function to create user profile when auth user is created
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.user_profiles (id, email, full_name)
    values (new.id, new.email, coalesce(new.raw_user_meta_data->>'full_name', ''));
    return new;
end;
$$ language plpgsql security definer;

-- Trigger to create profile on user signup
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();

-- Function to update user usage statistics
create or replace function update_user_usage(
    p_user_id uuid,
    p_images_count integer default 1,
    p_qwen_calls integer default 0,
    p_job_success boolean default true
) returns void as $$
declare
    current_year integer := extract(year from current_date);
    current_month integer := extract(month from current_date);
begin
    insert into public.user_usage (
        user_id, year, month, images_processed, qwen_api_calls,
        jobs_created, successful_jobs, failed_jobs
    )
    values (
        p_user_id, current_year, current_month, p_images_count, p_qwen_calls,
        1, case when p_job_success then 1 else 0 end, case when p_job_success then 0 else 1 end
    )
    on conflict (user_id, year, month)
    do update set
        images_processed = user_usage.images_processed + p_images_count,
        qwen_api_calls = user_usage.qwen_api_calls + p_qwen_calls,
        jobs_created = user_usage.jobs_created + 1,
        successful_jobs = user_usage.successful_jobs + case when p_job_success then 1 else 0 end,
        failed_jobs = user_usage.failed_jobs + case when p_job_success then 0 else 1 end,
        updated_at = timezone('utc'::text, now());
end;
$$ language plpgsql security definer;

-- Function to check usage limits
create or replace function check_usage_limit(p_user_id uuid, p_images_count integer default 1)
returns table(
    can_process boolean,
    remaining_images integer,
    plan_limit integer,
    current_usage integer,
    user_plan text
) as $$
declare
    user_plan_val text;
    plan_limit_val integer;
    current_usage_val integer;
    current_year integer := extract(year from current_date);
    current_month integer := extract(month from current_date);
begin
    -- Get user plan
    select plan into user_plan_val from public.user_profiles where id = p_user_id;

    if user_plan_val is null then
        user_plan_val := 'free';
    end if;

    -- Get plan limit
    select max_images_per_month into plan_limit_val
    from public.plan_features where plan = user_plan_val;

    -- Get current usage
    select coalesce(images_processed, 0) into current_usage_val
    from public.user_usage
    where user_id = p_user_id and year = current_year and month = current_month;

    if current_usage_val is null then
        current_usage_val := 0;
    end if;

    -- Return results
    return query select
        (current_usage_val + p_images_count <= plan_limit_val) as can_process,
        (plan_limit_val - current_usage_val) as remaining_images,
        plan_limit_val as plan_limit,
        current_usage_val as current_usage,
        user_plan_val as user_plan;
end;
$$ language plpgsql security definer;

-- Function to generate API key
create or replace function generate_api_key(p_user_id uuid, p_key_name text)
returns text as $$
declare
    api_key_val text;
    key_prefix_val text;
begin
    -- Generate API key (mp_ prefix + 32 random characters)
    api_key_val := 'mp_' || encode(gen_random_bytes(24), 'base64');
    api_key_val := replace(replace(api_key_val, '/', '_'), '+', '-');
    key_prefix_val := substring(api_key_val from 1 for 8);

    -- Insert API key
    insert into public.api_keys (user_id, key_name, api_key, key_prefix)
    values (p_user_id, p_key_name, api_key_val, key_prefix_val);

    return api_key_val;
end;
$$ language plpgsql security definer;

-- Function to log performance metrics
create or replace function log_performance_metric(
    p_metric_name text,
    p_metric_value decimal,
    p_metric_unit text default 'count',
    p_dimensions jsonb default '{}'
) returns void as $$
begin
    insert into public.performance_metrics (metric_name, metric_value, metric_unit, dimensions)
    values (p_metric_name, p_metric_value, p_metric_unit, p_dimensions);
end;
$$ language plpgsql security definer;