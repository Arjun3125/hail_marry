export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch(path: string, options: RequestInit = {}) {
    const url = `${API_BASE}${path}`;
    const res = await fetch(url, {
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
        ...options,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(error.detail || `HTTP ${res.status}`);
    }

    return res.json();
}

async function apiFormFetch(path: string, formData: FormData) {
    const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        credentials: "include",
        body: formData,
    });

    const payload = await res.json().catch(() => ({}));
    if (!res.ok) {
        const detail =
            (payload && typeof payload === "object" && "detail" in payload ? (payload as { detail?: string }).detail : undefined) ||
            `HTTP ${res.status}`;
        throw new Error(detail);
    }

    return payload;
}

export const api = {
    auth: {
        loginGoogle: (token: string) =>
            apiFetch("/api/auth/google", {
                method: "POST",
                body: JSON.stringify({ token }),
            }),
        me: () => apiFetch("/api/auth/me"),
        updateProfile: (data: { full_name?: string; avatar_url?: string }) =>
            apiFetch("/api/auth/profile", {
                method: "PATCH",
                body: JSON.stringify(data),
            }),
        logout: () => apiFetch("/api/auth/logout", { method: "POST" }),
    },
    student: {
        dashboard: () => apiFetch("/api/student/dashboard"),
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
    },
    admin: {
        dashboard: () => apiFetch("/api/admin/dashboard"),
        users: () => apiFetch("/api/admin/users"),
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
        complaints: () => apiFetch("/api/admin/complaints"),
        updateComplaint: (id: string, status: string, resolution_note = "") =>
            apiFetch(`/api/admin/complaints/${id}`, {
                method: "PATCH",
                body: JSON.stringify({ status, resolution_note }),
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
        deleteTimetableSlot: (slotId: string) =>
            apiFetch(`/api/admin/timetable/${slotId}`, { method: "DELETE" }),
        reportsAttendance: () => apiFetch("/api/admin/reports/attendance"),
        reportsPerformance: () => apiFetch("/api/admin/reports/performance"),
        reportsAIUsage: () => apiFetch("/api/admin/reports/ai-usage"),
        security: () => apiFetch("/api/admin/security"),
        billing: () => apiFetch("/api/admin/billing"),
        settings: () => apiFetch("/api/admin/settings"),
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
        audioOverview: (data: { topic: string; format?: string; language?: string }) =>
            apiFetch("/api/ai/audio-overview", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        videoOverview: (data: { topic: string; num_slides?: number; language?: string }) =>
            apiFetch("/api/ai/video-overview", {
                method: "POST",
                body: JSON.stringify(data),
            }),
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
