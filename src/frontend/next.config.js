const withPWA = require("next-pwa")({
  dest: "public",
  disable: process.env.NODE_ENV === "development",
  register: true,
  skipWaiting: true,
  sw: "sw.js",
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  // -----------------------------------------------------------------------
  // Output mode — "standalone" produces a self-contained server bundle
  // that is copied into the production Docker image.
  // -----------------------------------------------------------------------
  output: "standalone",

  // -----------------------------------------------------------------------
  // Image optimisation
  // Whitelist external image domains used by the application.
  // -----------------------------------------------------------------------
  images: {
    remotePatterns: [
      {
        // Mapbox static images API (used for zone map thumbnails in emails)
        protocol: "https",
        hostname: "api.mapbox.com",
        pathname: "/styles/v1/**",
      },
      {
        // Supabase Storage (user-uploaded assets, e.g. farm logos)
        protocol: "https",
        hostname: "*.supabase.co",
        pathname: "/storage/v1/object/public/**",
      },
    ],
  },

  // -----------------------------------------------------------------------
  // Environment variable exposure
  // NEXT_PUBLIC_* vars are automatically exposed to the browser bundle
  // by Next.js.  We list them here for documentation and to enable
  // type-checking in next.config.js itself.
  //
  // Server-only variables (no NEXT_PUBLIC_ prefix) must NOT be listed
  // here — they must only be accessed in server components / API routes.
  // -----------------------------------------------------------------------
  env: {
    // All NEXT_PUBLIC_ variables are auto-exposed; no additional config needed.
    // This block is intentionally left for any non-NEXT_PUBLIC_ server env vars
    // that need to be forwarded (currently none).
  },

  // -----------------------------------------------------------------------
  // Webpack configuration
  // mapbox-gl requires special handling to suppress "mapbox-gl" warnings
  // from server-side rendering.
  // -----------------------------------------------------------------------
  webpack: (config, { isServer }) => {
    if (isServer) {
      // mapbox-gl is a browser-only library; exclude it from the server bundle
      config.externals = [...(config.externals || []), "mapbox-gl"];
    }
    return config;
  },

  // -----------------------------------------------------------------------
  // Experimental features
  // -----------------------------------------------------------------------
  experimental: {
    // Enable server actions (used for Supabase server-side auth helpers)
    serverActions: {
      allowedOrigins: ["localhost:3000"],
    },
  },
};

module.exports = withPWA(nextConfig);
