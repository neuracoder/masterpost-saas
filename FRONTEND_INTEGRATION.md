# 🎨 Integración del Frontend con SQLite Auth

## Resumen

El contexto de autenticación `SimpleAuthContext` ya está creado. Ahora necesitas integrarlo en tu aplicación Next.js.

---

## 📋 PASO 1: Envolver la App con el Provider

### Archivo: `app/layout.tsx` o `pages/_app.tsx`

```typescript
// app/layout.tsx (Next.js 13+ App Router)
import { SimpleAuthProvider } from '@/contexts/SimpleAuthContext';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <SimpleAuthProvider>
          {children}
        </SimpleAuthProvider>
      </body>
    </html>
  );
}
```

O si usas Pages Router:

```typescript
// pages/_app.tsx (Next.js Pages Router)
import { SimpleAuthProvider } from '@/contexts/SimpleAuthContext';
import type { AppProps } from 'next/app';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <SimpleAuthProvider>
      <Component {...pageProps} />
    </SimpleAuthProvider>
  );
}
```

---

## 📋 PASO 2: Crear Página de Login

### Archivo: `app/login/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSimpleAuth } from '@/contexts/SimpleAuthContext';

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useSimpleAuth();
  const [email, setEmail] = useState('');
  const [accessCode, setAccessCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const success = await login(email, accessCode);

    if (success) {
      router.push('/'); // Redirigir al dashboard
    } else {
      setError('Invalid email or access code');
    }

    setLoading(false);
  };

  // Si ya está autenticado, redirigir
  if (isAuthenticated) {
    router.push('/');
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div>
          <h2 className="text-3xl font-bold text-center">Masterpost.io</h2>
          <p className="mt-2 text-center text-gray-600">
            Sign in with your access code
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="accessCode" className="block text-sm font-medium text-gray-700">
              Access Code
            </label>
            <input
              id="accessCode"
              type="text"
              required
              value={accessCode}
              onChange={(e) => setAccessCode(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="MP-XXXX-XXXX"
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="text-center text-sm text-gray-600">
          <p>Don't have an access code?</p>
          <p>Contact support to get started.</p>
        </div>
      </div>
    </div>
  );
}
```

---

## 📋 PASO 3: Usar el Hook en Componentes

### Ejemplo: Header con Info de Usuario

```typescript
'use client';

import { useSimpleAuth } from '@/contexts/SimpleAuthContext';

export function Header() {
  const { email, credits, logout, isAuthenticated } = useSimpleAuth();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Masterpost.io</h1>

        <div className="flex items-center gap-4">
          <div className="text-sm">
            <p className="font-medium">{email}</p>
            <p className="text-gray-600">{credits} credits</p>
          </div>

          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
```

### Ejemplo: Protected Route

```typescript
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSimpleAuth } from '@/contexts/SimpleAuthContext';

export function ProtectedPage() {
  const router = useRouter();
  const { isAuthenticated, email, credits, refreshCredits } = useSimpleAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Welcome, {email}!</h1>
      <p>You have {credits} credits remaining.</p>
      <button onClick={refreshCredits}>Refresh Credits</button>
    </div>
  );
}
```

---

## 📋 PASO 4: Actualizar API Calls

El API client (`lib/api.ts`) ya está configurado para enviar automáticamente el header `x-user-email` desde localStorage.

### Ejemplo de Upload

```typescript
'use client';

import { useState } from 'react';
import { useSimpleAuth } from '@/contexts/SimpleAuthContext';
import { apiClient } from '@/lib/api';

export function UploadForm() {
  const { credits, refreshCredits } = useSimpleAuth();
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (files.length === 0) return;

    setLoading(true);

    // El API client automáticamente agrega el header x-user-email
    const result = await apiClient.uploadImages(files);

    if (result.error) {
      alert(`Upload failed: ${result.error}`);
    } else {
      alert(`Upload successful! Job ID: ${result.data?.job_id}`);
      // Refresh credits después del upload
      await refreshCredits();
    }

    setLoading(false);
  };

  return (
    <div>
      <p>Available credits: {credits}</p>

      <input
        type="file"
        multiple
        accept="image/*"
        onChange={(e) => setFiles(Array.from(e.target.files || []))}
      />

      <button onClick={handleUpload} disabled={loading || files.length === 0}>
        {loading ? 'Uploading...' : `Upload ${files.length} files`}
      </button>

      <p className="text-sm text-gray-600">
        Cost: {files.length} credits
      </p>
    </div>
  );
}
```

---

## 📋 PASO 5: Middleware para Rutas Protegidas (Opcional)

### Archivo: `middleware.ts` (raíz del proyecto)

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Rutas públicas
  const publicPaths = ['/login', '/'];

  if (publicPaths.includes(pathname)) {
    return NextResponse.next();
  }

  // Verificar si hay credenciales en localStorage
  // Nota: El middleware se ejecuta en el servidor, así que usamos cookies
  const email = request.cookies.get('mp_email')?.value;
  const accessCode = request.cookies.get('mp_access_code')?.value;

  if (!email || !accessCode) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/upload/:path*', '/jobs/:path*'],
};
```

**Nota**: Para que esto funcione, necesitas también guardar las credenciales en cookies además de localStorage:

```typescript
// En SimpleAuthContext.tsx, modificar la función login:
const login = async (email: string, code: string): Promise<boolean> => {
  try {
    const response = await fetch('/api/v1/auth/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, access_code: code })
    });

    if (response.ok) {
      const data = await response.json();
      setEmail(email);
      setAccessCode(code);
      setCredits(data.credits);

      // localStorage
      localStorage.setItem('mp_email', email);
      localStorage.setItem('mp_access_code', code);

      // También guardar en cookies para el middleware
      document.cookie = `mp_email=${email}; path=/; max-age=2592000`; // 30 días
      document.cookie = `mp_access_code=${code}; path=/; max-age=2592000`;

      return true;
    }
    return false;
  } catch (error) {
    console.error('Login error:', error);
    return false;
  }
};
```

---

## 📋 PASO 6: Testing del Frontend

### Test 1: Verificar Context

```bash
# En el navegador, abrir Console
localStorage.getItem('mp_email')
localStorage.getItem('mp_access_code')
```

### Test 2: Login Manual

1. Ir a `/login`
2. Ingresar:
   - Email: `demo@masterpost.io`
   - Access Code: (el que obtuviste de `python quick_start.py`)
3. Click "Sign In"
4. Deberías ser redirigido al dashboard

### Test 3: API Call

```javascript
// En el navegador Console
const result = await fetch('/api/v1/auth/credits', {
  headers: {
    'x-user-email': localStorage.getItem('mp_email')
  }
});
const data = await result.json();
console.log(data); // Debe mostrar email y créditos
```

---

## 🎨 COMPONENTES DE EJEMPLO

### Credit Badge

```typescript
'use client';

import { useSimpleAuth } from '@/contexts/SimpleAuthContext';

export function CreditBadge() {
  const { credits, refreshCredits } = useSimpleAuth();

  return (
    <div
      onClick={refreshCredits}
      className="cursor-pointer px-3 py-1 bg-blue-100 text-blue-800 rounded-full"
    >
      {credits} credits
    </div>
  );
}
```

### User Menu

```typescript
'use client';

import { useSimpleAuth } from '@/contexts/SimpleAuthContext';
import { Menu } from '@headlessui/react';

export function UserMenu() {
  const { email, credits, logout } = useSimpleAuth();

  return (
    <Menu as="div" className="relative">
      <Menu.Button className="flex items-center gap-2">
        <div className="text-right">
          <p className="text-sm font-medium">{email}</p>
          <p className="text-xs text-gray-500">{credits} credits</p>
        </div>
      </Menu.Button>

      <Menu.Items className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg">
        <Menu.Item>
          {({ active }) => (
            <button
              onClick={logout}
              className={`${
                active ? 'bg-gray-100' : ''
              } w-full text-left px-4 py-2 text-sm`}
            >
              Logout
            </button>
          )}
        </Menu.Item>
      </Menu.Items>
    </Menu>
  );
}
```

---

## ✅ CHECKLIST DE INTEGRACIÓN

- [ ] Envolver app con `SimpleAuthProvider`
- [ ] Crear página `/login`
- [ ] Actualizar componentes para usar `useSimpleAuth()`
- [ ] Agregar header con info de usuario
- [ ] Proteger rutas privadas
- [ ] Configurar middleware (opcional)
- [ ] Actualizar cookies además de localStorage
- [ ] Probar flujo completo de login
- [ ] Probar upload con header automático
- [ ] Verificar refresh de créditos

---

## 🔧 DEBUGGING

### El header `x-user-email` no se envía

**Verificar**:
```javascript
// Console del navegador
localStorage.getItem('mp_email')
```

**Solución**: Hacer login primero

### Los créditos no se actualizan

**Solución**:
```typescript
const { refreshCredits } = useSimpleAuth();
await refreshCredits();
```

### Error 401 en API calls

**Causa**: Header `x-user-email` no se envía

**Verificar**:
```javascript
// En api.ts, agregar log temporal
console.log('Email header:', email);
```

---

## 📚 API del Hook

### `useSimpleAuth()`

```typescript
interface AuthContextType {
  email: string | null;              // Email del usuario actual
  accessCode: string | null;         // Código de acceso
  credits: number;                   // Créditos disponibles
  isAuthenticated: boolean;          // ¿Está autenticado?
  login: (email, code) => Promise<boolean>;  // Función de login
  logout: () => void;                // Función de logout
  refreshCredits: () => Promise<void>;  // Refrescar créditos
}
```

### Ejemplo Completo

```typescript
const {
  email,           // "demo@masterpost.io"
  accessCode,      // "MP-XXXX-XXXX"
  credits,         // 500
  isAuthenticated, // true
  login,           // async (email, code) => boolean
  logout,          // () => void
  refreshCredits   // async () => void
} = useSimpleAuth();
```

---

**¡Listo para integrar el frontend! 🎨**

Sigue los pasos en orden y tendrás autenticación funcionando en minutos.
