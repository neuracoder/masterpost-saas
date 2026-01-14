'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSimpleAuth } from '@/app/contexts/SimpleAuthContext';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useSimpleAuth();
  const [email, setEmail] = useState('');
  const [accessCode, setAccessCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Si ya está autenticado, redirigir al dashboard
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/app');
    }
  }, [isAuthenticated, router]);

  // Validación de formato del access code
  const isValidFormat = (code: string): boolean => {
    const regex = /^MP-[A-Z0-9]{4}-[A-Z0-9]{4}$/;
    return regex.test(code);
  };

  // Auto-format del Access Code
  const handleAccessCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');

    // Remove MP prefix if user types it
    if (value.startsWith('MP')) {
      value = value.slice(2);
    }

    // Format: MP-XXXX-XXXX
    if (value.length === 0) {
      setAccessCode('');
    } else if (value.length <= 4) {
      setAccessCode(`MP-${value}`);
    } else if (value.length <= 8) {
      setAccessCode(`MP-${value.slice(0, 4)}-${value.slice(4)}`);
    } else {
      setAccessCode(`MP-${value.slice(0, 4)}-${value.slice(4, 8)}`);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setIsLoading(true);

    try {
      const loginSuccess = await login(email, accessCode);

      if (loginSuccess) {
        setSuccess(true);
        // El redirect se manejará en el useEffect
      } else {
        setError('Invalid access code. Please verify your code and try again.');
      }
    } catch (err) {
      setError('Connection error. Please check your internet connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Si está autenticado, mostrar mensaje de carga
  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">

        {/* HEADER */}
        <div className="text-center mb-8">
          {/* Logo - Clickeable al Home */}
          <Link href="/" className="inline-block group">
            <img
              src="/logo-masterpost.png"
              alt="Masterpost.io"
              className="w-28 h-28 mx-auto mb-4 transition-transform duration-200 group-hover:scale-105 cursor-pointer"
            />
          </Link>

          {/* Título */}
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Masterpost.io
          </h1>

          {/* Tagline */}
          <p className="text-gray-600 text-sm">
            Professional Image Processing
          </p>
        </div>

        {/* CARD PRINCIPAL (Login Form) */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          {/* Título del Card */}
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <span>🎉</span> Welcome Back!
          </h2>

          {/* Success Message */}
          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-700 flex items-center gap-2">
                <span>✅</span> Login successful! Redirecting...
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700 flex items-center gap-2">
                <span>❌</span> {error}
              </p>
            </div>
          )}

          <form onSubmit={handleLogin}>
            {/* Email Field */}
            <div className="mb-4">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                <span>📧</span> Your Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                disabled={isLoading}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all outline-none disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>

            {/* Access Code Field */}
            <div className="mb-6">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
                <span>🔑</span> Access Code
              </label>
              <input
                type="text"
                value={accessCode}
                onChange={handleAccessCodeChange}
                placeholder="MP-XXXX-XXXX"
                maxLength={12}
                required
                disabled={isLoading}
                className={`w-full px-4 py-3 border-2 rounded-lg font-mono text-lg tracking-wider uppercase transition-all outline-none disabled:opacity-50 disabled:cursor-not-allowed ${
                  isValidFormat(accessCode)
                    ? 'border-green-500 focus:ring-2 focus:ring-green-200'
                    : 'border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200'
                }`}
              />
              <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                <span>✓</span> Format: MP-XXXX-XXXX (12 characters)
              </p>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={!email || !isValidFormat(accessCode) || isLoading}
              className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <span className="animate-spin">⏳</span>
                  Logging in...
                </>
              ) : (
                <>
                  Login & Start Processing
                  <span>→</span>
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 border-t border-gray-200"></div>
            <span className="text-sm text-gray-500">or</span>
            <div className="flex-1 border-t border-gray-200"></div>
          </div>

          {/* CTA Link */}
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">
              💳 Don't have credits yet?
            </p>
            <Link
              href="/"
              className="text-purple-600 hover:text-purple-700 font-semibold text-sm hover:underline"
            >
              View Pricing Plans →
            </Link>
          </div>
        </div>

        {/* INFO CARD (Ayuda) */}
        <div className="mt-6 bg-green-50 border border-green-200 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span>📧</span> Check your email
          </h3>
          <p className="text-sm text-gray-700 mb-3">
            Your access code was sent after purchase
          </p>

          <div className="space-y-2">
            <p className="text-sm font-semibold text-gray-800">
              🔍 Can't find it?
            </p>
            <ul className="text-sm text-gray-600 space-y-1 ml-4">
              <li>• Check your spam folder</li>
              <li>• Verify the email address you used</li>
              <li>
                • <a href="mailto:support@masterpost.io" className="text-purple-600 hover:text-purple-700 font-medium hover:underline">
                  Contact Support →
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* FOOTER */}
        <div className="mt-8 text-center">
          {/* Security Badges */}
          <div className="flex items-center justify-center gap-4 text-sm text-gray-600 mb-4">
            <span className="flex items-center gap-1">
              🔒 Secure Login
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              ⏰ Credits Never Expire
            </span>
          </div>

          {/* Help Links */}
          <div className="flex items-center justify-center gap-4 text-sm">
            <a href="mailto:support@masterpost.io" className="text-gray-600 hover:text-purple-600 transition-colors">
              Need Help?
            </a>
            <span className="text-gray-300">|</span>
            <a href="#" className="text-gray-600 hover:text-purple-600 transition-colors">
              FAQ
            </a>
            <span className="text-gray-300">|</span>
            <a href="mailto:support@masterpost.io" className="text-gray-600 hover:text-purple-600 transition-colors">
              Contact Support
            </a>
          </div>
        </div>

      </div>
    </div>
  );
}
