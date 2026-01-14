-- MASTERPOST.IO V2.0 - ROW LEVEL SECURITY (RLS)
-- Execute this AFTER running supabase_schema.sql

-- 1. USER PROFILES TABLE RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Service role full access to profiles" ON public.user_profiles
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 2. PLAN FEATURES TABLE RLS
ALTER TABLE public.plan_features ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read plan features" ON public.plan_features
    FOR SELECT USING (true);

CREATE POLICY "Service role can modify plan features" ON public.plan_features
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 3. USER USAGE TABLE RLS
ALTER TABLE public.user_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own usage" ON public.user_usage
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access to usage" ON public.user_usage
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "System can update usage data" ON public.user_usage
    FOR INSERT WITH CHECK (true);

CREATE POLICY "System can modify usage data" ON public.user_usage
    FOR UPDATE USING (true);

-- 4. JOBS TABLE RLS
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own jobs" ON public.jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own jobs" ON public.jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own jobs" ON public.jobs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Service role full access to jobs" ON public.jobs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 5. JOB FILES TABLE RLS
ALTER TABLE public.job_files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own job files" ON public.job_files
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.jobs
            WHERE jobs.id = job_files.job_id
            AND jobs.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert own job files" ON public.job_files
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.jobs
            WHERE jobs.id = job_files.job_id
            AND jobs.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own job files" ON public.job_files
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.jobs
            WHERE jobs.id = job_files.job_id
            AND jobs.user_id = auth.uid()
        )
    );

CREATE POLICY "Service role full access to job files" ON public.job_files
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 6. API KEYS TABLE RLS
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own API keys" ON public.api_keys
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own API keys" ON public.api_keys
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own API keys" ON public.api_keys
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own API keys" ON public.api_keys
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Service role full access to API keys" ON public.api_keys
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 7. BILLING TRANSACTIONS TABLE RLS
ALTER TABLE public.billing_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own billing" ON public.billing_transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access to billing" ON public.billing_transactions
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 8. SYSTEM CONFIG TABLE RLS
ALTER TABLE public.system_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role only access to system config" ON public.system_config
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 9. PERFORMANCE METRICS TABLE RLS
ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role only access to performance metrics" ON public.performance_metrics
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- 10. AUDIT LOGS TABLE RLS
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own audit logs" ON public.audit_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role full access to audit logs" ON public.audit_logs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "System can insert audit logs" ON public.audit_logs
    FOR INSERT WITH CHECK (true);

-- GRANTS FOR AUTHENTICATED USERS
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;
GRANT SELECT ON public.plan_features TO authenticated;

-- REALTIME SUBSCRIPTIONS SETUP
ALTER PUBLICATION supabase_realtime ADD TABLE public.jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE public.job_files;
ALTER PUBLICATION supabase_realtime ADD TABLE public.user_usage;