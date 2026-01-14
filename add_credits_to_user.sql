-- =====================================================
-- ADD CREDITS TO USER
-- Execute this in Supabase SQL Editor
-- =====================================================

-- Step 1: Check if user exists in auth.users
SELECT id, email, created_at
FROM auth.users
WHERE id = '48beba84-bbe5-493b-906d-b98790951d9d';

-- Step 2: Insert or update user credits (give 1000 credits)
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

-- Step 3: Verify credits were added
SELECT user_id, credits, created_at, updated_at
FROM public.user_credits
WHERE user_id = '48beba84-bbe5-493b-906d-b98790951d9d';

-- Step 4: Test the RPC function
SELECT get_user_credits('48beba84-bbe5-493b-906d-b98790951d9d');

-- Expected result: 1000
