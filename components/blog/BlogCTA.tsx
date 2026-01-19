import Link from "next/link"
import { ArrowRight, Sparkles, Check, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface BlogCTAProps {
  variant?: 'default' | 'inline' | 'full'
  title?: string
  description?: string
}

export default function BlogCTA({
  variant = 'default',
  title = "Ready to Automate Your Image Processing?",
  description = "Stop wasting hours on manual editing. Masterpost.io processes your product images in seconds with AI-powered background removal."
}: BlogCTAProps) {
  if (variant === 'inline') {
    return (
      <div className="my-8 p-6 bg-gradient-to-r from-green-50 to-yellow-50 border-2 border-green-200 rounded-xl not-prose">
        <div className="flex flex-col md:flex-row items-center gap-4">
          <div className="flex-1">
            <p className="font-bold text-gray-900 mb-1">{title}</p>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
          <Link href="/app">
            <Button className="bg-green-600 hover:bg-green-700 text-white whitespace-nowrap">
              Try Free <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  if (variant === 'full') {
    return (
      <section className="my-16 not-prose">
        <Card className="overflow-hidden border-0 shadow-2xl">
          <div className="bg-gradient-to-br from-green-600 via-green-600 to-emerald-700 text-white">
            <CardContent className="p-8 md:p-12">
              <div className="grid md:grid-cols-2 gap-8 items-center">
                <div className="space-y-6">
                  <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                    <Sparkles className="w-4 h-4" />
                    <span className="text-sm font-semibold">72% Cheaper Than Competitors</span>
                  </div>

                  <h2 className="text-3xl md:text-4xl font-bold leading-tight">
                    {title}
                  </h2>

                  <p className="text-lg text-green-100 leading-relaxed">
                    {description}
                  </p>

                  <div className="flex flex-col sm:flex-row gap-4">
                    <Link href="/app">
                      <Button
                        size="lg"
                        className="bg-white text-green-600 hover:bg-gray-100 shadow-xl font-bold"
                      >
                        Start Free - 10 Images
                        <ArrowRight className="w-5 h-5 ml-2" />
                      </Button>
                    </Link>
                    <Link href="/pricing">
                      <Button
                        size="lg"
                        variant="outline"
                        className="border-2 border-white text-white hover:bg-white/10"
                      >
                        View Pricing
                      </Button>
                    </Link>
                  </div>

                  <p className="text-sm text-green-200 flex items-center gap-4 flex-wrap">
                    <span className="flex items-center">
                      <Check className="w-4 h-4 mr-1" /> No credit card
                    </span>
                    <span className="flex items-center">
                      <Check className="w-4 h-4 mr-1" /> 10 free images
                    </span>
                    <span className="flex items-center">
                      <Check className="w-4 h-4 mr-1" /> Instant results
                    </span>
                  </p>
                </div>

                <div className="hidden md:block">
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 space-y-4">
                    <h4 className="font-bold text-lg">What You Get:</h4>
                    <ul className="space-y-3">
                      {[
                        { icon: <Zap className="w-5 h-5" />, text: "1-click Amazon compliance" },
                        { icon: <Sparkles className="w-5 h-5" />, text: "AI-powered background removal" },
                        { icon: <Check className="w-5 h-5" />, text: "Pure white backgrounds (RGB 255,255,255)" },
                        { icon: <Check className="w-5 h-5" />, text: "Bulk processing up to 100 images" },
                        { icon: <Check className="w-5 h-5" />, text: "Multiple marketplace formats" },
                      ].map((item, i) => (
                        <li key={i} className="flex items-center gap-3">
                          <span className="text-yellow-400">{item.icon}</span>
                          <span>{item.text}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </div>
        </Card>
      </section>
    )
  }

  // Default variant
  return (
    <div className="my-12 not-prose">
      <Card className="border-2 border-green-200 bg-gradient-to-br from-green-50 via-white to-yellow-50 overflow-hidden">
        <CardContent className="p-8 md:p-10">
          <div className="text-center max-w-2xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 bg-green-100 text-green-700 px-4 py-2 rounded-full">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-bold">Try Masterpost.io Free</span>
            </div>

            <h3 className="text-2xl md:text-3xl font-bold text-gray-900">
              {title}
            </h3>

            <p className="text-gray-600 leading-relaxed">
              {description}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/app">
                <Button
                  size="lg"
                  className="bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-500/25 font-bold"
                >
                  Process 10 Images Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>

            <p className="text-sm text-gray-500 flex items-center justify-center gap-4 flex-wrap">
              <span className="flex items-center">
                <Check className="w-4 h-4 text-green-600 mr-1" /> No credit card
              </span>
              <span className="flex items-center">
                <Check className="w-4 h-4 text-green-600 mr-1" /> 72% cheaper
              </span>
              <span className="flex items-center">
                <Check className="w-4 h-4 text-green-600 mr-1" /> Instant results
              </span>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
