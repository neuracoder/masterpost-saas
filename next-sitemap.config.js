/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: 'https://masterpost.io',
  generateRobotsTxt: false, // Ya tenemos robots.txt manual
  generateIndexSitemap: false,
  outDir: 'public',
  exclude: [
    '/app/*',
    '/api/*',
    '/login',
    '/auth/*',
    '/payment-success',
    '/manual-editor',
  ],
  changefreq: 'weekly',
  priority: 0.7,
  transform: async (config, path) => {
    // Prioridades personalizadas por página
    const priorities = {
      '/': 1.0,
      '/pricing': 0.9,
      '/privacy': 0.5,
      '/terms': 0.5,
      '/refund': 0.4,
    }

    return {
      loc: path,
      changefreq: path === '/' || path === '/pricing' ? 'weekly' : 'monthly',
      priority: priorities[path] || 0.7,
      lastmod: new Date().toISOString(),
    }
  },
}
