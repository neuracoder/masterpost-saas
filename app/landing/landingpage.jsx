'use client';

import { useState } from 'react';
import { Check, X, Clock, ArrowRight, Shield, CreditCard, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

const LandingPage = () => {
  const [activeFaq, setActiveFaq] = useState(null);

  const toggleFaq = (index) => {
    setActiveFaq(activeFaq === index ? null : index);
  };

  const scrollToPricing = () => {
    const pricingSection = document.getElementById('pricing-section');
    if (pricingSection) {
      pricingSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleBuyCredits = async (priceId) => {
    try {
      const customerEmail = prompt('Please enter your email:');
      if (!customerEmail) return;

      const response = await fetch('/api/v1/stripe/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          price_id: priceId,
          customer_email: customerEmail
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { url } = await response.json();
      window.location.href = url;
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to start checkout. Please try again.');
    }
  };

  const faqs = [
    {
      question: "Do you store my images?",
      answer: "No. Images are processed and deleted after 24 hours. We never keep or use your product photos."
    },
    {
      question: "What if the AI makes a mistake?",
      answer: "Use the manual editor to fix any edge cases. Unlimited edits included in all plans."
    },
    {
      question: "Can I cancel anytime?",
      answer: "Yes. No contracts. Cancel from your dashboard with one click."
    },
    {
      question: "What marketplaces do you support?",
      answer: "Amazon (all categories), eBay, Etsy, Instagram Shop, Walmart. Custom pipelines available on Business plan."
    },
    {
      question: "Do you have an API?",
      answer: "Yes, included in Business plan. Documentation at docs.masterpost.io"
    },
    {
      question: "What is your refund policy?",
      answer: "100% refund within 14 days if you are not satisfied. No questions asked."
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* HERO SECTION */}
      <section className="relative bg-gradient-to-br from-gray-50 to-white pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <motion.h1 
              className="text-4xl md:text-6xl font-bold text-gray-900 mb-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              Amazon-Compliant Product Images in 1 Click
            </motion.h1>
            <motion.p 
              className="text-xl text-gray-600 max-w-3xl mx-auto mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              Stop getting listings rejected. Masterpost automatically formats your product photos to meet Amazon, eBay, and Etsy requirements—in minutes, not days.
            </motion.p>
            
            <motion.div
              className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <button
                onClick={scrollToPricing}
                className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-4 px-8 rounded-lg text-lg transition-colors duration-200 flex items-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5" />
              </button>
              <p className="text-gray-600">No credit card required • 10 images free</p>
            </motion.div>

            <motion.div 
              className="flex items-center justify-center gap-4 mb-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              <span className="text-gray-700 font-medium">Trusted by 500+ Amazon sellers</span>
              <div className="flex -space-x-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="w-8 h-8 bg-gray-200 rounded-full border-2 border-white"></div>
                ))}
              </div>
            </motion.div>

            <motion.div 
              className="bg-white rounded-xl shadow-lg p-6 max-w-4xl mx-auto border border-gray-200"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="flex-1 text-center">
                  <div className="bg-gray-100 rounded-lg p-4 mb-2">
                    <div className="bg-gray-300 border-2 border-dashed rounded-xl w-64 h-64 mx-auto" />
                  </div>
                  <p className="text-gray-600 font-medium">Before: Rejected by Amazon</p>
                </div>
                <div className="flex-1 text-center">
                  <div className="bg-gray-100 rounded-lg p-4 mb-2 relative">
                    <div className="bg-gray-300 border-2 border-dashed rounded-xl w-64 h-64 mx-auto" />
                    <div className="absolute top-2 right-2 bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                      <Check className="w-3 h-3" />
                      Amazon Guidelines Compliant
                    </div>
                  </div>
                  <p className="text-gray-600 font-medium">After: Approved instantly</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* PROBLEM SECTION */}
      <section className="py-20 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Are Your Listings Getting Suppressed?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              You are not alone. Thousands of sellers face these exact problems every day.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                icon: <X className="w-8 h-8 text-red-500" />,
                title: "Rejected Images",
                description: "Amazon AI auto-detects non-compliant images faster than ever. One bad photo = suppressed listing = lost sales."
              },
              {
                icon: <Clock className="w-8 h-8 text-orange-500" />,
                title: "Manual Processing Takes Days",
                description: "Editing 500 SKUs in Photoshop? That is 40+ hours of work. Your time is worth more than $2/image."
              },
              {
                icon: <span className="text-2xl">💸</span>,
                title: "Designers Are Expensive",
                description: "Hiring a VA or designer costs $2-5 per image. For a 1000-product catalog, that is $5,000."
              }
            ].map((item, index) => (
              <motion.div 
                key={index}
                className="text-center p-6 rounded-xl border border-gray-200 hover:shadow-md transition-shadow duration-200"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <div className="flex justify-center mb-4">
                  {item.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* SOLUTION SECTION */}
      <section className="py-20 bg-gray-50 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              3 Steps to Marketplace-Ready Images
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From upload to download in under 5 minutes
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200 transform -translate-x-1/2"></div>
              
              {[
                {
                  step: 1,
                  icon: "📤",
                  title: "Upload",
                  description: "Drag & drop images or ZIP files. Process up to 1,500 at once."
                },
                {
                  step: 2,
                  icon: "🎯",
                  title: "Select Pipeline",
                  description: "Choose: Amazon Main Image | eBay Listing | Instagram Shop | Custom"
                },
                {
                  step: 3,
                  icon: "⬇️",
                  title: "Download",
                  description: "Get perfectly formatted images in 5 minutes. Ready to upload to any marketplace."
                }
              ].map((item, index) => (
                <motion.div 
                  key={item.step}
                  className="flex items-start mb-12 relative"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                >
                  <div className="flex-shrink-0 w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center text-2xl font-bold text-purple-600 z-10">
                    {item.icon}
                  </div>
                  <div className="ml-8">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                    <p className="text-gray-600">{item.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="mt-12 bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="bg-gray-200 border-2 border-dashed rounded-xl w-full h-64 mx-auto mb-4 flex items-center justify-center">
                <span className="text-gray-500">Demo: Upload → Process → Download</span>
              </div>
              <p className="text-gray-600">Watch how it works in 10 seconds</p>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section className="py-20 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Built Specifically for E-Commerce Sellers
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Not just another background remover—this is your e-commerce image workflow
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                title: "Marketplace Pipelines",
                description: "Pre-configured for Amazon (1000x1000, white bg), eBay (1600x1600), Etsy, Instagram. Not generic 'background removal.'"
              },
              {
                title: "Professional Shadows",
                description: "4 shadow types (drop, reflection, natural, auto). Toggle on/off. Amazon-compliant."
              },
              {
                title: "Batch Processing",
                description: "Upload ZIP with 500 images. All processed simultaneously. Download ZIP when done."
              },
              {
                title: "Manual Editor",
                description: "AI missed an edge? Fix it manually with brush tools. Undo/redo unlimited."
              },
              {
                title: "Compliance Checking",
                description: "Pre-flight check: Will Amazon reject this? Fix issues before upload."
              },
              {
                title: "Agency-Ready",
                description: "White-label option. API access. Process for multiple clients from one account."
              }
            ].map((feature, index) => (
              <motion.div 
                key={index}
                className="p-6 rounded-xl border border-gray-200 hover:border-purple-300 transition-colors duration-200"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* PRICING SECTION */}
      <section id="pricing-section" className="py-20 bg-gray-50 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Plans That Scale With Your Business
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choose the right plan for your catalog size and business needs
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                title: "STARTER",
                price: "$4.99",
                period: "one-time",
                credits: "50 credits",
                features: [
                  "50 image credits",
                  "All marketplace pipelines",
                  "No watermark",
                  "Email support"
                ],
                perfectFor: "Solo sellers",
                cta: "Get Started",
                popular: false,
                priceId: "price_1SLljD3M485N62s33mV2Jx2e"
              },
              {
                title: "PRO",
                price: "$17.99",
                period: "one-time",
                credits: "200 credits",
                features: [
                  "200 image credits",
                  "Manual editor unlimited",
                  "Batch ZIP processing",
                  "Priority processing",
                  "Chat support"
                ],
                perfectFor: "Power sellers",
                cta: "Get Pro",
                popular: true,
                priceId: "price_1SLljE3M485N62s3ieI3a0xv"
              },
              {
                title: "BUSINESS",
                price: "$39.99",
                period: "one-time",
                credits: "500 credits",
                features: [
                  "500 image credits",
                  "API access",
                  "White-label option",
                  "Custom pipelines",
                  "Dedicated support"
                ],
                perfectFor: "Agencies",
                cta: "Get Business",
                popular: false,
                priceId: "price_1SLljE3M485N62s3R66Ym6iA"
              }
            ].map((plan, index) => (
              <motion.div 
                key={index}
                className={`relative rounded-xl p-8 border-2 ${
                  plan.popular 
                    ? 'border-purple-500 bg-white shadow-xl' 
                    : 'border-gray-200 bg-white'
                }`}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      MOST POPULAR
                    </span>
                  </div>
                )}
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.title}</h3>
                <div className="mb-6">
                  <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                  <span className="text-gray-600">{plan.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                      <span className="text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handleBuyCredits(plan.priceId)}
                  className={`w-full py-3 px-4 rounded-lg font-semibold mb-4 ${
                    plan.popular
                      ? 'bg-purple-600 hover:bg-purple-700 text-white'
                      : 'bg-gray-900 hover:bg-gray-800 text-white'
                  } transition-colors duration-200`}
                >
                  {plan.cta}
                </button>
                <p className="text-sm text-gray-500 text-center">Perfect for: {plan.perfectFor}</p>
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12 max-w-3xl mx-auto">
            <p className="text-gray-600 mb-2">
              All plans include: Unlimited re-edits • All shadow effects • Lifetime access to updates
            </p>
            <p className="text-gray-600">Add-on: $0.05 per extra image</p>
          </div>
        </div>
      </section>

      {/* COMPARISON SECTION */}
      <section className="py-20 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Masterpost vs Hiring a Designer or VA?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              The numbers do not lie - automation wins every time
            </p>
          </div>

          <div className="max-w-4xl mx-auto overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left py-4 px-4 font-semibold text-gray-900">Feature</th>
                  <th className="text-center py-4 px-4 font-semibold text-gray-900">Masterpost</th>
                  <th className="text-center py-4 px-4 font-semibold text-gray-900">Hire Designer</th>
                  <th className="text-center py-4 px-4 font-semibold text-gray-900">Use Photoshop</th>
                </tr>
              </thead>
              <tbody>
                {[
                  {
                    feature: "Cost per 500 images",
                    masterpost: "$79/month",
                    designer: "$1,000-2,500",
                    photoshop: "Free (40 hours)"
                  },
                  {
                    feature: "Time to process",
                    masterpost: "5 minutes",
                    designer: "3-5 days",
                    photoshop: "40+ hours"
                  },
                  {
                    feature: "Amazon compliance",
                    masterpost: "✓ Automatic",
                    designer: "❌ Manual check",
                    photoshop: "❌ Manual check"
                  },
                  {
                    feature: "Batch processing",
                    masterpost: "✓ 500 at once",
                    designer: "❌ One by one",
                    photoshop: "❌ One by one"
                  },
                  {
                    feature: "Shadow effects",
                    masterpost: "✓ 4 types",
                    designer: "Depends",
                    photoshop: "Manual"
                  },
                  {
                    feature: "Revisions",
                    masterpost: "✓ Unlimited",
                    designer: "Extra cost",
                    photoshop: "Your time"
                  }
                ].map((row, index) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-4 px-4 font-medium text-gray-900">{row.feature}</td>
                    <td className="py-4 px-4 text-center text-gray-600">{row.masterpost}</td>
                    <td className="py-4 px-4 text-center text-gray-600">{row.designer}</td>
                    <td className="py-4 px-4 text-center text-gray-600">{row.photoshop}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* SOCIAL PROOF SECTION */}
      <section className="py-20 bg-gray-50 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              What Sellers Are Saying
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Real results from real e-commerce businesses
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                quote: "Processed 800 SKUs in one afternoon. Before Masterpost, this would have taken my VA 2 weeks. Already saved $1,500.",
                name: "Juan López",
                title: "Amazon FBA Seller",
                badge: "Verified Seller"
              },
              {
                quote: "The Amazon pipeline is amazing. Zero rejections since I started using it. Compliance issues are a thing of the past.",
                name: "Sarah Chen",
                title: "Shopify Store Owner",
                badge: "Pro Plan"
              },
              {
                quote: "We process images for 12 clients. The white-label option lets us offer it as our own service. ROI in first month.",
                name: "Miguel Torres",
                title: "E-commerce Agency",
                badge: "Business Plan"
              }
            ].map((testimonial, index) => (
              <motion.div 
                key={index}
                className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
              >
                <div className="mb-4">
                  <p className="text-gray-700 italic">"{testimonial.quote}"</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gray-200 rounded-full flex-shrink-0"></div>
                  <div>
                    <p className="font-semibold text-gray-900">{testimonial.name}</p>
                    <p className="text-gray-600 text-sm">{testimonial.title}</p>
                    <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full mt-1">
                      {testimonial.badge}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ SECTION */}
      <section className="py-20 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know before getting started
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <motion.div 
                key={index}
                className="border border-gray-200 rounded-lg overflow-hidden"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <button
                  className="w-full text-left p-6 flex justify-between items-center bg-white hover:bg-gray-50 transition-colors duration-200"
                  onClick={() => toggleFaq(index)}
                >
                  <span className="font-semibold text-gray-900">{faq.question}</span>
                  <svg 
                    className={`w-5 h-5 text-gray-500 transition-transform duration-200 ${
                      activeFaq === index ? 'rotate-180' : ''
                    }`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <div 
                  className={`overflow-hidden transition-all duration-300 ${
                    activeFaq === index ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
                  }`}
                >
                  <div className="p-6 pt-0 bg-gray-50">
                    <p className="text-gray-600">{faq.answer}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FINAL CTA SECTION */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-purple-700 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.h2
            className="text-3xl md:text-4xl font-bold text-white mb-4"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Ready to Stop Losing Sales to Rejected Images?
          </motion.h2>
          <motion.p
            className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Join 500+ sellers who automated their image processing.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <button
              onClick={scrollToPricing}
              className="bg-white text-purple-600 hover:bg-gray-100 font-bold py-4 px-8 rounded-lg text-lg transition-colors duration-200 flex items-center gap-2 mx-auto mb-8"
            >
              Start Free Trial — 10 Images Free
              <ArrowRight className="w-5 h-5" />
            </button>

            <div className="flex flex-wrap justify-center gap-6 text-purple-100">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                <span>Bank-level encryption</span>
              </div>
              <div className="flex items-center gap-2">
                <CreditCard className="w-5 h-5" />
                <span>Secure Stripe payments</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* FLOATING STICKY BUTTON */}
      <motion.button
        onClick={scrollToPricing}
        className="fixed bottom-8 right-8 bg-purple-600 hover:bg-purple-700 text-white font-bold py-4 px-6 rounded-full shadow-2xl flex items-center gap-2 z-50 transition-all duration-300 hover:scale-105"
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 1 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <CreditCard className="w-5 h-5" />
        <span>Buy Credits</span>
      </motion.button>
    </div>
  );
};

export default LandingPage;