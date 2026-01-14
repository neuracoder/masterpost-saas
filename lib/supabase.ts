import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { createClient } from '@supabase/supabase-js'

// Client-side Supabase client (for components)
export const supabase = createClientComponentClient()

// Direct client for non-component usage (if needed, though createClientComponentClient is preferred in Next.js app dir)
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

export const supabaseClient = createClient(supabaseUrl, supabaseAnonKey)
