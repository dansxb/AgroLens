export const MAPBOX_CACHE = "mapbox-tiles-v1";
export const API_CACHE = "api-responses-v1";

export const MAPBOX_URL_PATTERN = /^https:\/\/api\.mapbox\.com\//;
export const API_URL_PATTERN = /\/api\/v1\//;

export const CACHE_FIRST_MAX_AGE_SECONDS = 7 * 24 * 60 * 60;
export const NETWORK_FIRST_MAX_AGE_SECONDS = 5 * 60;

export const RUNTIME_CACHING = [
  {
    urlPattern: MAPBOX_URL_PATTERN,
    handler: "CacheFirst" as const,
    options: {
      cacheName: MAPBOX_CACHE,
      expiration: {
        maxEntries: 500,
        maxAgeSeconds: CACHE_FIRST_MAX_AGE_SECONDS,
      },
    },
  },
  {
    urlPattern: API_URL_PATTERN,
    handler: "NetworkFirst" as const,
    options: {
      cacheName: API_CACHE,
      networkTimeoutSeconds: 5,
      expiration: {
        maxEntries: 200,
        maxAgeSeconds: NETWORK_FIRST_MAX_AGE_SECONDS,
      },
    },
  },
];
