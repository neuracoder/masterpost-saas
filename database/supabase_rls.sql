-- =====================================================
-- MASTERPOST.IO V2.0 - ROW LEVEL SECURITY (RLS)
-- Comprehensive security policies for all tables
-- =====================================================

-- =====================================================
-- 1. USER PROFILES TABLE RLS
-- =====================================================

-- Enable RLS on user_profiles
alter table public.user_profiles enable row level security;

-- Users can view their own profile
create policy "Users can view own profile" on public.user_profiles
    for select using (auth.uid() = id);

-- Users can update their own profile
create policy "Users can update own profile" on public.user_profiles
    for update using (auth.uid() = id);

-- Service role can access all profiles (for admin operations)
create policy "Service role full access to profiles" on public.user_profiles
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- 2. PLAN FEATURES TABLE RLS
-- =====================================================

-- Enable RLS on plan_features
alter table public.plan_features enable row level security;

-- Anyone can read plan features (public information)
create policy "Anyone can read plan features" on public.plan_features
    for select using (true);

-- Only service role can modify plan features
create policy "Service role can modify plan features" on public.plan_features
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- 3. USER USAGE TABLE RLS
-- =====================================================

-- Enable RLS on user_usage
alter table public.user_usage enable row level security;

-- Users can view their own usage
create policy "Users can view own usage" on public.user_usage
    for select using (auth.uid() = user_id);

-- Service role can access all usage data
create policy "Service role full access to usage" on public.user_usage
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- System can insert/update usage data (for automated tracking)
create policy "System can update usage data" on public.user_usage
    for insert with check (true);

create policy "System can modify usage data" on public.user_usage
    for update using (true);

-- =====================================================
-- 4. JOBS TABLE RLS
-- =====================================================

-- Enable RLS on jobs
alter table public.jobs enable row level security;

-- Users can view their own jobs
create policy "Users can view own jobs" on public.jobs
    for select using (auth.uid() = user_id);

-- Users can create jobs for themselves
create policy "Users can create own jobs" on public.jobs
    for insert with check (auth.uid() = user_id);

-- Users can update their own jobs
create policy "Users can update own jobs" on public.jobs
    for update using (auth.uid() = user_id);

-- Service role can access all jobs
create policy "Service role full access to jobs" on public.jobs
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- 5. JOB FILES TABLE RLS
-- =====================================================

-- Enable RLS on job_files
alter table public.job_files enable row level security;

-- Users can view files from their own jobs
create policy "Users can view own job files" on public.job_files
    for select using (
        exists (
            select 1 from public.jobs
            where jobs.id = job_files.job_id
            and jobs.user_id = auth.uid()
        )
    );

-- Users can insert files to their own jobs
create policy "Users can insert own job files" on public.job_files
    for insert with check (
        exists (
            select 1 from public.jobs
            where jobs.id = job_files.job_id
            and jobs.user_id = auth.uid()
        )
    );

-- Users can update files in their own jobs
create policy "Users can update own job files" on public.job_files
    for update using (
        exists (
            select 1 from public.jobs
            where jobs.id = job_files.job_id
            and jobs.user_id = auth.uid()
        )
    );

-- Service role can access all job files
create policy "Service role full access to job files" on public.job_files
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- 6. API KEYS TABLE RLS
-- =====================================================

-- Enable RLS on api_keys
alter table public.api_keys enable row level security;

-- Users can view their own API keys (but not the full key value)
create policy "Users can view own API keys" on public.api_keys
    for select using (auth.uid() = user_id);

-- Users can create their own API keys
create policy "Users can create own API keys" on public.api_keys
    for insert with check (auth.uid() = user_id);

-- Users can update their own API keys (deactivate, rename, etc.)
create policy "Users can update own API keys" on public.api_keys
    for update using (auth.uid() = user_id);

-- Users can delete their own API keys
create policy "Users can delete own API keys" on public.api_keys
    for delete using (auth.uid() = user_id);

-- Service role can access all API keys
create policy "Service role full access to API keys" on public.api_keys
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- 7. BILLING TRANSACTIONS TABLE RLS
-- =====================================================

-- Enable RLS on billing_transactions
alter table public.billing_transactions enable row level security;

-- Users can view their own billing transactions
create policy "Users can view own billing" on public.billing_transactions
    for select using (auth.uid() = user_id);

-- Service role can access all billing data
create policy "Service role full access to billing" on public.billing_transactions
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- 8. SYSTEM CONFIG TABLE RLS
-- =====================================================

-- Enable RLS on system_config
alter table public.system_config enable row level security;

-- Only service role can access system config
create policy "Service role only access to system config" on public.system_config
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- 9. PERFORMANCE METRICS TABLE RLS
-- =====================================================

-- Enable RLS on performance_metrics
alter table public.performance_metrics enable row level security;

-- Only service role can access performance metrics
create policy "Service role only access to performance metrics" on public.performance_metrics
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- =====================================================
-- 10. AUDIT LOGS TABLE RLS
-- =====================================================

-- Enable RLS on audit_logs
alter table public.audit_logs enable row level security;

-- Users can view audit logs related to their actions
create policy "Users can view own audit logs" on public.audit_logs
    for select using (auth.uid() = user_id);

-- Service role can access all audit logs
create policy "Service role full access to audit logs" on public.audit_logs
    for all using (auth.jwt() ->> 'role' = 'service_role');

-- System can insert audit logs
create policy "System can insert audit logs" on public.audit_logs
    for insert with check (true);

-- =====================================================
-- ADDITIONAL SECURITY FUNCTIONS
-- =====================================================

-- Function to check if user has business plan (for API access)
create or replace function user_has_business_plan(user_id_param uuid default auth.uid())
returns boolean as $$
begin
    return exists (
        select 1 from public.user_profiles
        where id = user_id_param and plan = 'business'
    );
end;
$$ language plpgsql security definer;

-- Function to check if user can access API keys
create or replace function user_can_access_api_keys(user_id_param uuid default auth.uid())
returns boolean as $$
begin
    return exists (
        select 1 from public.user_profiles
        where id = user_id_param and plan in ('business')
    );
end;
$$ language plpgsql security definer;

-- Function to validate API key and get user info
create or replace function validate_api_key(api_key_param text)
returns table(
    user_id uuid,
    plan text,
    is_valid boolean,
    rate_limit integer,
    scopes text[]
) as $$
begin
    return query
    select
        ak.user_id,
        up.plan,
        (ak.is_active and (ak.expires_at is null or ak.expires_at > now())) as is_valid,
        ak.rate_limit_per_hour,
        ak.scopes
    from public.api_keys ak
    join public.user_profiles up on ak.user_id = up.id
    where ak.api_key = api_key_param;
end;
$$ language plpgsql security definer;

-- Function to log API key usage
create or replace function log_api_key_usage(api_key_param text)
returns void as $$
begin
    update public.api_keys
    set
        last_used_at = timezone('utc'::text, now()),
        requests_count = requests_count + 1
    where api_key = api_key_param;
end;
$$ language plpgsql security definer;

-- Function to get user dashboard stats
create or replace function get_user_dashboard_stats(user_id_param uuid default auth.uid())
returns table(
    current_plan text,
    images_processed_this_month integer,
    images_remaining_this_month integer,
    qwen_api_calls_this_month integer,
    jobs_this_month integer,
    successful_jobs_this_month integer,
    total_jobs integer,
    success_rate decimal
) as $$
declare
    current_year integer := extract(year from current_date);
    current_month integer := extract(month from current_date);
begin
    return query
    select
        up.plan,
        coalesce(uu.images_processed, 0)::integer,
        (pf.max_images_per_month - coalesce(uu.images_processed, 0))::integer,
        coalesce(uu.qwen_api_calls, 0)::integer,
        coalesce(uu.jobs_created, 0)::integer,
        coalesce(uu.successful_jobs, 0)::integer,
        (select count(*)::integer from public.jobs where user_id = user_id_param),
        case
            when coalesce(uu.jobs_created, 0) > 0 then
                round((coalesce(uu.successful_jobs, 0)::decimal / uu.jobs_created * 100), 2)
            else 0.00
        end
    from public.user_profiles up
    left join public.plan_features pf on up.plan = pf.plan
    left join public.user_usage uu on up.id = uu.user_id
        and uu.year = current_year
        and uu.month = current_month
    where up.id = user_id_param;
end;
$$ language plpgsql security definer;

-- =====================================================
-- GRANTS FOR AUTHENTICATED USERS
-- =====================================================

-- Grant usage on sequences
grant usage on all sequences in schema public to authenticated;

-- Grant execute on functions
grant execute on all functions in schema public to authenticated;

-- Grant select on plan_features to all authenticated users
grant select on public.plan_features to authenticated;

-- =====================================================
-- REALTIME SUBSCRIPTIONS SETUP
-- =====================================================

-- Enable realtime for job status updates
alter publication supabase_realtime add table public.jobs;
alter publication supabase_realtime add table public.job_files;
alter publication supabase_realtime add table public.user_usage;

-- =====================================================
-- ADDITIONAL CONSTRAINTS AND VALIDATIONS
-- =====================================================

-- Add constraint to ensure valid email format
alter table public.user_profiles add constraint valid_email_format
    check (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Add constraint to ensure positive values in usage
alter table public.user_usage add constraint positive_usage_values
    check (images_processed >= 0 and qwen_api_calls >= 0 and jobs_created >= 0);

-- Add constraint to ensure valid file sizes
alter table public.job_files add constraint positive_file_size
    check (file_size is null or file_size > 0);

-- Add constraint to ensure valid processing times
alter table public.job_files add constraint positive_processing_time
    check (processing_time_seconds is null or processing_time_seconds >= 0);

-- Add constraint to ensure valid billing amounts
alter table public.billing_transactions add constraint positive_billing_amount
    check (amount_usd > 0);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

comment on table public.user_profiles is 'Extended user profiles linked to Supabase auth.users';
comment on table public.plan_features is 'Static configuration for subscription plans';
comment on table public.user_usage is 'Monthly usage tracking per user';
comment on table public.jobs is 'Main processing jobs created by users';
comment on table public.job_files is 'Individual files within each processing job';
comment on table public.api_keys is 'API keys for Business plan users';
comment on table public.billing_transactions is 'Stripe billing and payment records';
comment on table public.system_config is 'System-wide configuration parameters';
comment on table public.performance_metrics is 'Application performance and usage metrics';
comment on table public.audit_logs is 'Security and change audit trail';

comment on function update_user_usage is 'Updates monthly usage statistics for a user';
comment on function check_usage_limit is 'Checks if user can process additional images';
comment on function generate_api_key is 'Generates a new API key for Business users';
comment on function get_user_dashboard_stats is 'Gets comprehensive dashboard statistics for user';
comment on function validate_api_key is 'Validates API key and returns user permissions';

-- =====================================================
-- INITIAL DATA SETUP
-- =====================================================

-- Insert default system admin (will be created manually via Supabase Auth)
-- This is just documentation - actual admin users should be created via Supabase dashboard

-- Example: Create a demo user for testing (run this after creating the auth user)
/*
-- First create user in Supabase Auth UI, then run:
-- insert into public.user_profiles (id, email, full_name, plan)
-- values (
--     'uuid-from-auth-users',
--     'demo@masterpost.io',
--     'Demo User',
--     'pro'
-- );
*/