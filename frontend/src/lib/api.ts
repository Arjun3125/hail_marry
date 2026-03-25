export const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\s+/g, "").replace(/\/+$/, "");
const ACCESS_TOKEN_KEY = "vidyaos_access_token";

export type APIErrorType = "auth" | "rate_limit" | "validation" | "service_unavailable" | "unknown";

export class APIError extends Error {
    status: number;
    type: APIErrorType;
    action: string;

    constructor(message: string, status: number, type: APIErrorType, action: string) {
        super(message);
        this.name = "APIError";
        this.status = status;
        this.type = type;
        this.action = action;
    }
}

function classifyAPIError(status: number, detail: string): APIError {
    if (status === 401 || status === 403) {
        return new APIError(detail || "Authentication required.", status, "auth", "Contact admin");
    }
    if (status === 429) {
        return new APIError(detail || "Too many requests.", status, "rate_limit", "Retry now");
    }
    if (status === 400 || status === 422) {
        return new APIError(detail || "Please check your input and try again.", status, "validation", "Try simplified mode");
    }
    if (status >= 500) {
        return new APIError(detail || "Service is temporarily unavailable.", status, "service_unavailable", "Retry now");
    }
    return new APIError(detail || "Unexpected error.", status, "unknown", "Contact admin");
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

export async function apiFetch(path: string, options: RequestInit = {}) {
    const url = `${API_BASE}${path}`;
    const headers = new Headers(options.headers || {});
    const token = getStoredAccessToken();

    if (!headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }
    if (token && !headers.has("Authorization")) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const res = await fetch(url, {
        credentials: "include",
        headers,
        ...options,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Request failed" }));
        throw classifyAPIError(res.status, error.detail || `HTTP ${res.status}`);
    }

    return res.json();
}

async function apiFormFetch(path: string, formData: FormData) {
    const token = getStoredAccessToken();
    const headers = new Headers();
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        credentials: "include",
        headers,
        body: formData,
    });

    const payload = await res.json().catch(() => ({}));
    if (!res.ok) {
        const detail =
            (payload && typeof payload === "object" && "detail" in payload ? (payload as { detail?: string }).detail : undefined) ||
            `HTTP ${res.status}`;
        throw classifyAPIError(res.status, detail);
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
        dispatchObservabilityAlerts: () => apiFetch("/api/admin/observability/alerts/dispatch", { method: "POST" }),
        traceDetail: (traceId: string) => apiFetch(`/api/admin/observability/traces/${traceId}`),
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
    ai: {
        query: (data: { query: string; mode: string; subject_id?: string; language?: string; response_length?: string; expertise_level?: string }) =>
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
};
