/**
 * VidyaOS service worker: offline-first support for safe cached surfaces.
 * Static routes use cache-first. Read-only school data uses network-first.
 */
const CACHE_NAME = "vidyaos-v2";
const STATIC_ASSETS = [
    "/",
    "/manifest.json",
    // Student routes
    "/student/attendance",
    "/student/assignments",
    "/student/timetable",
    "/student/upload",
    "/student/results",
    "/student/lectures",
    // Teacher routes
    "/teacher/dashboard",
    "/teacher/classes",
    "/teacher/attendance",
    "/teacher/assignments",
    "/teacher/marks",
    // Parent routes
    "/parent/dashboard",
    "/parent/attendance",
    "/parent/results",
];
const OFFLINE_API_PATTERNS = [
    // Student APIs
    "/api/student/attendance",
    "/api/student/assignments",
    "/api/student/timetable",
    "/api/student/materials",
    "/api/student/results",
    "/api/student/lectures",
    // Teacher APIs
    "/api/teacher/attendance/history",
    "/api/teacher/assignments/list",
    "/api/teacher/marks/history",
    "/api/teacher/classes",
    // Parent APIs
    "/api/parent/attendance",
    "/api/parent/results",
    "/api/parent/children",
    // Common read-only APIs
    "/api/school/timetable",
    "/api/school/holidays",
];

self.addEventListener("install", (event) => {
    event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)));
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))),
        ),
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    const { request } = event;
    if (request.method !== "GET" || request.url.includes("/api/notifications/ws")) return;

    const url = new URL(request.url);
    const canCacheApi = OFFLINE_API_PATTERNS.some((pattern) => url.pathname.startsWith(pattern));

    if (url.pathname.startsWith("/api/")) {
        if (!canCacheApi) return;
        event.respondWith(
            fetch(request)
                .then((response) => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                    }
                    return response;
                })
                .catch(() => caches.match(request)),
        );
        return;
    }

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
        }),
    );
});
