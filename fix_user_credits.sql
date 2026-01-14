-- =====================================================
-- FIX: Dar créditos al usuario autenticado
-- Usuario ID: 48beba84-bbe5-493b-906d-b98790951d9d (del log)
-- =====================================================

-- PASO 1: Verificar si el usuario existe en user_credits
SELECT
  user_id,
  credits,
  created_at,
  updated_at
FROM public.user_credits
WHERE user_id = '48beba84-bbe5-493b-906d-b98790951d9d';

-- PASO 2: Si NO existe, crear entrada con 1000 créditos
INSERT INTO public.user_credits (user_id, credits, created_at, updated_at)
VALUES (
  '48beba84-bbe5-493b-906d-b98790951d9d',
  1000,
  NOW(),
  NOW()
)
ON CONFLICT (user_id) DO NOTHING;

-- PASO 3: Si YA existe pero tiene 0 créditos, actualizar a 1000
UPDATE public.user_credits
SET
  credits = 1000,
  updated_at = NOW()
WHERE user_id = '48beba84-bbe5-493b-906d-b98790951d9d';

-- PASO 4: Verificar que el cambio se aplicó
SELECT
  user_id,
  credits,
  created_at,
  updated_at
FROM public.user_credits
WHERE user_id = '48beba84-bbe5-493b-906d-b98790951d9d';

-- =====================================================
-- RESULTADO ESPERADO:
-- user_id                               | credits | created_at           | updated_at
-- 48beba84-bbe5-493b-906d-b98790951d9d | 1000    | 2025-XX-XX XX:XX:XX | 2025-XX-XX XX:XX:XX
-- =====================================================
