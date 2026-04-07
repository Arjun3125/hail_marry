"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, FileText, Loader2, Sparkles, Upload, Youtube } from "lucide-react";
import EmptyState from "@/components/EmptyState";
import { PrismInput, PrismSelect } from "@/components/prism/PrismControls";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type SubjectItem = { id: string; name: string };
type TeacherClass = { id: string; name: string; subjects: SubjectItem[] };
type UploadActivity = {
    id: string; name: string; type: "document" | "youtube"; status: "processing" | "completed" | "failed";
    detail?: string; ocrWarning?: string; ocrReviewRequired?: boolean; ocrPending?: boolean; ocrProcessed?: boolean; ocrConfidence?: number;
};
type AIJobStatus = "queued" | "running" | "completed" | "failed";

const ALLOWED_EXTENSIONS = ["pdf", "docx", "pptx", "xlsx", "jpg", "jpeg", "png"];
const MAX_FILE_SIZE = 50 * 1024 * 1024;

export default function UploadPage() {
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [subjectId, setSubjectId] = useState("");
    const [youtubeUrl, setYoutubeUrl] = useState("");
    const [youtubeTitle, setYoutubeTitle] = useState("");
    const [activities, setActivities] = useState<UploadActivity[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const allSubjects = useMemo(() => {
        const map = new Map<string, SubjectItem>();
        classes.forEach((c) => (c.subjects || []).forEach((s) => !map.has(s.id) && map.set(s.id, s)));
        return Array.from(map.values());
    }, [classes]);

    const summary = useMemo(() => ({
        docs: activities.filter((a) => a.type === "document").length,
        youtube: activities.filter((a) => a.type === "youtube").length,
        processing: activities.filter((a) => a.status === "processing").length,
        review: activities.filter((a) => a.ocrReviewRequired).length,
    }), [activities]);

    useEffect(() => {
        if (!allSubjects.some((s) => s.id === subjectId)) setSubjectId(allSubjects[0]?.id || "");
    }, [allSubjects, subjectId]);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true); setError(null);
                setClasses(((await api.teacher.classes()) || []) as TeacherClass[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load classes and subjects");
            } finally { setLoading(false); }
        };
        void load();
    }, []);

    const push = (item: UploadActivity) => setActivities((p) => [item, ...p]);
    const patch = (id: string, next: Partial<UploadActivity>) => setActivities((p) => p.map((a) => a.id === id ? { ...a, ...next } : a));

    const poll = async (activityId: string, jobId: string, done: (result?: Record<string, unknown>) => void) => {
        try {
            const job = (await api.ai.jobStatus(jobId)) as { status: AIJobStatus; error?: string; result?: Record<string, unknown>; poll_after_ms?: number };
            if (job.status === "completed") return done(job.result);
            if (job.status === "failed") return patch(activityId, { status: "failed", detail: job.error || "Ingestion failed" });
            window.setTimeout(() => void poll(activityId, jobId, done), job.poll_after_ms ?? 2000);
        } catch (err) {
            patch(activityId, { status: "failed", detail: err instanceof Error ? err.message : "Ingestion failed" });
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const fileList = e.target.files; if (!fileList) return; setError(null);
        for (const file of Array.from(fileList)) {
            const ext = file.name.split(".").pop()?.toLowerCase() || "";
            const id = `${Date.now()}-${file.name}-${Math.random().toString(36).slice(2, 8)}`;
            const isImage = ["jpg", "jpeg", "png"].includes(ext);
            push({ id, name: file.name, type: "document", status: "processing", ocrPending: isImage });
            if (!ALLOWED_EXTENSIONS.includes(ext)) { patch(id, { status: "failed", detail: "Only PDF, DOCX, PPTX, XLSX, JPG, PNG are allowed" }); continue; }
            if (file.size > MAX_FILE_SIZE) { patch(id, { status: "failed", detail: "File exceeds 50MB limit" }); continue; }
            try {
                const formData = new FormData(); formData.append("file", file);
                const payload = (await api.teacher.uploadDocument(formData)) as { success?: boolean; job_id?: string; error?: string; ocr_processed?: boolean; ocr_review_required?: boolean; ocr_warning?: string; ocr_confidence?: number };
                if (payload?.success === false) throw new Error(payload.error || "Upload failed");
                const base = { ocrProcessed: payload.ocr_processed, ocrReviewRequired: payload.ocr_review_required, ocrWarning: payload.ocr_warning, ocrConfidence: typeof payload.ocr_confidence === "number" ? payload.ocr_confidence : undefined };
                if (!payload.job_id) { patch(id, { status: "completed", detail: "Ingested", ...base }); continue; }
                patch(id, { status: "processing", detail: "Queued for ingestion" });
                void poll(id, payload.job_id, (result) => patch(id, { status: "completed", detail: `Ingested (${Number(result?.chunks ?? 0)} chunks)`, ...base }));
            } catch (err) {
                patch(id, { status: "failed", detail: err instanceof Error ? err.message : "Upload failed" });
            }
        }
        e.target.value = "";
    };

    const handleYoutubeSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!youtubeUrl.trim() || !youtubeTitle.trim() || !subjectId) return setError("YouTube URL, title, and subject are required");
        setError(null);
        const id = `${Date.now()}-youtube-${Math.random().toString(36).slice(2, 8)}`;
        push({ id, name: youtubeTitle.trim(), type: "youtube", status: "processing", detail: youtubeUrl.trim() });
        try {
            const payload = (await api.teacher.ingestYoutube({ url: youtubeUrl.trim(), title: youtubeTitle.trim(), subject_id: subjectId })) as { success?: boolean; job_id?: string; error?: string };
            if (payload?.success === false) throw new Error(payload.error || "YouTube ingestion failed");
            if (!payload.job_id) throw new Error("YouTube ingestion job was not created");
            patch(id, { status: "processing", detail: "Queued transcript ingestion" });
            void poll(id, payload.job_id, (result) => patch(id, { status: "completed", detail: `Transcript ingested (${Number(result?.chunks ?? 0)} chunks)` }));
            setYoutubeUrl(""); setYoutubeTitle("");
        } catch (err) {
            patch(id, { status: "failed", detail: err instanceof Error ? err.message : "YouTube ingestion failed" });
        }
    };

    return (
        <PrismPage className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker><Upload className="h-3.5 w-3.5" />Teacher Ingestion Surface</PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">Upload Notes</h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">Bring in classroom documents, image captures, and YouTube lectures from one teacher-facing workspace with OCR and ingestion feedback kept visible.</p>
                        </div>
                    </div>
                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <Metric icon={FileText} title="Documents" value={`${summary.docs}`} summary="Session file uploads" tone="blue" />
                        <Metric icon={Youtube} title="Lectures" value={`${summary.youtube}`} summary="YouTube ingests queued or done" tone="emerald" />
                        <Metric icon={Sparkles} title="Attention" value={`${summary.processing || summary.review}`} summary={summary.processing ? "Jobs still processing" : "OCR items flagged for review"} tone="amber" />
                    </div>
                </div>

                {error ? <ErrorRemediation error={error} scope="teacher-upload" onRetry={() => window.location.reload()} /> : null}

                <PrismPanel className="overflow-hidden p-0">
                    <div className="border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Ingestion workspace</p>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">Handle document upload, OCR-heavy image intake, and lecture ingestion without leaving the teacher workflow.</p>
                            </div>
                            <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">{allSubjects.length} subjects available</div>
                        </div>
                    </div>

                    <div className="grid gap-6 p-5 xl:grid-cols-[1.08fr_0.92fr]">
                        <div className="space-y-4">
                            <div className="grid gap-4 lg:grid-cols-2">
                                <PrismPanel className="p-5">
                                    <p className="mb-1 text-sm font-semibold text-[var(--text-primary)]">Document intake</p>
                                    <p className="mb-4 text-xs text-[var(--text-secondary)]">Upload notes, slides, spreadsheets, or image captures.</p>
                                    <label className="block cursor-pointer rounded-[28px] border border-dashed border-[var(--border)] bg-[rgba(8,15,30,0.52)] p-8 text-center transition hover:border-[var(--primary)]/40 hover:bg-[rgba(59,130,246,0.06)]">
                                        <Upload className="mx-auto mb-3 h-8 w-8 text-[var(--text-primary)]" />
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">Click to upload or drag files</p>
                                        <p className="mt-1 text-xs text-[var(--text-secondary)]">PDF, DOCX, PPTX, XLSX, JPG, PNG up to 50MB</p>
                                        <input type="file" accept=".pdf,.docx,.pptx,.xlsx,image/*" capture="environment" multiple onChange={handleFileUpload} className="hidden" />
                                    </label>
                                </PrismPanel>

                                <PrismPanel className="p-5">
                                    <p className="mb-1 text-sm font-semibold text-[var(--text-primary)]">Lecture ingestion</p>
                                    <p className="mb-4 text-xs text-[var(--text-secondary)]">Queue transcript ingestion for a YouTube lecture.</p>
                                    <form onSubmit={(e) => void handleYoutubeSubmit(e)} className="space-y-3">
                                        <PrismSelect value={subjectId} onChange={(e) => setSubjectId(e.target.value)} disabled={loading || allSubjects.length === 0} className="text-sm">
                                            {allSubjects.length === 0 ? <option value="">No subjects assigned</option> : allSubjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                                        </PrismSelect>
                                        <PrismInput type="text" value={youtubeTitle} onChange={(e) => setYoutubeTitle(e.target.value)} placeholder="Lecture title" className="text-sm" />
                                        <PrismInput type="url" value={youtubeUrl} onChange={(e) => setYoutubeUrl(e.target.value)} placeholder="Paste YouTube URL..." className="text-sm" />
                                        <button type="submit" disabled={loading || !subjectId || !youtubeUrl.trim() || !youtubeTitle.trim()} className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(239,68,68,0.96),rgba(249,115,22,0.92))] px-4 py-3 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(239,68,68,0.18)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"><Youtube className="h-4 w-4" />Ingest Lecture</button>
                                    </form>
                                </PrismPanel>
                            </div>

                            <PrismPanel className="overflow-hidden p-0">
                                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                                    <div><p className="text-sm font-semibold text-[var(--text-primary)]">Recent upload activity</p><p className="mt-1 text-xs text-[var(--text-secondary)]">OCR status, ingestion progress, and final indexing details stay visible in one ledger.</p></div>
                                    <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">{activities.length} session items</div>
                                </div>
                                <div className="p-5">
                                    {activities.length === 0 ? <EmptyState icon={Upload} title="No uploads in this session yet" description="Add a document or lecture above to begin building the teacher knowledge base." /> : <div className="space-y-3">{activities.map((a) => <Activity key={a.id} item={a} />)}</div>}
                                </div>
                            </PrismPanel>
                        </div>

                        <div className="space-y-4">
                            <PrismPanel className="p-5"><p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Session summary</p><div className="mt-4 space-y-3">{[
                                ["Subjects ready", `${allSubjects.length}`], ["Documents", `${summary.docs}`], ["YouTube ingests", `${summary.youtube}`], ["OCR review flags", `${summary.review}`],
                            ].map(([l, v]) => <Row key={l} label={l} value={v} />)}</div></PrismPanel>
                            <PrismPanel className="p-5"><p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Workflow notes</p><div className="mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]"><p>The intake flow stays unchanged: upload the file or lecture, queue the backend job if needed, then surface the final ingestion state in the same teacher workspace.</p><p>OCR metadata remains attached to each activity so low-confidence image captures are visible immediately instead of being hidden behind logs.</p></div></PrismPanel>
                        </div>
                    </div>
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}

function Metric({ icon: Icon, title, value, summary, tone }: { icon: typeof FileText; title: string; value: string; summary: string; tone: "blue" | "emerald" | "amber" }) {
    const tones = { blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))] text-status-blue", emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))] text-status-emerald", amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))] text-status-amber" } as const;
    return <PrismPanel className="p-4"><div className={`mb-3 flex h-11 w-11 items-center justify-center rounded-2xl ${tones[tone]}`}><Icon className="h-5 w-5" /></div><p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{title}</p><p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{value}</p><p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p></PrismPanel>;
}

function Row({ label, value }: { label: string; value: string }) {
    return <div className="flex items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-4 py-3"><span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</span><span className="text-sm font-medium text-[var(--text-primary)]">{value}</span></div>;
}

function Activity({ item }: { item: UploadActivity }) {
    const statusTone = item.status === "completed" ? "border-[rgba(16,185,129,0.18)] bg-[rgba(16,185,129,0.1)] text-status-emerald" : item.status === "failed" ? "border-[rgba(239,68,68,0.18)] bg-[rgba(239,68,68,0.1)] text-status-red" : "border-[rgba(96,165,250,0.18)] bg-[rgba(96,165,250,0.1)] text-status-blue";
    const StatusIcon = item.status === "completed" ? CheckCircle2 : item.status === "failed" ? AlertCircle : Loader2;
    return (
        <div className="rounded-[28px] border border-[var(--border)] bg-[rgba(8,15,30,0.58)] p-5 shadow-[0_18px_40px_rgba(2,6,23,0.16)]">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-start">
                <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2"><h2 className="text-base font-semibold text-[var(--text-primary)]">{item.name}</h2><span className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{item.type}</span></div>
                    <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.detail || "Pending update"}</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                        {item.status === "processing" && item.ocrPending ? <Tag text="OCR in progress" tone="info" /> : null}
                        {item.status === "completed" && item.ocrProcessed ? <Tag text="OCR completed" tone="success" /> : null}
                        {item.ocrReviewRequired ? <Tag text="OCR review recommended" tone="warning" /> : null}
                        {typeof item.ocrConfidence === "number" ? <Tag text={`OCR confidence ${Math.round(item.ocrConfidence * 100)}%`} tone="info" /> : null}
                        {item.ocrWarning ? <Tag text={item.ocrWarning} tone="warning" /> : null}
                    </div>
                </div>
                <div className={`inline-flex items-center gap-2 rounded-2xl border px-4 py-2 text-sm font-semibold ${statusTone}`}><StatusIcon className={`h-4 w-4 ${item.status === "processing" ? "animate-spin" : ""}`} /><span className="capitalize">{item.status}</span></div>
            </div>
        </div>
    );
}

function Tag({ text, tone }: { text: string; tone: "info" | "success" | "warning" }) {
    const tones = { info: "border-[rgba(96,165,250,0.18)] bg-[rgba(96,165,250,0.1)] text-status-blue", success: "border-[rgba(16,185,129,0.18)] bg-[rgba(16,185,129,0.1)] text-status-emerald", warning: "border-[rgba(251,191,36,0.18)] bg-[rgba(251,191,36,0.1)] text-status-amber" } as const;
    return <span className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${tones[tone]}`}>{text}</span>;
}
