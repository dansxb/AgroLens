// Custom service worker — augments next-pwa generated SW with Mapbox tile caching.
// next-pwa injects its own precache manifest; this file adds runtime strategies.

const MAPBOX_CACHE = "mapbox-tiles-v1";
const API_CACHE = "api-responses-v1";
const MAPBOX_PATTERN = /^https:\/\/api\.mapbox\.com\//;
const API_PATTERN = /\/api\/v1\//;

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = request.url;

  // Cache-first for Mapbox tiles (expensive, rarely changes)
  if (MAPBOX_PATTERN.test(url)) {
    event.respondWith(
      caches.open(MAPBOX_CACHE).then((cache) =>
        cache.match(request).then((cached) => {
          if (cached) return cached;
          return fetch(request).then((response) => {
            if (response.ok) cache.put(request, response.clone());
            return response;
          });
        })
      )
    );
    return;
  }

  // Network-first for API responses (fresh data preferred, cache as fallback)
  if (API_PATTERN.test(url) && request.method === "GET") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            caches.open(API_CACHE).then((cache) => cache.put(request, response.clone()));
          }
          return response;
        })
        .catch(() =>
          caches.open(API_CACHE).then((cache) => cache.match(request))
        )
    );
  }
});
