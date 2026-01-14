-- ============================================
-- MASTERPOST.IO - SUPABASE DATABASE SETUP
-- ============================================

-- 1. Tabla: user_credits
-- Almacena el balance de créditos de cada usuario
CREATE TABLE IF NOT EXISTS user_credits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  credits INTEGER DEFAULT 10 CHECK (credits >= 0),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Índice para búsquedas rápidas por user_id
CREATE INDEX IF NOT EXISTS idx_user_credits_user_id ON user_credits(user_id);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para actualizar updated_at en cada UPDATE
DROP TRIGGER IF EXISTS update_user_credits_updated_at ON user_credits;
CREATE TRIGGER update_user_credits_updated_at
  BEFORE UPDATE ON user_credits
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 2. Tabla: transactions
-- Historial de todas las transacciones de créditos
CREATE TABLE IF NOT EXISTS transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL CHECK (type IN ('free_pack', 'purchase', 'usage_basic', 'usage_premium')),
  credits_change INTEGER NOT NULL,
  credits_after INTEGER NOT NULL CHECK (credits_after >= 0),
  description TEXT,
  stripe_payment_intent_id VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para búsquedas eficientes
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);

-- 3. Tabla: stripe_customers
-- Mapeo entre usuarios de Supabase y customers de Stripe
CREATE TABLE IF NOT EXISTS stripe_customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  stripe_customer_id VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_stripe_customers_user_id ON stripe_customers(user_id);
CREATE INDEX IF NOT EXISTS idx_stripe_customers_stripe_id ON stripe_customers(stripe_customer_id);

-- ============================================
-- POLÍTICAS DE SEGURIDAD (RLS - Row Level Security)
-- ============================================

-- Habilitar RLS en todas las tablas
ALTER TABLE user_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE stripe_customers ENABLE ROW LEVEL SECURITY;

-- Políticas para user_credits
-- Los usuarios solo pueden ver sus propios créditos
DROP POLICY IF EXISTS "Users can view own credits" ON user_credits;
CREATE POLICY "Users can view own credits"
  ON user_credits FOR SELECT
  USING (auth.uid() = user_id);

-- Políticas para transactions
-- Los usuarios solo pueden ver su propio historial
DROP POLICY IF EXISTS "Users can view own transactions" ON transactions;
CREATE POLICY "Users can view own transactions"
  ON transactions FOR SELECT
  USING (auth.uid() = user_id);

-- Políticas para stripe_customers
-- Los usuarios solo pueden ver su propia info de Stripe
DROP POLICY IF EXISTS "Users can view own stripe info" ON stripe_customers;
CREATE POLICY "Users can view own stripe info"
  ON stripe_customers FOR SELECT
  USING (auth.uid() = user_id);

-- ============================================
-- FUNCIONES AUXILIARES
-- ============================================

-- Función para obtener el balance de créditos de un usuario
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

-- Función para usar créditos (con validación)
CREATE OR REPLACE FUNCTION use_credits(
  p_user_id UUID,
  p_credits_needed INTEGER,
  p_transaction_type VARCHAR(50),
  p_description TEXT
)
RETURNS JSON AS $$
DECLARE
  v_current_credits INTEGER;
  v_new_credits INTEGER;
  v_result JSON;
BEGIN
  -- Obtener créditos actuales
  SELECT credits INTO v_current_credits
  FROM user_credits
  WHERE user_id = p_user_id
  FOR UPDATE; -- Lock para evitar race conditions

  -- Verificar si tiene suficientes créditos
  IF v_current_credits < p_credits_needed THEN
    RETURN json_build_object(
      'success', false,
      'error', 'Insufficient credits',
      'current_credits', v_current_credits,
      'needed', p_credits_needed
    );
  END IF;

  -- Calcular nuevos créditos
  v_new_credits := v_current_credits - p_credits_needed;

  -- Actualizar créditos
  UPDATE user_credits
  SET credits = v_new_credits,
      updated_at = NOW()
  WHERE user_id = p_user_id;

  -- Registrar transacción
  INSERT INTO transactions (
    user_id,
    type,
    credits_change,
    credits_after,
    description
  ) VALUES (
    p_user_id,
    p_transaction_type,
    -p_credits_needed,
    v_new_credits,
    p_description
  );

  -- Retornar resultado
  RETURN json_build_object(
    'success', true,
    'credits_used', p_credits_needed,
    'credits_remaining', v_new_credits
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para agregar créditos (compras)
CREATE OR REPLACE FUNCTION add_credits(
  p_user_id UUID,
  p_credits_amount INTEGER,
  p_description TEXT,
  p_stripe_payment_intent_id VARCHAR(255) DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
  v_current_credits INTEGER;
  v_new_credits INTEGER;
BEGIN
  -- Obtener créditos actuales
  SELECT credits INTO v_current_credits
  FROM user_credits
  WHERE user_id = p_user_id
  FOR UPDATE;

  -- Calcular nuevos créditos
  v_new_credits := COALESCE(v_current_credits, 0) + p_credits_amount;

  -- Actualizar o insertar créditos
  INSERT INTO user_credits (user_id, credits)
  VALUES (p_user_id, v_new_credits)
  ON CONFLICT (user_id)
  DO UPDATE SET
    credits = v_new_credits,
    updated_at = NOW();

  -- Registrar transacción
  INSERT INTO transactions (
    user_id,
    type,
    credits_change,
    credits_after,
    description,
    stripe_payment_intent_id
  ) VALUES (
    p_user_id,
    'purchase',
    p_credits_amount,
    v_new_credits,
    p_description,
    p_stripe_payment_intent_id
  );

  -- Retornar resultado
  RETURN json_build_object(
    'success', true,
    'credits_added', p_credits_amount,
    'credits_total', v_new_credits
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- DATOS INICIALES / CONFIGURACIÓN
-- ============================================

-- Comentarios en las tablas
COMMENT ON TABLE user_credits IS 'Almacena el balance de créditos de cada usuario';
COMMENT ON TABLE transactions IS 'Historial completo de transacciones de créditos (compras y usos)';
COMMENT ON TABLE stripe_customers IS 'Mapeo entre usuarios de Supabase Auth y customers de Stripe';

COMMENT ON COLUMN user_credits.credits IS 'Balance actual de créditos del usuario';
COMMENT ON COLUMN transactions.type IS 'Tipo: free_pack, purchase, usage_basic, usage_premium';
COMMENT ON COLUMN transactions.credits_change IS 'Cambio en créditos: positivo para compras, negativo para uso';

-- ============================================
-- VERIFICACIÓN
-- ============================================

-- Ver todas las tablas creadas
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('user_credits', 'transactions', 'stripe_customers');

-- Ver políticas RLS
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename IN ('user_credits', 'transactions', 'stripe_customers');

-- ============================================
-- INSTRUCCIONES DE USO
-- ============================================

/*
INSTRUCCIONES PARA EJECUTAR ESTE SCRIPT:

1. Ve a tu proyecto en Supabase: https://supabase.com/dashboard
2. Navega a: SQL Editor (icono de base de datos en la barra lateral)
3. Click en "New Query"
4. Copia y pega TODO este archivo
5. Click en "Run" (o presiona Ctrl+Enter)
6. Verifica que todas las tablas se crearon correctamente en "Table Editor"

TESTING:
-- Ver créditos de un usuario
SELECT * FROM user_credits WHERE user_id = 'tu-user-id';

-- Ver historial de transacciones
SELECT * FROM transactions WHERE user_id = 'tu-user-id' ORDER BY created_at DESC;

-- Usar función para obtener créditos
SELECT get_user_credits('tu-user-id');
*/
