const RAW_API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\s+/g, "").replace(/\/+$/, "");
const ACCESS_TOKEN_KEY = "vidyaos_access_token";

export type APIErrorType = "auth" | "rate_limit" | "validation" | "service_unavailable" | "unknown";

function isLoopbackHost(hostname: string): boolean {
    return (
        hostname === "localhost" ||
        hostname === "127.0.0.1" ||
        hostname === "::1" ||
        hostname === "[::1]" ||
        hostname.startsWith("192.168.") ||
        hostname.startsWith("10.") ||
        hostname.startsWith("172.") ||
        hostname.startsWith("169.254.")
    );
}

function resolveAPIBase(): string {
    // Server-side (SSR): use configured URL or default for server-to-server calls
    if (typeof window === "undefined") {
        return RAW_API_BASE || "http://127.0.0.1:8000";
    }

    // Client-side: ALWAYS use relative paths so requests go through
    // the Next.js proxy rewrites configured in next.config.ts.
    // This completely avoids CORS issues in local development.
    if (!RAW_API_BASE) {
        return "";
    }

    try {
        const currentOrigin = new URL(window.location.origin);
        const configuredOrigin = new URL(RAW_API_BASE, currentOrigin.origin);

        // If both are local/private, always proxy through Next.js
        if (isLoopbackHost(configuredOrigin.hostname) || isLoopbackHost(currentOrigin.hostname)) {
            return "";
        }

        return configuredOrigin.origin === currentOrigin.origin ? "" : configuredOrigin.origin;
    } catch {
        return "";
    }
}

function buildApiUrl(base: string, path: string): string {
    return base ? `${base}${path}` : path;
}

export const API_BASE = resolveAPIBase();

export class APIError extends Error {
    status: number;
    type: APIErrorType;
    action: string;
    errorCode?: string;
    traceId?: string;
    subsystem?: string;

    constructor(message: string, status: number, type: APIErrorType, action: string, errorCode?: string, traceId?: string, subsystem?: string) {
        super(message);
        this.name = "APIError";
        this.status = status;
        this.type = type;
        this.action = action;
        this.errorCode = errorCode;
        this.traceId = traceId;
        this.subsystem = subsystem;
    }
}

type APIErrorPayload = {
    detail?: string;
    error_code?: string;
    trace_id?: string;
    subsystem?: string;
};

function formatAPIErrorMessage(detail: string, errorCode?: string): string {
    return errorCode ? `${detail} Error Code: ${errorCode}` : detail;
}

function classifyAPIError(status: number, payload: string | APIErrorPayload): APIError {
    const detail = typeof payload === "string" ? payload : payload.detail || `HTTP ${status}`;
    const errorCode = typeof payload === "string" ? undefined : payload.error_code;
    const traceId = typeof payload === "string" ? undefined : payload.trace_id;
    const subsystem = typeof payload === "string" ? undefined : payload.subsystem;
    const message = formatAPIErrorMessage(detail || `HTTP ${status}`, errorCode);
    if (status === 401 || status === 403) {
        return new APIError(message || "Authentication required.", status, "auth", "Contact admin", errorCode, traceId, subsystem);
    }
    if (status === 429) {
        return new APIError(message || "Too many requests.", status, "rate_limit", "Retry now", errorCode, traceId, subsystem);
    }
    if (status === 400 || status === 422) {
        return new APIError(message || "Please check your input and try again.", status, "validation", "Try simplified mode", errorCode, traceId, subsystem);
    }
    if (status >= 500) {
        return new APIError(message || "Service is temporarily unavailable.", status, "service_unavailable", "Retry now", errorCode, traceId, subsystem);
    }
    return new APIError(message || "Unexpected error.", status, "unknown", "Contact admin", errorCode, traceId, subsystem);
}

export function getStoredAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setStoredAccessToken(token: string) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function clearStoredAccessToken() {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
}

/**
 * Clear all demo session state (token + role cookie).
 * Call before every demo login to prevent stale token collisions.
 */
export function clearDemoSession() {
    clearStoredAccessToken();
    if (typeof document !== "undefined") {
        document.cookie = "demo_role=; path=/; max-age=0";
        document.cookie = "access_token=; path=/; max-age=0";
    }
}

function getApiBaseCandidates(path: string): string[] {
    const candidates = new Set<string>();

    if (API_BASE) {
        candidates.add(API_BASE);
    }

    if (typeof window !== "undefined") {
        // Client-side: only use relative paths (Next.js proxy).
        // Never add a direct cross-origin :8000 URL — that causes CORS.
        candidates.add("");
    } else {
        // Server-side: direct backend calls are fine
        candidates.add("http://127.0.0.1:8000");
    }

    return Array.from(candidates).map((base) => buildApiUrl(base, path));
}

async function fetchWithFallback(path: string, options: RequestInit): Promise<Response> {
    let lastError: unknown;

    for (const url of getApiBaseCandidates(path)) {
        try {
            const response = await fetch(url, options);

            // In local demo/dev mode, a same-origin `/api/*` miss means the
            // request hit Next.js instead of the FastAPI backend. Fall through
            // to the explicit backend candidate before surfacing the 404.
            if (
                typeof window !== "undefined" &&
                response.status === 404 &&
                path.startsWith("/api/") &&
                (url.startsWith("/") || url.startsWith(window.location.origin))
            ) {
                continue;
            }

            return response;
        } catch (error) {
            lastError = error;
        }
    }

    throw new APIError(
        lastError instanceof Error
            ? `Failed to reach the API service. ${lastError.message}`
            : "Failed to reach the API service.",
        0,
        "service_unavailable",
        "Retry now",
    );
}

export async function apiFetch(path: string, options: RequestInit = {}) {
    const headers = new Headers(options.headers || {});
    const token = getStoredAccessToken();

    if (!headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }
    if (token && !headers.has("Authorization")) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const res = await fetchWithFallback(path, {
        credentials: "include",
        headers,
        ...options,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Request failed" })) as APIErrorPayload;
        throw classifyAPIError(res.status, error);
    }

    if (res.status === 204) {
        return null;
    }

    const contentType = res.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
        return null;
    }

    return res.json();
}

async function apiFormFetch(path: string, formData: FormData) {
    const token = getStoredAccessToken();
    const headers = new Headers();
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const res = await fetchWithFallback(path, {
        method: "POST",
        credentials: "include",
        headers,
        body: formData,
    });

    const payload = await res.json().catch(() => ({}));
    if (!res.ok) {
        throw classifyAPIError(res.status, (payload || {}) as APIErrorPayload);
    }

    return payload;
}

export const api = {
    auth: {
        loginGoogle: async (token: string) => {
            const payload = await apiFetch("/api/auth/google", {
                method: "POST",
                body: JSON.stringify({ token }),
            }) as { access_token?: string };
            if (payload?.access_token) {
                setStoredAccessToken(payload.access_token);
            }
            return payload;
        },
        qrLogin: async (token: string) => {
            const payload = await apiFetch("/api/auth/qr", {
                method: "POST",
                body: JSON.stringify({ token }),
            }) as { access_token?: string };
            if (payload?.access_token) {
                setStoredAccessToken(payload.access_token);
            }
            return payload;
        },
        me: () => apiFetch("/api/auth/me"),
        updateProfile: (data: { full_name?: string; avatar_url?: string }) =>
            apiFetch("/api/auth/profile", {
                method: "PATCH",
                body: JSON.stringify(data),
            }),
        logout: async () => {
            try {
                return await apiFetch("/api/auth/logout", { method: "POST" });
            } finally {
                clearStoredAccessToken();
            }
        },
    },
    student: {
        dashboard: () => apiFetch("/api/student/dashboard"),
        streaks: () => apiFetch("/api/student/streaks"),
        attendance: (params?: string) => apiFetch(`/api/student/attendance${params ? `?${params}` : ""}`),
        results: () => apiFetch("/api/student/results"),
        resultsTrends: () => apiFetch("/api/student/results/trends"),
        assignments: () => apiFetch("/api/student/assignments"),
        submitAssignment: (assignmentId: string, formData: FormData) =>
            apiFormFetch(`/api/student/assignments/${assignmentId}/submit`, formData),
        timetable: () => apiFetch("/api/student/timetable"),
        lectures: () => apiFetch("/api/student/lectures"),
        complaints: () => apiFetch("/api/student/complaints"),
        createComplaint: (data: { category: string; description: string }) =>
            apiFetch("/api/student/complaints", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        upload: (formData: FormData) => apiFormFetch("/api/student/upload", formData),
        uploads: () => apiFetch("/api/student/uploads"),
        weakTopics: () => apiFetch("/api/student/weak-topics"),
        generateTool: (data: { tool: "quiz" | "flashcards" | "mindmap" | "flowchart" | "concept_map"; topic: string; subject_id?: string }) =>
            apiFetch("/api/student/tools/generate", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        enqueueToolJob: (data: { tool: "quiz" | "flashcards" | "mindmap" | "flowchart" | "concept_map"; topic: string; subject_id?: string }) =>
            apiFetch("/api/student/tools/generate/jobs", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        reviews: () => apiFetch("/api/student/reviews"),
        createReview: (data: { topic: string; subject_id?: string }) =>
            apiFetch("/api/student/reviews", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        completeReview: (id: string, data: { rating: number }) =>
            apiFetch(`/api/student/reviews/${id}/complete`, {
                method: "POST",
                body: JSON.stringify(data),
            }),
        testSeries: () => apiFetch("/api/student/test-series"),
        leaderboard: (seriesId: string) => apiFetch(`/api/student/test-series/${seriesId}/leaderboard`),
        myRank: (seriesId: string) => apiFetch(`/api/student/test-series/${seriesId}/my-rank`),
        submitMockTest: (seriesId: string, data: { marks_obtained: number; time_taken_minutes?: number }) =>
            apiFetch(`/api/student/test-series/${seriesId}/submit`, {
                method: "POST",
                body: JSON.stringify(data),
            }),
    },
    teacher: {
        dashboard: () => apiFetch("/api/teacher/dashboard"),
        classes: () => apiFetch("/api/teacher/classes"),
        assignments: () => apiFetch("/api/teacher/assignments"),
        insights: () => apiFetch("/api/teacher/insights"),
        submitAttendance: (data: { class_id: string; date: string; entries: Array<{ student_id: string; status: string }> }) =>
            apiFetch("/api/teacher/attendance", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        classAttendance: (classId: string) => apiFetch(`/api/teacher/attendance/${classId}`),
        importAttendanceCsv: (classId: string, date: string, formData: FormData) => {
            const query = new URLSearchParams({ class_id: classId, date });
            return apiFormFetch(`/api/teacher/attendance/csv-import?${query.toString()}`, formData);
        },
        createExam: (data: { name: string; subject_id: string; max_marks: number; exam_date?: string }) =>
            apiFetch("/api/teacher/exams", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        submitMarks: (data: { exam_id: string; entries: Array<{ student_id: string; marks_obtained: number }> }) =>
            apiFetch("/api/teacher/marks", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        importMarksCsv: (examId: string, formData: FormData) => {
            const query = new URLSearchParams({ exam_id: examId });
            return apiFormFetch(`/api/teacher/marks/csv-import?${query.toString()}`, formData);
        },
        createAssignment: (data: { title: string; description: string; subject_id: string; due_date?: string }) =>
            apiFetch("/api/teacher/assignments", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        ingestYoutube: (data: { url: string; title: string; subject_id?: string }) =>
            apiFetch("/api/teacher/youtube", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        uploadDocument: (formData: FormData) => apiFormFetch("/api/teacher/upload", formData),
        previewStudentOnboarding: (formData: FormData) => apiFormFetch("/api/teacher/onboard/students?preview=1", formData),
        onboardStudents: (formData: FormData) => apiFormFetch("/api/teacher/onboard/students", formData),
        generateAssessment: (data: { subject_id: string; topic: string; num_questions?: number }) =>
            apiFetch("/api/teacher/generate-assessment", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        doubtHeatmap: () => apiFetch("/api/teacher/doubt-heatmap"),
        getQrTokens: (classId: string) => apiFetch(`/api/teacher/classes/${classId}/qr-tokens`),
        broadcast: (data: { class_id: string; message: string; priority?: string }) =>
            apiFetch("/api/teacher/broadcast", {
                method: "POST",
                body: JSON.stringify(data),
            }),
    },
    admin: {
        dashboard: () => apiFetch("/api/admin/dashboard"),
        users: () => apiFetch("/api/admin/users"),
        features: () => apiFetch("/api/features"),
        toggleFeature: (featureId: string, enabled: boolean) =>
            apiFetch(`/api/features/${featureId}/toggle`, {
                method: "POST",
                body: JSON.stringify({ enabled }),
            }),
        applyProfile: (profileName: string) =>
            apiFetch(`/api/features/profile/${profileName}`, { method: "POST" }),
        students: () => apiFetch("/api/admin/students"),
        changeUserRole: (id: string, role: string) =>
            apiFetch(`/api/admin/users/${id}/role`, {
                method: "PATCH",
                body: JSON.stringify({ role }),
            }),
        toggleUserActive: (id: string) =>
            apiFetch(`/api/admin/users/${id}/deactivate`, {
                method: "PATCH",
            }),
        aiUsage: () => apiFetch("/api/admin/ai-usage"),
        aiReview: () => apiFetch("/api/admin/ai-review"),
        aiReviewDetail: (id: string) => apiFetch(`/api/admin/ai-review/${id}`),
        updateAIReview: (id: string, data: { action: "approve" | "flag"; note?: string }) =>
            apiFetch(`/api/admin/ai-review/${id}`, {
                method: "PATCH",
                body: JSON.stringify(data),
            }),
        aiJobsMetrics: () => apiFetch("/api/admin/ai-jobs/metrics"),
        aiJobs: (params?: { limit?: number; status?: string; job_type?: string }) => {
            const query = new URLSearchParams();
            if (params?.limit) query.set("limit", String(params.limit));
            if (params?.status) query.set("status", params.status);
            if (params?.job_type) query.set("job_type", params.job_type);
            const suffix = query.toString();
            return apiFetch(`/api/admin/ai-jobs${suffix ? `?${suffix}` : ""}`);
        },
        aiJobsHistory: (limit = 50) => apiFetch(`/api/admin/ai-jobs/history?limit=${limit}`),
        aiJobDetail: (id: string) => apiFetch(`/api/admin/ai-jobs/${id}`),
        cancelAIJob: (id: string) => apiFetch(`/api/admin/ai-jobs/${id}/cancel`, { method: "POST" }),
        retryAIJob: (id: string) => apiFetch(`/api/admin/ai-jobs/${id}/retry`, { method: "POST" }),
        deadLetterAIJob: (id: string) => apiFetch(`/api/admin/ai-jobs/${id}/dead-letter`, { method: "POST" }),
        observabilityAlerts: () => apiFetch("/api/admin/observability/alerts"),
        ocrMetrics: () => apiFetch("/api/admin/observability/ocr-metrics"),
        dispatchObservabilityAlerts: () => apiFetch("/api/admin/observability/alerts/dispatch", { method: "POST" }),
        traceDetail: (traceId: string) => apiFetch(`/api/admin/observability/traces/${traceId}`),
        traceabilitySummary: (days = 7) => apiFetch(`/api/admin/observability/traceability?days=${days}`),
        complaints: () => apiFetch("/api/admin/complaints"),
        updateComplaint: (id: string, status: string, resolution_note = "") =>
            apiFetch(`/api/admin/complaints/${id}`, {
                method: "PATCH",
                body: JSON.stringify({ status, resolution_note }),
            }),
        generateQrTokens: (data?: { student_ids?: string[]; class_id?: string; expires_in_days?: number; regenerate?: boolean }) =>
            apiFetch("/api/admin/generate-qr-tokens", {
                method: "POST",
                body: JSON.stringify(data || {}),
            }),
        classes: () => apiFetch("/api/admin/classes"),
        createClass: (data: { name: string; grade_level: string; academic_year?: string }) =>
            apiFetch("/api/admin/classes", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        createSubject: (data: { name: string; class_id: string }) =>
            apiFetch("/api/admin/subjects", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        timetable: (classId: string) => apiFetch(`/api/admin/timetable/${classId}`),
        createTimetableSlot: (data: {
            class_id: string;
            subject_id: string;
            teacher_id: string;
            day_of_week: number;
            start_time: string;
            end_time: string;
        }) =>
            apiFetch("/api/admin/timetable", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        generateTimetable: (data: Record<string, unknown>) =>
            apiFetch("/api/admin/timetable/generate", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        deleteTimetableSlot: (slotId: string) =>
            apiFetch(`/api/admin/timetable/${slotId}`, { method: "DELETE" }),
        reportsAttendance: () => apiFetch("/api/admin/reports/attendance"),
        reportsPerformance: () => apiFetch("/api/admin/reports/performance"),
        reportsAIUsage: () => apiFetch("/api/admin/reports/ai-usage"),
        security: () => apiFetch("/api/admin/security"),
        billing: () => apiFetch("/api/admin/billing"),
        settings: () => apiFetch("/api/admin/settings"),
        brandingConfig: () => apiFetch("/api/branding/config"),
        extractBranding: (formData: FormData) => apiFormFetch("/api/branding/extract", formData),
        saveBranding: (data: { primary_color?: string; secondary_color?: string; accent_color?: string; font_family?: string; theme_style?: string; logo_url?: string }) =>
            apiFetch("/api/branding/save", {
                method: "PATCH",
                body: JSON.stringify(data),
            }),
        whatsappReleaseGateSnapshot: (days = 7) => apiFetch(`/api/whatsapp/release-gate-snapshot?days=${days}`),
        mascotReleaseGateSnapshot: (days = 7) => apiFetch(`/api/mascot/release-gate-snapshot?days=${days}`),
        mascotReleaseGateEvidence: (days = 7) => apiFetch(`/api/mascot/release-gate-evidence?days=${days}`),
        mascotStagingPacket: (days = 7) => apiFetch(`/api/mascot/staging-packet?days=${days}`),
        updateSettings: (data: { ai_daily_limit?: number; name?: string }) =>
            apiFetch("/api/admin/settings", {
                method: "PATCH",
                body: JSON.stringify(data),
            }),
        webhooks: () => apiFetch("/api/admin/webhooks"),
        createWebhook: (data: { event_type: string; target_url: string }) =>
            apiFetch("/api/admin/webhooks", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        toggleWebhook: (id: string, is_active: boolean) =>
            apiFetch(`/api/admin/webhooks/${id}`, {
                method: "PATCH",
                body: JSON.stringify({ is_active }),
            }),
        deleteWebhook: (id: string) =>
            apiFetch(`/api/admin/webhooks/${id}`, { method: "DELETE" }),
        webhookDeliveries: (id: string) =>
            apiFetch(`/api/admin/webhooks/${id}/deliveries`),
        parentLinks: () => apiFetch("/api/admin/parent-links"),
        createParentLink: (data: { parent_id: string; child_id: string }) =>
            apiFetch("/api/admin/parent-links", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        deleteParentLink: (id: string) =>
            apiFetch(`/api/admin/parent-links/${id}`, { method: "DELETE" }),
    },
    enterprise: {
        ssoSettings: () => apiFetch("/api/admin/enterprise/sso"),
        updateSSOSettings: (data: { enabled?: boolean; entity_id?: string; metadata_url?: string; attribute_email?: string; attribute_name?: string }) =>
            apiFetch("/api/admin/enterprise/sso", {
                method: "PATCH",
                body: JSON.stringify(data),
            }),
        importSSOMetadata: (data: { metadata_url?: string; metadata_xml?: string }) =>
            apiFetch("/api/admin/enterprise/sso/import-metadata", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        vectorBackend: () => apiFetch("/api/admin/enterprise/vector-backend"),
        complianceSettings: () => apiFetch("/api/admin/enterprise/compliance/settings"),
        updateComplianceSettings: (data: { data_retention_days?: number; export_retention_days?: number }) =>
            apiFetch("/api/admin/enterprise/compliance/settings", {
                method: "PATCH",
                body: JSON.stringify(data),
            }),
        complianceExports: () => apiFetch("/api/admin/enterprise/compliance/exports"),
        createComplianceExport: (data: { scope_type?: string; scope_user_id?: string }) =>
            apiFetch("/api/admin/enterprise/compliance/exports", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        deletionRequests: () => apiFetch("/api/admin/enterprise/compliance/deletion-requests"),
        createDeletionRequest: (data: { target_user_id?: string; reason: string }) =>
            apiFetch("/api/admin/enterprise/compliance/deletion-requests", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        resolveDeletionRequest: (id: string, note: string) =>
            apiFetch(`/api/admin/enterprise/compliance/deletion-requests/${id}/resolve`, {
                method: "POST",
                body: JSON.stringify({ note }),
            }),
        incidentRoutes: () => apiFetch("/api/admin/enterprise/incidents/routes"),
        createIncidentRoute: (data: {
            name: string;
            channel_type: string;
            target: string;
            secret?: string;
            severity_filter?: string;
            escalation_channel_type?: string;
            escalation_target?: string;
            escalation_after_minutes?: number;
        }) =>
            apiFetch("/api/admin/enterprise/incidents/routes", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        syncIncidents: () => apiFetch("/api/admin/enterprise/incidents/sync", { method: "POST" }),
        incidents: () => apiFetch("/api/admin/enterprise/incidents"),
        incidentDetail: (id: string) => apiFetch(`/api/admin/enterprise/incidents/${id}`),
        acknowledgeIncident: (id: string) =>
            apiFetch(`/api/admin/enterprise/incidents/${id}/acknowledge`, { method: "POST" }),
        resolveIncident: (id: string, note: string) =>
            apiFetch(`/api/admin/enterprise/incidents/${id}/resolve`, {
                method: "POST",
                body: JSON.stringify({ note }),
            }),
    },
    parent: {
        dashboard: () => apiFetch("/api/parent/dashboard"),
        attendance: () => apiFetch("/api/parent/attendance"),
        results: () => apiFetch("/api/parent/results"),
        reports: () => apiFetch("/api/parent/reports"),
        audioReport: (childId?: string) =>
            apiFetch(`/api/parent/audio-report${childId ? `?child_id=${childId}` : ""}`),
    },
    aiHistory: {
        list: (params?: {
            page?: number;
            mode?: string;
            folder_id?: string;
            is_pinned?: boolean;
            search?: string;
            date_from?: string;
            date_to?: string;
            sort_by?: string;
            sort_order?: string;
        }) => {
            const query = new URLSearchParams();
            if (params?.page) query.set("page", String(params.page));
            if (params?.mode) query.set("mode", params.mode);
            if (params?.folder_id) query.set("folder_id", params.folder_id);
            if (params?.is_pinned !== undefined) query.set("is_pinned", String(params.is_pinned));
            if (params?.search) query.set("search", params.search);
            if (params?.date_from) query.set("date_from", params.date_from);
            if (params?.date_to) query.set("date_to", params.date_to);
            if (params?.sort_by) query.set("sort_by", params.sort_by);
            if (params?.sort_order) query.set("sort_order", params.sort_order);
            const suffix = query.toString();
            return apiFetch(`/api/student/ai-history${suffix ? `?${suffix}` : ""}`);
        },
        get: (id: string) => apiFetch(`/api/student/ai-history/${id}`),
        updateTitle: (id: string, title: string) =>
            apiFetch(`/api/student/ai-history/${id}/title`, {
                method: "PATCH",
                body: JSON.stringify({ title }),
            }),
        togglePin: (id: string) =>
            apiFetch(`/api/student/ai-history/${id}/pin`, { method: "POST" }),
        delete: (id: string) =>
            apiFetch(`/api/student/ai-history/${id}`, { method: "DELETE" }),
        moveToFolder: (id: string, folder_id: string | null) =>
            apiFetch(`/api/student/ai-history/${id}/move`, {
                method: "POST",
                body: JSON.stringify({ folder_id }),
            }),
        folders: {
            list: () => apiFetch("/api/student/ai-history/folders"),
            create: (name: string, color?: string) =>
                apiFetch("/api/student/ai-history/folders", {
                    method: "POST",
                    body: JSON.stringify({ name, color }),
                }),
            update: (id: string, name?: string, color?: string) =>
                apiFetch(`/api/student/ai-history/folders/${id}`, {
                    method: "PATCH",
                    body: JSON.stringify({ name, color }),
                }),
            delete: (id: string) =>
                apiFetch(`/api/student/ai-history/folders/${id}`, { method: "DELETE" }),
        },
        stats: () => apiFetch("/api/student/ai-history/stats"),
    },
    notebooks: {
        list: () => apiFetch("/api/notebooks"),
        create: (data: { name: string; description?: string; subject?: string; color?: string; icon?: string }) =>
            apiFetch("/api/notebooks", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        get: (id: string) => apiFetch(`/api/notebooks/${id}`),
        update: (id: string, data: Partial<{ name: string; description: string; subject: string; color: string; icon: string; is_active: boolean }>) =>
            apiFetch(`/api/notebooks/${id}`, {
                method: "PUT",
                body: JSON.stringify(data),
            }),
        delete: (id: string) => apiFetch(`/api/notebooks/${id}`, { method: "DELETE" }),
        stats: (id: string) => apiFetch(`/api/notebooks/${id}/stats`),
    },
    ai: {
        query: (data: { query: string; mode: string; subject_id?: string; notebook_id?: string | null; language?: string; response_length?: string; expertise_level?: string }) =>
            apiFetch("/api/ai/query", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        enqueueQueryJob: (data: { query: string; mode: string; subject_id?: string; language?: string; response_length?: string; expertise_level?: string }) =>
            apiFetch("/api/ai/query/jobs", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        audioOverview: (data: { topic: string; format?: string; language?: string }) =>
            apiFetch("/api/ai/audio-overview", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        enqueueAudioOverviewJob: (data: { topic: string; format?: string; language?: string }) =>
            apiFetch("/api/ai/audio-overview/jobs", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        videoOverview: (data: { topic: string; num_slides?: number; language?: string }) =>
            apiFetch("/api/ai/video-overview", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        enqueueVideoOverviewJob: (data: { topic: string; num_slides?: number; language?: string }) =>
            apiFetch("/api/ai/video-overview/jobs", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        jobStatus: (jobId: string) => apiFetch(`/api/ai/jobs/${jobId}`),
        discoverSources: (data: { query: string; max_results?: number }) =>
            apiFetch("/api/ai/discover-sources", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        ingestUrl: (data: { url: string; title?: string; subject_id?: string }) =>
            apiFetch("/api/ai/ingest-url", {
                method: "POST",
                body: JSON.stringify(data),
            }),
    },
    mascot: {
        message: (data: {
            message: string;
            channel?: "web";
            notebook_id?: string | null;
            session_id?: string | null;
            conversation_history?: Array<{ role: string; content: string }>;
            attachments?: Array<{ kind: string; url?: string | null; label?: string | null; content_type?: string | null }>;
            ui_context?: {
                current_route?: string;
                selected_notebook_id?: string | null;
                current_page_entity?: string | null;
                current_page_entity_id?: string | null;
                metadata?: Record<string, unknown>;
            };
        }) =>
            apiFetch("/api/mascot/message", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        upload: (formData: FormData) => apiFormFetch("/api/mascot/upload", formData),
        confirm: (data: { confirmation_id: string; approved: boolean; channel?: "web"; session_id?: string | null }) =>
            apiFetch("/api/mascot/confirm", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        suggestions: (params?: { current_route?: string; notebook_id?: string | null; current_page_entity?: string | null }) => {
            const query = new URLSearchParams();
            if (params?.current_route) query.set("current_route", params.current_route);
            if (params?.notebook_id) query.set("notebook_id", params.notebook_id);
            if (params?.current_page_entity) query.set("current_page_entity", params.current_page_entity);
            const suffix = query.toString();
            return apiFetch(`/api/mascot/suggestions${suffix ? `?${suffix}` : ""}`);
        },
        session: (params?: { channel?: string; session_id?: string | null }) => {
            const query = new URLSearchParams();
            if (params?.channel) query.set("channel", params.channel);
            if (params?.session_id) query.set("session_id", params.session_id);
            const suffix = query.toString();
            return apiFetch(`/api/mascot/session${suffix ? `?${suffix}` : ""}`);
        },
        clearSession: (params?: { channel?: string; session_id?: string | null }) => {
            const query = new URLSearchParams();
            if (params?.channel) query.set("channel", params.channel);
            if (params?.session_id) query.set("session_id", params.session_id);
            const suffix = query.toString();
            return apiFetch(`/api/mascot/session${suffix ? `?${suffix}` : ""}`, { method: "DELETE" });
        },
    },
    personalization: {
        recommendations: (params?: {
            active_tool?: string;
            notebook_id?: string | null;
            current_surface?: string;
            current_topic?: string | null;
            current_query?: string | null;
        }) => {
            const query = new URLSearchParams();
            if (params?.active_tool) query.set("active_tool", params.active_tool);
            if (params?.notebook_id) query.set("notebook_id", params.notebook_id);
            if (params?.current_surface) query.set("current_surface", params.current_surface);
            if (params?.current_topic) query.set("current_topic", params.current_topic);
            if (params?.current_query) query.set("current_query", params.current_query);
            const suffix = query.toString();
            return apiFetch(`/api/personalization/recommendations${suffix ? `?${suffix}` : ""}`);
        },
        remediation: (params?: { limit?: number }) => {
            const query = new URLSearchParams();
            if (typeof params?.limit === "number") query.set("limit", String(params.limit));
            const suffix = query.toString();
            return apiFetch(`/api/personalization/remediation${suffix ? `?${suffix}` : ""}`);
        },
        studyPath: (params?: {
            topic?: string | null;
            notebook_id?: string | null;
            subject_id?: string | null;
            current_surface?: string | null;
            force_refresh?: boolean;
        }) => {
            const query = new URLSearchParams();
            if (params?.topic) query.set("topic", params.topic);
            if (params?.notebook_id) query.set("notebook_id", params.notebook_id);
            if (params?.subject_id) query.set("subject_id", params.subject_id);
            if (params?.current_surface) query.set("current_surface", params.current_surface);
            if (params?.force_refresh) query.set("force_refresh", "true");
            const suffix = query.toString();
            return apiFetch(`/api/personalization/study-path${suffix ? `?${suffix}` : ""}`);
        },
        recordEvent: (data: {
            event_type: "recommendation_click" | "study_path_open" | "study_path_step_complete";
            surface?: string;
            target?: string;
            item_id?: string;
        }) =>
            apiFetch("/api/personalization/events", {
                method: "POST",
                body: JSON.stringify(data),
                keepalive: true,
            }),
        metrics: () => apiFetch("/api/personalization/metrics"),
        completeStudyPathStep: (planId: string, stepId: string) =>
            apiFetch(`/api/personalization/study-path/${planId}/steps/${stepId}/complete`, { method: "POST" }),
    },
};
