'use client';

import { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

export default function PaymentSuccessPage() {
  const searchParams = useSearchParams();
  const [email, setEmail] = useState<string>('user@example.com');
  const [isFree, setIsFree] = useState<boolean>(false);
  const hasCaptured = useRef(false);

  useEffect(() => {
    const emailParam = searchParams.get('email');
    const planParam = searchParams.get('plan');
    const paymentId = searchParams.get('paymentId');
    const payerId = searchParams.get('PayerID');
    const transactionId = searchParams.get('transaction_id'); // Paddle transaction ID

    if (emailParam) {
      setEmail(emailParam);
    }

    if (planParam === 'free') {
      setIsFree(true);
    }

    // Paddle payment - just show success (webhook handles credit assignment)
    if (transactionId) {
      console.log('Paddle payment completed:', transactionId);
      // Credits are assigned via webhook, no additional action needed here
    }

    // Capturar pago de PayPal si los parámetros están presentes
    if (paymentId && payerId && !hasCaptured.current) {
      hasCaptured.current = true; // Marcar como capturado antes de la llamada

      fetch('/api/v1/paypal/capture-order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_id: paymentId, payer_id: payerId })
      })
      .then(res => res.json())
      .then(data => {
        console.log('Payment captured successfully:', data);
        if (data.email) {
          setEmail(data.email);
        }
      })
      .catch(err => {
        console.error('PayPal capture error:', err);
        // Permitir reintentar en caso de error
        hasCaptured.current = false;
      });
    }
  }, [searchParams]);

  return (
    <>
      <style jsx global>{`
        /* Custom scrollbar for cleaner look */
        ::-webkit-scrollbar {
          width: 8px;
        }
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        ::-webkit-scrollbar-thumb {
          background: #52B788;
          border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: #40916C;
        }
      `}</style>

      <div className="bg-gray-50 font-display text-slate-900 transition-colors duration-300 min-h-screen flex flex-col">
        {/* Top Navbar - Green Gradient */}
        <header className="w-full bg-gradient-to-r from-green-500 to-green-600 shadow-lg sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <Link href="/" className="flex-shrink-0 flex items-center gap-2 cursor-pointer hover:opacity-90 transition-opacity">
                <img
                  src="/logo-masterpost.png"
                  alt="Masterpost.io"
                  className="w-10 h-10 rounded-lg"
                />
                <span className="font-bold text-xl tracking-tight text-white">
                  Masterpost.io
                </span>
              </Link>
              {/* Optional Right Menu */}
              <div className="flex space-x-4 text-sm font-medium text-white/90">
                <a href="mailto:support@masterpost.io" className="hover:text-white transition-colors">
                  Help
                </a>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
          {/* Decorative Background Elements - Green/Yellow */}
          <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-green-500/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-yellow-400/10 rounded-full blur-3xl"></div>
            <div className="absolute top-[20%] right-[-5%] w-[20%] h-[20%] bg-green-400/5 rounded-full blur-2xl"></div>
          </div>

          <div className="max-w-xl w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl border border-gray-100 animate-fade-up">
            {/* Hero / Success Icon - Green/White */}
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-white shadow-xl mb-6 animate-pop-in border-4 border-green-500">
                <span className="material-symbols-outlined text-6xl text-green-500 font-bold" style={{ fontVariationSettings: "'wght' 700" }}>
                  check
                </span>
              </div>
              <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl mb-3">
                <span className="bg-gradient-to-r from-green-600 to-green-500 bg-clip-text text-transparent">
                  {isFree ? 'Welcome to Your Free Trial!' : 'Payment Successful!'}
                </span>
              </h1>
              <p className="text-lg text-gray-700">
                {isFree
                  ? 'You now have 10 free credits ready to use!'
                  : 'Thanks for your purchase. Your credits have been added to your account.'
                }
              </p>
            </div>

            {/* Instruction Card - Yellow Border + Soft Background */}
            <div className="bg-gradient-to-r from-yellow-50 via-green-50 to-yellow-50 border-l-4 border-yellow-400 rounded-xl p-6 flex items-start gap-4 shadow-md hover:shadow-lg transition-all duration-300">
              <div className="flex-shrink-0">
                <div className="h-12 w-12 rounded-full bg-white flex items-center justify-center text-green-600 shadow-sm">
                  <span className="material-symbols-outlined text-2xl">mail</span>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-gray-900 mb-1">
                  📧 {isFree ? 'Check your email for your access code' : 'We\'ve sent an access code to you'}
                </h3>
                <p className="text-sm text-gray-700 mb-2">
                  Please check your inbox at <span className="font-semibold text-green-700">{email}</span>.
                </p>
                <p className="text-xs text-gray-600 flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px] text-yellow-600">info</span>
                  Don't see it? Check your spam folder.
                </p>
              </div>
            </div>

            {/* Next Steps */}
            <div className="border-t border-gray-100 pt-6">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Next Steps</h3>
              <nav aria-label="Progress">
                <ol className="overflow-hidden" role="list">
                  {/* Step 1 - COMPLETADO (Verde) */}
                  <li className="relative pb-8">
                    <div aria-hidden="true" className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-green-300"></div>
                    <div className="relative flex items-start bg-green-50 rounded-lg p-3 -ml-2 border-l-2 border-green-500">
                      <span className="h-9 flex items-center">
                        <span className="relative z-10 w-10 h-10 flex items-center justify-center bg-green-500 rounded-full shadow-md">
                          <span className="material-symbols-outlined text-white text-lg font-bold">check</span>
                        </span>
                      </span>
                      <span className="ml-4 min-w-0 flex flex-col">
                        <span className="text-sm font-bold text-green-700 tracking-wide">
                          ✓ {isFree ? 'Free trial activated' : 'Payment completed'}
                        </span>
                        <span className="text-sm text-green-600">
                          Email sent to {email}
                        </span>
                      </span>
                    </div>
                  </li>

                  {/* Step 2 - Green Outline */}
                  <li className="relative pb-8 group">
                    <div aria-hidden="true" className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"></div>
                    <div className="relative flex items-start group">
                      <span className="h-9 flex items-center">
                        <span className="relative z-10 w-10 h-10 flex items-center justify-center bg-white border-[3px] border-green-400 rounded-full shadow-sm group-hover:bg-green-50 group-hover:border-green-500 transition-all">
                          <span className="text-sm font-bold text-green-600">2</span>
                        </span>
                      </span>
                      <span className="ml-4 min-w-0 flex flex-col">
                        <span className="text-sm font-semibold text-gray-700 group-hover:text-green-700 transition-colors">
                          Copy your access code
                        </span>
                        <span className="text-sm text-gray-500">
                          You'll need this to activate your credits
                        </span>
                      </span>
                    </div>
                  </li>

                  {/* Step 3 - Green Outline */}
                  <li className="relative group">
                    <div className="relative flex items-start group">
                      <span className="h-9 flex items-center">
                        <span className="relative z-10 w-10 h-10 flex items-center justify-center bg-white border-[3px] border-green-400 rounded-full shadow-sm group-hover:bg-green-50 group-hover:border-green-500 transition-all">
                          <span className="text-sm font-bold text-green-600">3</span>
                        </span>
                      </span>
                      <span className="ml-4 min-w-0 flex flex-col">
                        <span className="text-sm font-semibold text-gray-700 group-hover:text-green-700 transition-colors">
                          Login and start processing
                        </span>
                        <span className="text-sm text-gray-500">
                          Access your dashboard to begin
                        </span>
                      </span>
                    </div>
                  </li>
                </ol>
              </nav>
            </div>

            {/* Action Area */}
            <div className="flex flex-col gap-4 pt-2">
              <Link
                href="/login"
                className="group w-full flex justify-center py-4 px-6 border border-transparent rounded-xl shadow-lg text-base font-bold text-white bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-4 focus:ring-green-300 transition-all duration-200 transform hover:-translate-y-1 hover:shadow-xl"
              >
                Login & Start Processing
                <span className="material-symbols-outlined ml-2 group-hover:translate-x-1 transition-transform">
                  arrow_forward
                </span>
              </Link>
              <div className="text-center">
                <a
                  href="mailto:support@masterpost.io"
                  className="font-medium text-gray-600 hover:text-green-600 text-sm transition-colors flex items-center justify-center gap-1"
                >
                  <span className="material-symbols-outlined text-sm">headset_mic</span>
                  Need help? Contact support
                </a>
              </div>
            </div>
          </div>
        </main>

        {/* Footer - Green/Yellow Accents */}
        <footer className="bg-gray-50 border-t border-gray-200">
          <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <img
                src="/logo-masterpost.png"
                alt="Masterpost.io"
                className="w-6 h-6 opacity-80 hover:opacity-100 transition-opacity"
              />
              <span className="text-sm text-gray-600 font-medium">
                © 2025 Masterpost.io
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <a href="#" className="text-sm text-gray-500 hover:text-green-600 transition-colors">
                Documentation
              </a>
              <span className="text-yellow-400">•</span>
              <a href="#" className="text-sm text-gray-500 hover:text-green-600 transition-colors">
                FAQ
              </a>
              <span className="text-yellow-400">•</span>
              <a href="mailto:support@masterpost.io" className="text-sm text-gray-500 hover:text-green-600 transition-colors">
                Privacy
              </a>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
