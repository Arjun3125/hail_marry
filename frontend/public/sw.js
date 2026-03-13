/**
 * VidyaOS Service Worker — Offline-First PWA support.
 * Cache-First for static assets, Network-First for API calls.
 */
const CACHE_NAME = "vidyaos-v1";
const STATIC_ASSETS = ["/", "/manifest.json"];

// Install — pre-cache shell
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch — Network-First for API, Cache-First for static
self.addEventListener("fetch", (event) => {
    const { request } = event;

    // Skip non-GET and WebSocket
    if (request.method !== "GET" || request.url.includes("/api/notifications/ws")) {
        return;
    }

    // API calls: Network-First with cache fallback
    if (request.url.includes("/api/")) {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                    }
                    return response;
                })
                .catch(() => caches.match(request))
        );
        return;
    }

    // Static assets: Cache-First with network fallback
    event.respondWith(
        caches.match(request).then((cached) => {
            if (cached) return cached;
            return fetch(request).then((response) => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                }
                return response;
            });
        })
    );
});
