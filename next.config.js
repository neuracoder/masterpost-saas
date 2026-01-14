/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Environment variables available to the client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_API_V2_URL: process.env.NEXT_PUBLIC_API_V2_URL,
  },

  // Image configuration
  images: {
    unoptimized: true,
    domains: ['masterpost-io.onrender.com'], // Permite imágenes desde el backend
  },

  // Output configuration for production
  output: 'standalone',

  // ESLint and TypeScript configuration
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },

  // Headers para CORS y seguridad
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: 'https://masterpost-io.onrender.com',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'X-Requested-With,Content-Type,Authorization',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
