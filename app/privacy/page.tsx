import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function PrivacyPolicy() {
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
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
          <p className="text-sm text-gray-500 mb-8">Effective Date: January 1, 2026</p>

          <div className="prose prose-gray max-w-none space-y-8">
            {/* 1. Introduction */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Introduction</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                Masterpost.io, operated by Neuracoder, is committed to protecting your privacy. This Privacy Policy explains how we collect, use, store, and protect your personal information when you use our automated image processing service.
              </p>
              <p className="text-gray-700 leading-relaxed">
                By using our service, you consent to the data practices described in this policy.
              </p>
            </section>

            {/* 2. Information We Collect */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Information We Collect</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We collect the following types of information:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>Email Address:</strong> Used for account creation, authentication, and communication</li>
                <li><strong>Access Code:</strong> Unique identifier for secure login (format: MP-XXXX-XXXX)</li>
                <li><strong>Payment Information:</strong> Processed securely by Paddle (our Merchant of Record) - we do NOT store credit card details</li>
                <li><strong>Images:</strong> Photos you upload for processing (stored temporarily for 24 hours only)</li>
                <li><strong>Usage Data:</strong> Credits used, processing history, service interactions</li>
                <li><strong>Technical Data:</strong> IP address, browser type, device information for security and service improvement</li>
              </ul>
            </section>

            {/* 3. How We Use Your Information */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. How We Use Your Information</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We use your information for the following purposes:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>To provide and maintain our image processing service</li>
                <li>To authenticate users and manage accounts</li>
                <li>To process payments and manage credit balances</li>
                <li>To send service-related notifications (access codes, transaction confirmations)</li>
                <li>To improve our service and develop new features</li>
                <li>To detect and prevent fraud or abuse</li>
                <li>To comply with legal obligations</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                <strong>We will NEVER sell or rent your personal information to third parties.</strong>
              </p>
            </section>

            {/* 4. Image Processing and Storage */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Image Processing and Storage</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                Your images are handled with strict privacy controls:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>Temporary Storage:</strong> Images are stored for a maximum of 24 hours</li>
                <li><strong>Automatic Deletion:</strong> All uploaded and processed images are automatically deleted after 24 hours</li>
                <li><strong>No Training Data:</strong> Your images are NEVER used to train AI models</li>
                <li><strong>No Sharing:</strong> We do not share your images with third parties except as required for processing (Qwen AI for premium images)</li>
                <li><strong>Secure Processing:</strong> Images are processed on secure servers with encryption in transit</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                <strong>Important:</strong> Download your processed images within 24 hours or they will be permanently deleted.
              </p>
            </section>

            {/* 5. Payment Processing */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Payment Processing</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                All payment transactions are processed by <strong>Paddle</strong>, our Merchant of Record.
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Paddle handles all payment card information securely (PCI DSS compliant)</li>
                <li>We receive only transaction confirmations, not your credit card details</li>
                <li>Paddle may collect additional information for tax and compliance purposes</li>
                <li>For Paddle's privacy practices, see: <a href="https://www.paddle.com/legal/privacy" target="_blank" rel="noopener noreferrer" className="text-green-600 hover:text-green-700">Paddle Privacy Policy</a></li>
              </ul>
            </section>

            {/* 6. Data Storage and Security */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Data Storage and Security</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We implement industry-standard security measures to protect your data:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>Server Location:</strong> Data is stored on secure servers hosted by Hetzner in Germany (EU data protection laws apply)</li>
                <li><strong>Encryption:</strong> Data is encrypted in transit using HTTPS/TLS</li>
                <li><strong>Access Controls:</strong> Limited access to personal data by authorized personnel only</li>
                <li><strong>Regular Backups:</strong> Database backups are performed regularly and stored securely</li>
                <li><strong>Security Monitoring:</strong> We monitor for unauthorized access and suspicious activity</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                While we strive to protect your data, no method of transmission over the internet is 100% secure. We cannot guarantee absolute security.
              </p>
            </section>

            {/* 7. Your Rights */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Your Rights</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                You have the following rights regarding your personal data:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>Access:</strong> Request a copy of your personal data</li>
                <li><strong>Correction:</strong> Request correction of inaccurate data</li>
                <li><strong>Deletion:</strong> Request deletion of your account and personal data</li>
                <li><strong>Portability:</strong> Request your data in a machine-readable format</li>
                <li><strong>Objection:</strong> Object to certain processing of your data</li>
                <li><strong>Withdrawal:</strong> Withdraw consent at any time (may limit service availability)</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                To exercise any of these rights, contact us at <a href="mailto:support@masterpost.io" className="text-green-600 hover:text-green-700">support@masterpost.io</a>
              </p>
            </section>

            {/* 8. Cookies and Tracking */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Cookies and Tracking</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We use minimal cookies and tracking technologies:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>Essential Cookies:</strong> Required for authentication and session management</li>
                <li><strong>Analytics:</strong> We may use basic analytics to understand service usage (aggregated data only)</li>
                <li><strong>No Third-Party Advertising:</strong> We do not use cookies for advertising purposes</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                You can control cookies through your browser settings, but disabling essential cookies may limit service functionality.
              </p>
            </section>

            {/* 9. Data Retention */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Data Retention</h2>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>Account Data:</strong> Retained as long as your account is active</li>
                <li><strong>Transaction Records:</strong> Retained for 7 years for tax and legal compliance</li>
                <li><strong>Images:</strong> Automatically deleted after 24 hours</li>
                <li><strong>Logs:</strong> Technical logs retained for 90 days for security purposes</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                When you delete your account, we will delete your personal data within 30 days, except where retention is required by law.
              </p>
            </section>

            {/* 10. Third-Party Services */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Third-Party Services</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We use the following third-party services:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li><strong>Paddle:</strong> Payment processing (see their privacy policy)</li>
                <li><strong>Alibaba Cloud (Qwen AI):</strong> Premium image processing for AI-powered background removal</li>
                <li><strong>Hetzner:</strong> Server hosting in Germany</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                These services have their own privacy policies and we are not responsible for their practices.
              </p>
            </section>

            {/* 11. Children's Privacy */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Children's Privacy</h2>
              <p className="text-gray-700 leading-relaxed">
                Our service is not intended for users under 18 years of age. We do not knowingly collect personal information from children. If you believe we have collected information from a child, please contact us immediately so we can delete it.
              </p>
            </section>

            {/* 12. Changes to This Policy */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Changes to This Policy</h2>
              <p className="text-gray-700 leading-relaxed">
                We may update this Privacy Policy from time to time. Material changes will be notified via email at least 30 days before taking effect. Continued use of the service after changes constitutes acceptance of the updated policy.
              </p>
            </section>

            {/* 13. Contact Information */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">13. Contact Information</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                For questions, concerns, or to exercise your privacy rights, contact us at:
              </p>
              <p className="text-gray-700 font-semibold">
                📧 <a href="mailto:support@masterpost.io" className="text-green-600 hover:text-green-700">support@masterpost.io</a>
              </p>
              <p className="text-gray-700 mt-3">
                <strong>Data Controller:</strong> Neuracoder<br />
                <strong>Service:</strong> Masterpost.io
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
