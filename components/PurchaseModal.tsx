'use client';

import { useState, useEffect, useRef } from 'react';
import { X, Mail, Lock, Zap, Palette, CheckCircle2, AlertCircle } from 'lucide-react';

interface PurchaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (email: string) => void;
  packageName: string;  // "Starter Pack"
  credits: number;      // 50
  price: string;        // "$6.99"
  isFree?: boolean;     // NEW: Free trial mode
}

export default function PurchaseModal({
  isOpen,
  onClose,
  onSubmit,
  packageName,
  credits,
  price,
  isFree = false,
}: PurchaseModalProps) {
  const [email, setEmail] = useState('');
  const [touched, setTouched] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isValidEmail = emailRegex.test(email);
  const showError = touched && email.length > 0 && !isValidEmail;
  const showSuccess = touched && isValidEmail;

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen]);

  // Handle ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  // Handle form submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isValidEmail) {
      onSubmit(email);
    }
  };

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      {/* Backdrop with enhanced glass/blur effect */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-lg" />

      {/* Modal Card */}
      <div
        className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-gray-100 animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Header */}
          <div className="text-center space-y-3">
            {/* Logo */}
            <div className="flex justify-center">
              <img
                src="/logo-masterpost.png"
                alt="Masterpost.io"
                className="w-14 h-14 mb-2"
              />
            </div>

            {/* Title */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-1.5">
                {isFree ? 'Get Started with Free Credits!' : 'Complete Your Purchase'}
              </h2>
              <p className="text-base text-gray-600">
                {packageName} - <span className="font-semibold">{credits} Credits</span>
              </p>
              <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent mt-1.5">
                {price}
              </p>
            </div>
          </div>

          {/* Email Form */}
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-semibold text-gray-700 mb-1.5"
              >
                Your email address
              </label>
              <div className="relative">
                {/* Email Icon */}
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>

                {/* Input */}
                <input
                  ref={inputRef}
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onBlur={() => setTouched(true)}
                  placeholder="you@example.com"
                  className={`
                    block w-full pl-10 pr-10 py-2.5 border rounded-lg
                    focus:outline-none focus:ring-2 transition-colors
                    ${showError ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : ''}
                    ${showSuccess ? 'border-green-500 focus:ring-green-500 focus:border-green-500' : ''}
                    ${!showError && !showSuccess ? 'border-gray-300 focus:ring-purple-500 focus:border-purple-500' : ''}
                  `}
                />

                {/* Validation Icons */}
                {showSuccess && (
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                  </div>
                )}
                {showError && (
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  </div>
                )}
              </div>

              {/* Error Message */}
              {showError && (
                <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />
                  Please enter a valid email
                </p>
              )}
            </div>

            {/* What Happens Next Section */}
            <div className="bg-purple-50 border border-purple-100 rounded-xl p-4">
              <h3 className="text-sm font-bold text-gray-900 mb-2.5 flex items-center gap-2">
                <span className="text-base">📧</span>
                What happens next:
              </h3>
              <ol className="space-y-2">
                <li className="flex items-start gap-3 text-sm text-gray-700">
                  <span className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-xs font-bold">
                    1
                  </span>
                  <span>
                    <strong className="font-semibold">Enter your email</strong> above
                  </span>
                </li>
                {!isFree && (
                  <li className="flex items-start gap-3 text-sm text-gray-700">
                    <span className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-xs font-bold">
                      2
                    </span>
                    <span>
                      <strong className="font-semibold">Complete payment</strong> securely 🔒
                    </span>
                  </li>
                )}
                <li className="flex items-start gap-3 text-sm text-gray-700">
                  <span className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-xs font-bold">
                    {isFree ? '2' : '3'}
                  </span>
                  <span>
                    <strong className="font-semibold">Receive your access code</strong> instantly ⚡
                  </span>
                </li>
                <li className="flex items-start gap-3 text-sm text-gray-700">
                  <span className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-xs font-bold">
                    {isFree ? '3' : '4'}
                  </span>
                  <span>
                    <strong className="font-semibold">Start processing images</strong> right away 🎨
                  </span>
                </li>
              </ol>
            </div>

            {/* Privacy Note */}
            <p className="text-xs text-gray-500 text-center flex items-center justify-center gap-1">
              <Lock className="w-3 h-3" />
              Secure checkout. We never share your email.
            </p>

            {/* Action Buttons */}
            <div className="space-y-2.5 pt-1">
              {/* Submit Button */}
              <button
                type="submit"
                disabled={!isValidEmail}
                className={`
                  w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg
                  text-base font-semibold text-white transition-all duration-200
                  ${
                    isValidEmail
                      ? 'bg-gradient-to-r from-purple-600 to-purple-800 hover:from-purple-700 hover:to-purple-900 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                      : 'bg-gray-300 cursor-not-allowed opacity-50'
                  }
                `}
              >
                {isFree ? 'Start Free Trial' : 'Continue to Checkout'}
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </button>

              {/* Cancel Link */}
              <button
                type="button"
                onClick={onClose}
                className="w-full text-center text-sm text-gray-500 hover:text-gray-900 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
