import type React from "react"
import type { Metadata, Viewport } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Suspense } from "react"
import { SimpleAuthProvider } from "@/app/contexts/SimpleAuthContext"
import Script from "next/script"
import "./globals.css"

export const metadata: Metadata = {
  metadataBase: new URL('https://masterpost.io'),
  title: "Masterpost.io - AI Background Removal for E-commerce Sellers",
  description: "AI-powered bulk background removal for e-commerce sellers. Process hundreds of product images in minutes. 72% cheaper than competitors.",
  generator: "v0.app",

  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://masterpost.io/',
    title: 'Masterpost.io - AI Background Removal for E-commerce Sellers',
    description: 'AI-powered bulk background removal for e-commerce sellers. Process hundreds of product images in minutes. 72% cheaper than competitors.',
    siteName: 'Masterpost.io',
    images: [
      {
        url: 'https://masterpost.io/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Masterpost.io - Professional Background Removal',
      },
    ],
  },

  twitter: {
    card: 'summary_large_image',
    title: 'Masterpost.io - AI Background Removal for E-commerce Sellers',
    description: 'AI-powered bulk background removal for e-commerce sellers. Process hundreds of product images in minutes. 72% cheaper than competitors.',
    images: ['https://masterpost.io/og-image.png'],
  },

  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-48x48.png", sizes: "48x48", type: "image/png" },
      { url: "/favicon-96x96.png", sizes: "96x96", type: "image/png" },
      { url: "/favicon-144x144.png", sizes: "144x144", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
    other: [
      { rel: "android-chrome", url: "/android-chrome-192x192.png", sizes: "192x192" },
      { rel: "android-chrome", url: "/android-chrome-512x512.png", sizes: "512x512" },
    ],
  },
  manifest: "/site.webmanifest",
}

// Mover themeColor al objeto viewport según las recomendaciones de Next.js
export const viewport: Viewport = {
  themeColor: "#10b981",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <meta name="google-site-verification" content="BOd_FxHq_hRu541EGTJtays1JReKlhOJ5Zs98KR_hfU" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
      </head>
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable}`}>
        {/* Paddle.js SDK */}
        <Script
          src="https://cdn.paddle.com/paddle/v2/paddle.js"
          strategy="afterInteractive"
        />

        <SimpleAuthProvider>
          <Suspense fallback={null}>{children}</Suspense>
        </SimpleAuthProvider>
        {/* Analytics component removed: not compatible with Netlify hosting */}
      </body>
    </html>
  )
}
