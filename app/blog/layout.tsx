import type { Metadata } from "next"
import Link from "next/link"
import { Menu, X } from "lucide-react"

export const metadata: Metadata = {
  title: {
    template: '%s | Masterpost.io Blog',
    default: 'Blog - E-commerce Image Optimization Tips | Masterpost.io',
  },
  description: 'Expert tips on product photography, image optimization, and marketplace compliance for e-commerce sellers.',
}

export default function BlogLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-white">
      {/* Blog Header */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100 shadow-sm">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-2">
              <svg
                width="40"
                height="40"
                viewBox="0 0 40 40"
                xmlns="http://www.w3.org/2000/svg"
                className="flex-shrink-0 shadow-md"
              >
                <rect x="3" y="3" width="17" height="34" fill="#10b981" />
                <rect x="20" y="3" width="17" height="34" fill="#ffffff" />
                <rect x="0" y="0" width="40" height="40" rx="6" fill="none" stroke="#fbbf24" strokeWidth="3" />
                <text
                  x="20"
                  y="30"
                  fontFamily="system-ui, -apple-system, 'Segoe UI', sans-serif"
                  fontSize="28"
                  fontWeight="900"
                  fill="#fbbf24"
                  textAnchor="middle"
                  letterSpacing="-1"
                >
                  M
                </text>
              </svg>
              <span className="text-xl font-bold text-gray-900">Masterpost.io</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="/#features" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                Features
              </a>
              <Link href="/blog" className="text-green-600 font-semibold">
                Blog
              </Link>
              <Link href="/pricing" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                Pricing
              </Link>
              <a href="/#faq" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                FAQ
              </a>
            </div>

            {/* CTA Buttons */}
            <div className="hidden md:flex items-center space-x-4">
              <Link href="/login" className="text-gray-600 hover:text-green-600 transition-colors font-medium">
                Login
              </Link>
              <Link
                href="/app"
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-semibold transition-colors shadow-lg shadow-green-500/25"
              >
                Start Free
              </Link>
            </div>

            {/* Mobile Menu Button - handled by parent */}
            <button className="md:hidden text-gray-600 hover:text-green-600">
              <Menu className="w-6 h-6" />
            </button>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main>
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            {/* Brand */}
            <div className="space-y-4">
              <Link href="/" className="flex items-center space-x-2">
                <svg width="32" height="32" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="3" width="17" height="34" fill="#10b981" />
                  <rect x="20" y="3" width="17" height="34" fill="#ffffff" />
                  <rect x="0" y="0" width="40" height="40" rx="6" fill="none" stroke="#fbbf24" strokeWidth="3" />
                  <text
                    x="20"
                    y="30"
                    fontFamily="system-ui"
                    fontSize="28"
                    fontWeight="900"
                    fill="#fbbf24"
                    textAnchor="middle"
                  >
                    M
                  </text>
                </svg>
                <span className="text-xl font-bold text-white">Masterpost.io</span>
              </Link>
              <p className="text-sm text-gray-400">
                Professional e-commerce image processing powered by AI
              </p>
            </div>

            {/* Product */}
            <div className="space-y-3">
              <h3 className="text-white font-semibold">Product</h3>
              <ul className="space-y-2 text-sm">
                <li><a href="/#features" className="hover:text-green-400 transition-colors">Features</a></li>
                <li><a href="/#examples" className="hover:text-green-400 transition-colors">Examples</a></li>
                <li><Link href="/pricing" className="hover:text-green-400 transition-colors">Pricing</Link></li>
                <li><Link href="/app" className="hover:text-green-400 transition-colors">Dashboard</Link></li>
              </ul>
            </div>

            {/* Resources */}
            <div className="space-y-3">
              <h3 className="text-white font-semibold">Resources</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/blog" className="hover:text-green-400 transition-colors">Blog</Link></li>
                <li><a href="/#faq" className="hover:text-green-400 transition-colors">FAQ</a></li>
                <li><Link href="/app" className="hover:text-green-400 transition-colors">Contact</Link></li>
              </ul>
            </div>

            {/* Legal */}
            <div className="space-y-3">
              <h3 className="text-white font-semibold">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="hover:text-green-400 transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-green-400 transition-colors">Terms of Service</Link></li>
                <li><Link href="/refund" className="hover:text-green-400 transition-colors">Refund Policy</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-400">© 2026 Masterpost.io. All rights reserved.</p>
            <div className="flex items-center space-x-6">
              <a href="#" className="text-gray-400 hover:text-green-400 transition-colors">
                <span className="sr-only">Twitter</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-green-400 transition-colors">
                <span className="sr-only">LinkedIn</span>
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
