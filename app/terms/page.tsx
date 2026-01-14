import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">M</span>
            </div>
            <span className="text-xl font-bold text-gray-900">Masterpost.io</span>
          </Link>
          <Link href="/">
            <Button variant="outline" size="sm">Back to Home</Button>
          </Link>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-16 max-w-4xl">
        <div className="bg-white rounded-2xl shadow-lg p-8 md:p-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
          <p className="text-sm text-gray-500 mb-8">Effective Date: January 1, 2026</p>

          <div className="prose prose-gray max-w-none space-y-8">
            {/* 1. Introduction */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Introduction</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                Welcome to Masterpost.io, an automated image processing service operated by Neuracoder.
                By accessing or using our service, you agree to be bound by these Terms of Service.
              </p>
              <p className="text-gray-700 leading-relaxed">
                If you do not agree with any part of these terms, you may not use our service.
              </p>
            </section>

            {/* 2. Service Description */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Service Description</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                Masterpost.io provides automated image processing services specifically designed for e-commerce sellers, including:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Automated background removal using AI technology</li>
                <li>Amazon and eBay compliance formatting</li>
                <li>Image optimization for online marketplaces</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                Our service operates on a credit-based system where <strong>1 credit = 1 basic image</strong> (local processing)
                and <strong>3 credits = 1 premium image</strong> (advanced Qwen AI processing).
              </p>
            </section>

            {/* 3. User Accounts */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. User Accounts</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Accounts are created using your email address and a secure access code</li>
                <li>You are responsible for keeping your access code confidential</li>
                <li>One account per email address is permitted</li>
                <li>You must provide accurate and current information</li>
                <li>You are responsible for all activities that occur under your account</li>
              </ul>
            </section>

            {/* 4. Credits and Payments */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Credits and Payments</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>Credits never expire</strong> - use them at your own pace</li>
                <li>All payments are processed securely through <strong>Paddle</strong>, our Merchant of Record</li>
                <li>Prices are listed in <strong>USD</strong></li>
                <li>Credits are <strong>non-transferable</strong> between accounts</li>
                <li>Credits are <strong>non-refundable</strong> once used (see our Refund Policy for unused credits)</li>
                <li>We reserve the right to change pricing with 30 days notice</li>
              </ul>
            </section>

            {/* 5. Acceptable Use */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Acceptable Use</h2>
              <p className="text-gray-700 leading-relaxed mb-3">You agree NOT to:</p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Upload illegal, offensive, or harmful content</li>
                <li>Process copyrighted images you do not own or have permission to use</li>
                <li>Use the service for fraudulent or abusive purposes</li>
                <li>Attempt to reverse-engineer, hack, or compromise our systems</li>
                <li>Resell or redistribute our service without authorization</li>
                <li>Use automated tools to abuse our free trial system</li>
              </ul>
            </section>

            {/* 6. Service Limitations */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Service Limitations</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                Please understand the following limitations:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Images are processed "as-is" using AI technology</li>
                <li>We do not guarantee 100% perfect results for all images</li>
                <li>Complex images may require manual adjustments after processing</li>
                <li>Service is provided "as available" and may experience downtime</li>
                <li>Processing times may vary based on server load</li>
                <li>We reserve the right to limit file sizes and quantities</li>
              </ul>
            </section>

            {/* 7. Intellectual Property */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Intellectual Property</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>You retain full ownership</strong> of all images you upload</li>
                <li>We do not claim any rights to your processed images</li>
                <li>By uploading, you grant us a temporary license to process your images</li>
                <li>This license terminates when your images are deleted (within 24 hours)</li>
                <li>Our brand, logo, and service remain our intellectual property</li>
              </ul>
            </section>

            {/* 8. Termination */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Termination</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>We may terminate accounts for violations of these terms</li>
                <li>You may delete your account at any time by contacting us</li>
                <li>Unused credits will be handled according to our Refund Policy</li>
                <li>Termination does not excuse payment for services already rendered</li>
              </ul>
            </section>

            {/* 9. Limitation of Liability */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Limitation of Liability</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                To the fullest extent permitted by law:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>The service is provided "AS IS" without warranties of any kind</li>
                <li>We are not liable for any business losses, lost profits, or indirect damages</li>
                <li>Our total liability is limited to the amount you paid in the last 12 months</li>
                <li>We are not responsible for how you use the processed images</li>
                <li>You agree to indemnify us against claims arising from your use of the service</li>
              </ul>
            </section>

            {/* 10. Governing Law */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Governing Law</h2>
              <p className="text-gray-700 leading-relaxed">
                These terms shall be governed by and construed in accordance with international commercial law.
                Any disputes shall be resolved through good faith negotiation or binding arbitration.
              </p>
            </section>

            {/* 11. Changes to Terms */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Changes to Terms</h2>
              <p className="text-gray-700 leading-relaxed">
                We may update these Terms of Service from time to time. Material changes will be notified
                via email. Continued use of the service after changes constitutes acceptance of the new terms.
              </p>
            </section>

            {/* 12. Contact */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Contact Information</h2>
              <p className="text-gray-700 leading-relaxed">
                For questions about these Terms of Service, please contact us at:
              </p>
              <p className="text-gray-700 font-semibold mt-2">
                📧 <a href="mailto:support@masterpost.io" className="text-green-600 hover:text-green-700">support@masterpost.io</a>
              </p>
            </section>
          </div>

          {/* Back to Home */}
          <div className="mt-12 pt-8 border-t border-gray-200 text-center">
            <Link href="/">
              <Button className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white">
                Back to Masterpost.io
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-gray-600">
              © 2026 Masterpost.io by Neuracoder. All rights reserved.
            </p>
            <div className="flex space-x-6 text-sm">
              <Link href="/terms" className="text-gray-600 hover:text-green-600 transition-colors">
                Terms of Service
              </Link>
              <Link href="/privacy" className="text-gray-600 hover:text-green-600 transition-colors">
                Privacy Policy
              </Link>
              <Link href="/refund" className="text-gray-600 hover:text-green-600 transition-colors">
                Refund Policy
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
