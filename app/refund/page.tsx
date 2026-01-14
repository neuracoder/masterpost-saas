import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function RefundPolicy() {
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
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Refund Policy</h1>
          <p className="text-sm text-gray-500 mb-8">Effective Date: January 1, 2026</p>

          <div className="prose prose-gray max-w-none space-y-8">
            {/* 1. Overview */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Overview</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                At Masterpost.io, we want you to be completely satisfied with our service. This Refund Policy explains when and how you can request a refund for purchased credits.
              </p>
              <p className="text-gray-700 leading-relaxed">
                All payments are processed by <strong>Paddle</strong>, our Merchant of Record, who handles refund processing according to this policy.
              </p>
            </section>

            {/* 2. Refund Eligibility */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Refund Eligibility</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                You are eligible for a full refund if you request it within <strong>14 days</strong> of purchase.
              </p>
              <p className="text-gray-700 leading-relaxed mb-3">
                <strong>Examples of Valid Reasons:</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Service did not meet your expectations</li>
                <li>Technical issues prevented you from using the service</li>
                <li>Accidental duplicate purchase</li>
                <li>Purchased wrong credit package</li>
                <li>Changed your mind about the purchase</li>
              </ul>
            </section>

            {/* 3. Non-Refundable Situations */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Non-Refundable Situations</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                Refunds will <strong>NOT</strong> be issued in the following cases:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>More than 14 days have passed since purchase</li>
                <li>Your account was terminated due to Terms of Service violations</li>
                <li>Credits were obtained through promotional codes or free trials (free credits are not refundable)</li>
              </ul>
              <p className="text-gray-700 leading-relaxed mt-3">
                <strong>Important:</strong> Credits are consumed when images are processed, not when they are downloaded. Processing an image deducts credits immediately.
              </p>
            </section>

            {/* 4. Refund Processing */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Refund Processing</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                When you request a refund within the 14-day window:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Full refunds are processed regardless of credit usage</li>
                <li>Any remaining credits in your account will be removed upon refund</li>
                <li>Refunds are issued to the original payment method</li>
              </ul>
            </section>

            {/* 5. How to Request a Refund */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">5. How to Request a Refund</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                To request a refund, follow these steps:
              </p>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>Email us at <a href="mailto:support@masterpost.io" className="text-green-600 hover:text-green-700">support@masterpost.io</a></li>
                <li>Include your registered email address</li>
                <li>Provide your purchase date and transaction ID (from Paddle confirmation email)</li>
                <li>Explain the reason for your refund request</li>
              </ol>
              <p className="text-gray-700 leading-relaxed mt-4">
                We will review your request within <strong>3 business days</strong> and respond via email with our decision.
              </p>
            </section>

            {/* 6. Refund Timeline */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Refund Timeline</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                Refund timeline:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Refunds are processed through Paddle within 3-5 business days</li>
                <li>It may take an additional 5-10 business days for the refund to appear in your account (depending on your bank)</li>
                <li>You will receive a confirmation email when the refund is processed</li>
              </ul>
            </section>

            {/* 7. Chargebacks */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Chargebacks</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                We strongly encourage you to contact us before initiating a chargeback with your bank.
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
                <li>Chargebacks are costly and damage our relationship with payment processors</li>
                <li>Most issues can be resolved through our refund policy</li>
                <li>Initiating a chargeback without contacting us may result in account termination</li>
                <li>If a chargeback is found to be fraudulent, we reserve the right to pursue legal action</li>
              </ul>
            </section>

            {/* 8. Contact Us */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Contact Us</h2>
              <p className="text-gray-700 leading-relaxed mb-3">
                If you have questions about our Refund Policy or need assistance:
              </p>
              <p className="text-gray-700 font-semibold">
                📧 <a href="mailto:support@masterpost.io" className="text-green-600 hover:text-green-700">support@masterpost.io</a>
              </p>
              <p className="text-gray-700 mt-4 leading-relaxed">
                We're here to help and will do our best to resolve any issues you may have with our service.
              </p>
            </section>

            {/* FAQ Box */}
            <section className="bg-green-50 border border-green-200 rounded-lg p-6 mt-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">📌 Quick Refund FAQ</h3>
              <div className="space-y-4">
                <div>
                  <p className="font-semibold text-gray-900">Q: Can I get a refund if I don't like the processed images?</p>
                  <p className="text-gray-700 text-sm mt-1">A: Yes! You can request a full refund within 14 days of purchase for any reason, including if you're not satisfied with the results.</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Q: I accidentally bought the wrong package. Can I exchange it?</p>
                  <p className="text-gray-700 text-sm mt-1">A: Yes! Contact us within 14 days and we can refund and help you purchase the correct package.</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Q: Do credits expire?</p>
                  <p className="text-gray-700 text-sm mt-1">A: No! Credits never expire. Use them at your own pace with no time pressure.</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Q: Can I get a refund on free trial credits?</p>
                  <p className="text-gray-700 text-sm mt-1">A: No. Free trial credits are complimentary and non-refundable.</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Q: What if I've already used credits?</p>
                  <p className="text-gray-700 text-sm mt-1">A: You can still request a full refund within 14 days regardless of how many credits you've used.</p>
                </div>
              </div>
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
