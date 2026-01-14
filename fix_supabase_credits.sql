-- =====================================================
-- FIX SUPABASE CREDIT SYSTEM
-- Execute this entire script in Supabase SQL Editor
-- =====================================================

-- Step 1: Verify user_credits table exists
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name = 'user_credits';

-- Step 2: Create or replace get_user_credits function
CREATE OR REPLACE FUNCTION get_user_credits(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
  v_credits INTEGER;
BEGIN
  SELECT credits INTO v_credits
  FROM user_credits
  WHERE user_id = p_user_id;

  RETURN COALESCE(v_credits, 0);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 3: Create or replace use_credits function
CREATE OR REPLACE FUNCTION use_credits(
  p_user_id UUID,
  p_credits_needed INTEGER,
  p_transaction_type VARCHAR(50),
  p_description TEXT
)
RETURNS TABLE(
  success BOOLEAN,
  error TEXT,
  credits_before INTEGER,
  credits_used INTEGER,
  credits_after INTEGER
) AS $$
DECLARE
  v_current_credits INTEGER;
  v_new_credits INTEGER;
BEGIN
  -- Obtener créditos actuales
  SELECT credits INTO v_current_credits
  FROM user_credits
  WHERE user_id = p_user_id
  FOR UPDATE; -- Lock para evitar race conditions

  -- Verificar si tiene suficientes créditos
  IF v_current_credits < p_credits_needed THEN
    RETURN QUERY SELECT
      false AS success,
      'Insufficient credits' AS error,
      v_current_credits AS credits_before,
      0 AS credits_used,
      v_current_credits AS credits_after;
    RETURN;
  END IF;

  -- Calcular nuevos créditos
  v_new_credits := v_current_credits - p_credits_needed;

  -- Actualizar créditos
  UPDATE user_credits
  SET credits = v_new_credits,
      updated_at = NOW()
  WHERE user_id = p_user_id;

  -- Registrar transacción
  INSERT INTO transactions (user_id, type, amount, description, created_at)
  VALUES (p_user_id, p_transaction_type, -p_credits_needed, p_description, NOW());

  RETURN QUERY SELECT
    true AS success,
    NULL::TEXT AS error,
    v_current_credits AS credits_before,
    p_credits_needed AS credits_used,
    v_new_credits AS credits_after;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 4: Create or replace add_credits function
CREATE OR REPLACE FUNCTION add_credits(
  p_user_id UUID,
  p_credits_amount INTEGER,
  p_description TEXT,
  p_stripe_payment_intent_id TEXT DEFAULT NULL
)
RETURNS TABLE(
  success BOOLEAN,
  error TEXT,
  credits_added INTEGER,
  credits_total INTEGER
) AS $$
DECLARE
  v_current_credits INTEGER;
  v_new_credits INTEGER;
BEGIN
  -- Obtener créditos actuales (o crear entrada si no existe)
  INSERT INTO user_credits (user_id, credits, created_at, updated_at)
  VALUES (p_user_id, 0, NOW(), NOW())
  ON CONFLICT (user_id) DO NOTHING;

  SELECT credits INTO v_current_credits
  FROM user_credits
  WHERE user_id = p_user_id
  FOR UPDATE;

  -- Calcular nuevos créditos
  v_new_credits := v_current_credits + p_credits_amount;

  -- Actualizar créditos
  UPDATE user_credits
  SET credits = v_new_credits,
      updated_at = NOW()
  WHERE user_id = p_user_id;

  -- Registrar transacción
  INSERT INTO transactions (user_id, type, amount, description, stripe_payment_intent_id, created_at)
  VALUES (p_user_id, 'purchase', p_credits_amount, p_description, p_stripe_payment_intent_id, NOW());

  RETURN QUERY SELECT
    true AS success,
    NULL::TEXT AS error,
    p_credits_amount AS credits_added,
    v_new_credits AS credits_total;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 5: Create trigger to give 10 credits to new users
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_credits (user_id, credits, created_at, updated_at)
  VALUES (NEW.id, 10, NOW(), NOW());

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger that fires when a new user is created
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- Step 6: Add 1000 credits to the existing authenticated user
INSERT INTO public.user_credits (user_id, credits, created_at, updated_at)
VALUES (
  '48beba84-bbe5-493b-906d-b98790951d9d',
  1000,
  NOW(),
  NOW()
)
ON CONFLICT (user_id)
DO UPDATE SET
  credits = 1000,
  updated_at = NOW();

-- Step 7: Verify everything works
SELECT 'Testing get_user_credits function:' AS test;
SELECT get_user_credits('48beba84-bbe5-493b-906d-b98790951d9d') AS user_credits;

SELECT 'Checking user_credits table:' AS test;
SELECT user_id, credits, created_at, updated_at
FROM public.user_credits
WHERE user_id = '48beba84-bbe5-493b-906d-b98790951d9d';

-- =====================================================
-- EXPECTED RESULTS:
-- - get_user_credits should return: 1000
-- - user_credits table should show: 1000 credits
-- =====================================================
