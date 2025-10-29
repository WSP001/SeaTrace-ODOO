/**
 * Next.js Configuration for SeaTrace
 * Includes Content Security Policy for production deployment
 * 
 * For the Commons Good 🌊
 */

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Enable SWC minification for production
  swcMinify: true,

  // API proxy configuration for local development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.API_BASE_URL || 'http://localhost:8004/api/:path*',
      },
    ];
  },

  // Security headers including CSP
  async headers() {
    // Content Security Policy
    // Allows fonts from Google Fonts, API calls to localhost:8004 and production API
    const csp = `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
      font-src 'self' https://fonts.gstatic.com data:;
      img-src 'self' data: blob: https:;
      media-src 'self' data: blob:;
      connect-src 'self' 
        http://localhost:8004 
        https://api.seatrace.worldseafoodproducers.com 
        https://seatrace.worldseafoodproducers.com
        wss://seatrace.worldseafoodproducers.com;
      frame-src 'self';
      object-src 'none';
      base-uri 'self';
      form-action 'self';
      frame-ancestors 'none';
      upgrade-insecure-requests;
    `
      .replace(/\s{2,}/g, ' ')
      .trim();

    return [
      {
        // Apply security headers to all routes
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: csp,
          },
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(self), payment=()',
          },
        ],
      },
    ];
  },

  // Environment variables exposed to browser
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8004',
    NEXT_PUBLIC_SITE_NAME: 'SeaTrace',
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL || 'https://seatrace.worldseafoodproducers.com',
  },

  // Webpack configuration for optimizations
  webpack: (config, { isServer }) => {
    // Optimize bundle size
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    return config;
  },

  // Image optimization domains
  images: {
    domains: [
      'seatrace.worldseafoodproducers.com',
      'worldseafoodproducers.com',
    ],
    formats: ['image/avif', 'image/webp'],
  },

  // Compression
  compress: true,

  // Production source maps (disable for security in production)
  productionBrowserSourceMaps: false,

  // Trailing slash behavior
  trailingSlash: false,

  // Power user settings
  poweredByHeader: false, // Remove X-Powered-By header
};

module.exports = nextConfig;
