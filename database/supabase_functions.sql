-- MASTERPOST.IO V2.0 - DATABASE FUNCTIONS
-- Execute this AFTER running schema_clean.sql and rls_clean.sql

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_usage_updated_at
    BEFORE UPDATE ON public.user_usage
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON public.jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_files_updated_at
    BEFORE UPDATE ON public.job_files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_billing_transactions_updated_at
    BEFORE UPDATE ON public.billing_transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at
    BEFORE UPDATE ON public.system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create user profile when auth user is created
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'full_name', ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Function to update user usage statistics
CREATE OR REPLACE FUNCTION update_user_usage(
    p_user_id uuid,
    p_images_count integer DEFAULT 1,
    p_qwen_calls integer DEFAULT 0,
    p_job_success boolean DEFAULT true
) RETURNS VOID AS $$
DECLARE
    current_year integer := EXTRACT(YEAR FROM CURRENT_DATE);
    current_month integer := EXTRACT(MONTH FROM CURRENT_DATE);
BEGIN
    INSERT INTO public.user_usage (
        user_id, year, month, images_processed, qwen_api_calls,
        jobs_created, successful_jobs, failed_jobs
    )
    VALUES (
        p_user_id, current_year, current_month, p_images_count, p_qwen_calls,
        1, CASE WHEN p_job_success THEN 1 ELSE 0 END, CASE WHEN p_job_success THEN 0 ELSE 1 END
    )
    ON CONFLICT (user_id, year, month)
    DO UPDATE SET
        images_processed = user_usage.images_processed + p_images_count,
        qwen_api_calls = user_usage.qwen_api_calls + p_qwen_calls,
        jobs_created = user_usage.jobs_created + 1,
        successful_jobs = user_usage.successful_jobs + CASE WHEN p_job_success THEN 1 ELSE 0 END,
        failed_jobs = user_usage.failed_jobs + CASE WHEN p_job_success THEN 0 ELSE 1 END,
        updated_at = timezone('utc'::text, now());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check usage limits
CREATE OR REPLACE FUNCTION check_usage_limit(p_user_id uuid, p_images_count integer DEFAULT 1)
RETURNS TABLE(
    can_process boolean,
    remaining_images integer,
    plan_limit integer,
    current_usage integer,
    user_plan text
) AS $$
DECLARE
    user_plan_val text;
    plan_limit_val integer;
    current_usage_val integer;
    current_year integer := EXTRACT(YEAR FROM CURRENT_DATE);
    current_month integer := EXTRACT(MONTH FROM CURRENT_DATE);
BEGIN
    -- Get user plan
    SELECT plan INTO user_plan_val FROM public.user_profiles WHERE id = p_user_id;

    IF user_plan_val IS NULL THEN
        user_plan_val := 'free';
    END IF;

    -- Get plan limit
    SELECT max_images_per_month INTO plan_limit_val
    FROM public.plan_features WHERE plan = user_plan_val;

    -- Get current usage
    SELECT COALESCE(images_processed, 0) INTO current_usage_val
    FROM public.user_usage
    WHERE user_id = p_user_id AND year = current_year AND month = current_month;

    IF current_usage_val IS NULL THEN
        current_usage_val := 0;
    END IF;

    -- Return results
    RETURN QUERY SELECT
        (current_usage_val + p_images_count <= plan_limit_val) AS can_process,
        (plan_limit_val - current_usage_val) AS remaining_images,
        plan_limit_val AS plan_limit,
        current_usage_val AS current_usage,
        user_plan_val AS user_plan;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to generate API key
CREATE OR REPLACE FUNCTION generate_api_key(p_user_id uuid, p_key_name text)
RETURNS text AS $$
DECLARE
    api_key_val text;
    key_prefix_val text;
BEGIN
    -- Generate API key (mp_ prefix + 32 random characters)
    api_key_val := 'mp_' || encode(gen_random_bytes(24), 'base64');
    api_key_val := replace(replace(api_key_val, '/', '_'), '+', '-');
    key_prefix_val := substring(api_key_val FROM 1 FOR 8);

    -- Insert API key
    INSERT INTO public.api_keys (user_id, key_name, api_key, key_prefix)
    VALUES (p_user_id, p_key_name, api_key_val, key_prefix_val);

    RETURN api_key_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate API key and get user info
CREATE OR REPLACE FUNCTION validate_api_key(api_key_param text)
RETURNS TABLE(
    user_id uuid,
    plan text,
    is_valid boolean,
    rate_limit integer,
    scopes text[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ak.user_id,
        up.plan,
        (ak.is_active AND (ak.expires_at IS NULL OR ak.expires_at > now())) AS is_valid,
        ak.rate_limit_per_hour,
        ak.scopes
    FROM public.api_keys ak
    JOIN public.user_profiles up ON ak.user_id = up.id
    WHERE ak.api_key = api_key_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log API key usage
CREATE OR REPLACE FUNCTION log_api_key_usage(api_key_param text)
RETURNS VOID AS $$
BEGIN
    UPDATE public.api_keys
    SET
        last_used_at = timezone('utc'::text, now()),
        requests_count = requests_count + 1
    WHERE api_key = api_key_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user dashboard stats
CREATE OR REPLACE FUNCTION get_user_dashboard_stats(user_id_param uuid DEFAULT auth.uid())
RETURNS TABLE(
    current_plan text,
    images_processed_this_month integer,
    images_remaining_this_month integer,
    qwen_api_calls_this_month integer,
    jobs_this_month integer,
    successful_jobs_this_month integer,
    total_jobs integer,
    success_rate decimal
) AS $$
DECLARE
    current_year integer := EXTRACT(YEAR FROM CURRENT_DATE);
    current_month integer := EXTRACT(MONTH FROM CURRENT_DATE);
BEGIN
    RETURN QUERY
    SELECT
        up.plan,
        COALESCE(uu.images_processed, 0)::integer,
        (pf.max_images_per_month - COALESCE(uu.images_processed, 0))::integer,
        COALESCE(uu.qwen_api_calls, 0)::integer,
        COALESCE(uu.jobs_created, 0)::integer,
        COALESCE(uu.successful_jobs, 0)::integer,
        (SELECT count(*)::integer FROM public.jobs WHERE user_id = user_id_param),
        CASE
            WHEN COALESCE(uu.jobs_created, 0) > 0 THEN
                round((COALESCE(uu.successful_jobs, 0)::decimal / uu.jobs_created * 100), 2)
            ELSE 0.00
        END
    FROM public.user_profiles up
    LEFT JOIN public.plan_features pf ON up.plan = pf.plan
    LEFT JOIN public.user_usage uu ON up.id = uu.user_id
        AND uu.year = current_year
        AND uu.month = current_month
    WHERE up.id = user_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;