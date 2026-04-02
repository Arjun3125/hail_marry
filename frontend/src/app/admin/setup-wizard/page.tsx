"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
    School,
    BookOpen,
    Users,
    Clock,
    CheckCircle2,
    ArrowRight,
    ArrowLeft,
    Upload,
    Download,
    Sparkles,
} from "lucide-react";

import { API_BASE, getStoredAccessToken } from "@/lib/api";

/* ─── Step definitions ────────────────────────────────────── */
const STEPS = [
    { id: "school", label: "School Info", icon: School },
    { id: "classes", label: "Classes", icon: BookOpen },
    { id: "teachers", label: "Teachers", icon: Users },
    { id: "students", label: "Students", icon: Users },
    { id: "timetable", label: "Timetable", icon: Clock },
    { id: "done", label: "Done!", icon: CheckCircle2 },
];

type TeacherPreviewRow = {
    name: string;
    email: string;
    password: string;
};

type StudentPreviewRow = {
    full_name: string;
    email: string;
    password: string;
    class_name: string;
};

type PreviewMode = "teachers" | "students";
type PreviewRow = TeacherPreviewRow | StudentPreviewRow;

/* ─── Component ───────────────────────────────────────────── */
export default function SetupWizard() {
    const [step, setStep] = useState(0);
    const [schoolName, setSchoolName] = useState("");
    const [board, setBoard] = useState("CBSE");
    const [classes, setClasses] = useState("");

    const [busy, setBusy] = useState(false);
    const [result, setResult] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [ocrNotice, setOcrNotice] = useState<string | null>(null);
    const [previewMode, setPreviewMode] = useState<PreviewMode | null>(null);
    const [previewRows, setPreviewRows] = useState<PreviewRow[]>([]);
    const [previewErrors, setPreviewErrors] = useState<string[]>([]);
    const [previewBusy, setPreviewBusy] = useState(false);

    useEffect(() => {
        if (typeof window === "undefined") return;
        window.localStorage.setItem(
            "mascotPageContext",
            JSON.stringify({
                route: "/admin/setup-wizard",
                current_page_entity: "setup_step",
                current_page_entity_id: STEPS[step]?.id || null,
                metadata: {
                    setup_step: STEPS[step]?.id || null,
                },
            }),
        );
    }, [step]);

    const next = () => setStep((s) => Math.min(STEPS.length - 1, s + 1));
    const prev = () => setStep((s) => Math.max(0, s - 1));

    const downloadTemplate = (type: string) => {
        const url = `${API_BASE}/api/admin/csv-template/${type}`;
        window.open(url, "_blank");
    };

    const resetPreview = () => {
        setPreviewMode(null);
        setPreviewRows([]);
        setPreviewErrors([]);
        setPreviewBusy(false);
    };

    const escapeCsvValue = (value: string) => {
        if (value.includes(",") || value.includes("\"") || value.includes("\n")) {
            return `"${value.replace(/"/g, "\"\"")}"`;
        }
        return value;
    };

    const buildCsvFromRows = (mode: PreviewMode, rows: PreviewRow[]) => {
        if (mode === "teachers") {
            const header = ["name", "email", "password"];
            const lines = rows.map((row) => {
                const data = row as TeacherPreviewRow;
                return [data.name, data.email, data.password].map((val) => escapeCsvValue(val || "")).join(",");
            });
            return `${header.join(",")}\n${lines.join("\n")}\n`;
        }
        const header = ["full_name", "email", "password", "class_name"];
        const lines = rows.map((row) => {
            const data = row as StudentPreviewRow;
            return [data.full_name, data.email, data.password, data.class_name].map((val) => escapeCsvValue(val || "")).join(",");
        });
        return `${header.join(",")}\n${lines.join("\n")}\n`;
    };

    const handleCSVUpload = async (endpoint: string, file: File) => {
        setBusy(true);
        setError(null);
        setOcrNotice(null);
        setPreviewErrors([]);
        try {
            const formData = new FormData();
            formData.append("file", file);
            const token = getStoredAccessToken();
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: "POST",
                headers: token ? { Authorization: `Bearer ${token}` } : {},
                credentials: "include",
                body: formData,
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Upload failed");
            const createdCount = Number(data.created || data.imported || 0);
            setResult(`✅ Imported ${createdCount} records successfully!`);
            const reviewRequired = Boolean(data.ocr_review_required);
            const warning = typeof data.ocr_warning === "string" ? data.ocr_warning : null;
            const confidence = typeof data.ocr_confidence === "number" ? data.ocr_confidence : null;
            const unmatchedLines = Array.isArray(data.ocr_unmatched_lines) ? data.ocr_unmatched_lines.length : 0;
            if (reviewRequired || warning || unmatchedLines || confidence !== null) {
                const parts = ["OCR extracted text from the upload."];
                if (confidence !== null) parts.push(`OCR confidence ${(confidence * 100).toFixed(0)}%.`);
                if (reviewRequired) parts.push("Review recommended before finalizing.");
                if (unmatchedLines) {
                    parts.push(`${unmatchedLines} line${unmatchedLines === 1 ? "" : "s"} need manual cleanup.`);
                }
                if (warning) parts.push(warning);
                setOcrNotice(parts.join(" "));
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Upload failed");
        } finally {
            setBusy(false);
        }
    };

    const handlePreviewUpload = async (endpoint: string, file: File, mode: PreviewMode) => {
        setPreviewBusy(true);
        setError(null);
        setResult(null);
        setOcrNotice(null);
        setPreviewErrors([]);
        setPreviewRows([]);
        setPreviewMode(mode);
        try {
            const formData = new FormData();
            formData.append("file", file);
            const token = getStoredAccessToken();
            const res = await fetch(`${API_BASE}${endpoint}?preview=1`, {
                method: "POST",
                headers: token ? { Authorization: `Bearer ${token}` } : {},
                credentials: "include",
                body: formData,
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Preview failed");
            const rows = Array.isArray(data.preview_rows) ? data.preview_rows : [];
            if (!rows.length) throw new Error("No rows detected in the preview.");
            setPreviewRows(rows as PreviewRow[]);
            setPreviewErrors(Array.isArray(data.errors) ? data.errors : []);
            const reviewRequired = Boolean(data.ocr_review_required);
            const warning = typeof data.ocr_warning === "string" ? data.ocr_warning : null;
            const confidence = typeof data.ocr_confidence === "number" ? data.ocr_confidence : null;
            const unmatchedLines = Array.isArray(data.ocr_unmatched_lines) ? data.ocr_unmatched_lines.length : Number(data.ocr_unmatched_lines || 0);
            if (reviewRequired || warning || unmatchedLines || confidence !== null) {
                const parts = ["Preview extracted rows from OCR."];
                if (confidence !== null) parts.push(`OCR confidence ${(confidence * 100).toFixed(0)}%.`);
                if (reviewRequired) parts.push("Review recommended before final import.");
                if (unmatchedLines) {
                    parts.push(`${unmatchedLines} line${unmatchedLines === 1 ? "" : "s"} need manual cleanup.`);
                }
                if (warning) parts.push(warning);
                setOcrNotice(parts.join(" "));
            }
        } catch (err) {
            resetPreview();
            setError(err instanceof Error ? err.message : "Preview failed");
        } finally {
            setPreviewBusy(false);
        }
    };

    const updatePreviewRow = (index: number, field: string, value: string) => {
        setPreviewRows((prev) =>
            prev.map((row, idx) => (idx === index ? ({ ...row, [field]: value } as PreviewRow) : row)),
        );
    };

    const confirmPreviewImport = async () => {
        if (!previewMode || previewRows.length === 0) return;
        const csv = buildCsvFromRows(previewMode, previewRows);
        const file = new File([csv], `${previewMode}-import.csv`, { type: "text/csv" });
        const endpoint = previewMode === "teachers" ? "/api/admin/onboard-teachers" : "/api/admin/onboard-students";
        await handleCSVUpload(endpoint, file);
        resetPreview();
    };

    return (
        <div className="max-w-5xl mx-auto py-4 sm:py-8 relative">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[80%] h-[400px] bg-gradient-to-b from-[var(--primary)]/5 to-transparent blur-[100px] -z-10 rounded-full pointer-events-none" />
            
            <div className="mb-12 text-center stagger-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 mb-4 rounded-full glass-panel border-[var(--border)] text-[var(--primary)] text-sm font-medium shadow-[0_0_20px_rgba(var(--primary-rgb),0.1)]">
                    <Sparkles className="w-4 h-4" />
                    Interactive Setup
                </div>
                <h1 className="text-3xl md:text-5xl font-extrabold text-[var(--text-primary)] tracking-tight">
                    School <span className="premium-gradient">Setup Wizard</span>
                </h1>
                <p className="text-base text-[var(--text-secondary)] mt-4 max-w-lg mx-auto font-light">
                    Activate your digital infrastructure. Complete the core modules below to initialize the system.
                </p>
            </div>

            {/* ─── Glowing Progress Bar ─── */}
            <div className="flex items-center justify-between mb-16 relative stagger-2 px-4 sm:px-10">
                <div className="absolute top-5 left-10 right-10 h-1 bg-[var(--border)] -translate-y-1/2 rounded-full -z-10" />
                <div 
                    className="absolute top-5 left-10 h-1 bg-gradient-to-r from-indigo-500 to-cyan-500 -translate-y-1/2 rounded-full -z-10 transition-all duration-700 ease-out shadow-[0_0_15px_rgba(99,102,241,0.6)]" 
                    style={{ width: `calc(${(step / (STEPS.length - 1)) * 100}% - 2.5rem)` }}
                />
                
                {STEPS.map((s, i) => {
                    const isActive = i === step;
                    const isPast = i < step;
                    return (
                        <div key={s.id} className="flex flex-col items-center gap-3 cursor-pointer group relative" onClick={() => i <= step && setStep(i)}>
                            {isActive && (
                                <div className="absolute top-0 w-12 h-12 bg-[var(--primary)] blur-xl opacity-40 rounded-full animate-pulse z-0" />
                            )}
                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center relative z-10 transition-all duration-300 ${isActive ? 'bg-gradient-to-br from-indigo-500 to-cyan-500 text-white shadow-xl shadow-indigo-500/40 scale-110' : isPast ? 'bg-[var(--success)] text-white shadow-md' : 'glass-panel text-[var(--text-muted)] group-hover:border-[var(--text-secondary)] group-hover:scale-105'}`}>
                                <s.icon className="w-5 h-5" />
                            </div>
                            <span className={`hidden sm:block text-[10px] sm:text-xs font-bold tracking-wider uppercase transition-colors ${isActive ? 'premium-text' : isPast ? 'text-[var(--text-primary)]' : 'text-[var(--text-muted)]'}`}>
                                {s.label}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* ─── Feedback ─── */}
            <div className="stagger-3 mb-6">
                {error && (
                    <div className="rounded-2xl border border-[var(--error)]/30 bg-error-subtle px-5 py-4 text-sm text-[var(--error)] flex items-center gap-3 shadow-lg shadow-[var(--error)]/5">
                        <div className="w-2 h-2 rounded-full bg-[var(--error)] animate-pulse shrink-0" />
                        {error}
                    </div>
                )}
                {result && (
                    <div className="rounded-2xl border border-success-subtle bg-success-subtle px-5 py-4 text-sm text-[var(--success)] flex items-center gap-3 shadow-lg shadow-[var(--success)]/5">
                        <CheckCircle2 className="w-5 h-5 shrink-0" />
                        {result}
                    </div>
                )}
                {ocrNotice && (
                    <div className="mt-4 rounded-2xl border border-[var(--warning)]/30 bg-warning-subtle px-5 py-4 text-sm text-[var(--warning)] flex items-start gap-3 shadow-lg shadow-[var(--warning)]/5">
                        <Sparkles className="w-5 h-5 mt-0.5 shrink-0" />
                        <span>{ocrNotice}</span>
                    </div>
                )}
            </div>

            {/* ─── Step content ─── */}
            <div className="glass-panel rounded-3xl p-6 sm:p-12 shadow-2xl min-h-[400px] relative overflow-hidden stagger-4">
                {/* Decorative background glow for active card */}
                <div className="absolute -top-32 -right-32 w-64 h-64 bg-indigo-500/10 blur-[80px] rounded-full pointer-events-none" />

                {/* Step 0: School Info */}
                {step === 0 && (
                    <div className="space-y-6 relative z-10 animate-fade-in">
                        <div>
                            <h2 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight">Institutional Profile</h2>
                            <p className="text-sm text-[var(--text-secondary)] mt-2 font-medium">
                                Establish your core identity across the platform.
                            </p>
                        </div>
                        <div className="space-y-5 pt-4">
                            <div>
                                <label className="block text-sm font-semibold text-[var(--text-primary)] mb-2">Institution Code / Name</label>
                                <input
                                    type="text"
                                    value={schoolName}
                                    onChange={(e) => setSchoolName(e.target.value)}
                                    placeholder="e.g., Delhi Public School, Pune"
                                    className="w-full px-5 py-3.5 text-sm bg-[var(--bg-page)]/50 border border-[var(--border-strong)] rounded-2xl focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition-all shadow-inner placeholder:text-[var(--text-muted)]"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-[var(--text-primary)] mb-2">Curriculum Board</label>
                                <select
                                    value={board}
                                    onChange={(e) => setBoard(e.target.value)}
                                    className="w-full px-5 py-3.5 text-sm bg-[var(--bg-page)]/50 border border-[var(--border-strong)] rounded-2xl focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition-all shadow-inner appearance-none cursor-pointer"
                                    style={{ backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%239CA3AF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 1rem top 50%', backgroundSize: '0.65rem auto' }}
                                >
                                    <option value="CBSE">Central Board (CBSE)</option>
                                    <option value="ICSE">Council for School Certificate (ICSE)</option>
                                    <option value="State Board">State Board Curriculum</option>
                                    <option value="IB">International Baccalaureate (IB)</option>
                                    <option value="Other">Custom / Other</option>
                                </select>
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 1: Classes */}
                {step === 1 && (
                    <div className="space-y-6 relative z-10 animate-fade-in">
                        <div>
                            <h2 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight">Define Cohorts</h2>
                            <p className="text-sm text-[var(--text-secondary)] mt-2 font-medium">
                                Map out the physical or virtual classes operating within the system.
                            </p>
                        </div>
                        <div className="pt-2">
                            <textarea
                                value={classes}
                                onChange={(e) => setClasses(e.target.value)}
                                placeholder={"Class 10-A\\nClass 10-B\\nClass 11-Science\\nClass 12-Commerce"}
                                rows={8}
                                className="w-full px-5 py-4 text-sm bg-[var(--bg-page)]/50 border border-[var(--border-strong)] rounded-2xl focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition-all shadow-inner font-mono resize-y placeholder:text-[var(--text-muted)] leading-relaxed"
                            />
                            <p className="text-xs font-semibold text-[var(--text-muted)] mt-4 flex items-center gap-2">
                                <CheckCircle2 className="w-4 h-4 text-[var(--success)]" />
                                Separate each cohort by a new line. You can append more later globally.
                            </p>
                        </div>
                    </div>
                )}

                {/* Step 2: Teachers */}
                {step === 2 && (
                    <div className="space-y-6 relative z-10 animate-fade-in">
                        <div>
                            <h2 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight">Onboard Educators</h2>
                            <p className="text-sm text-[var(--text-secondary)] mt-2 font-medium">
                                Inject teacher sub-nets via CSV or intelligent OCR roster extraction.
                            </p>
                        </div>
                        
                        {!previewMode && (
                            <div className="flex flex-col sm:flex-row gap-5 pt-4">
                                <label className="flex-1 group relative cursor-pointer">
                                    <div className="absolute inset-0 bg-gradient-to-br from-[var(--primary)] to-cyan-500 rounded-3xl blur opacity-20 group-hover:opacity-40 transition-opacity" />
                                    <div className="relative h-full flex flex-col items-center justify-center p-8 glass-panel border-[var(--border-strong)] rounded-3xl group-hover:border-[var(--primary)] transition-colors text-center shadow-lg">
                                        <div className="w-14 h-14 bg-[var(--primary)]/10 text-[var(--primary)] rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                            <Upload className="w-7 h-7" />
                                        </div>
                                        <h3 className="text-lg font-bold text-[var(--text-primary)] mb-1">Optical Extraction</h3>
                                        <p className="text-sm font-medium text-[var(--text-secondary)]">Drop CSV or Excel Screenshot</p>
                                    </div>
                                    <input
                                        type="file"
                                        accept=".csv,image/*"
                                        capture="environment"
                                        className="hidden"
                                        onChange={(e) => {
                                            const file = e.target.files?.[0];
                                            if (file) handlePreviewUpload("/api/admin/onboard-teachers", file, "teachers");
                                        }}
                                        disabled={busy}
                                    />
                                </label>

                                <button
                                    onClick={() => downloadTemplate("teachers")}
                                    className="flex-1 flex flex-col items-center justify-center p-8 glass-panel rounded-3xl hover:bg-[var(--bg-page)] transition-colors text-center group border-[var(--border-strong)]"
                                >
                                    <div className="w-14 h-14 bg-[var(--bg-page)] border border-[var(--border)] text-[var(--text-secondary)] rounded-full flex items-center justify-center mb-4 group-hover:text-[var(--primary)] transition-colors">
                                        <Download className="w-7 h-7" />
                                    </div>
                                    <h3 className="text-lg font-bold text-[var(--text-primary)] mb-1">CSV Template</h3>
                                    <p className="text-sm font-medium text-[var(--text-secondary)]">Download strict format</p>
                                </button>
                            </div>
                        )}

                        {previewMode === "teachers" && previewRows.length > 0 ? (
                            <div className="mt-6 rounded-3xl border border-[var(--border-strong)] bg-[var(--bg-page)]/80 backdrop-blur-md overflow-hidden shadow-2xl">
                                <div className="px-6 py-5 border-b border-[var(--border)] flex flex-wrap gap-4 items-center justify-between bg-gradient-to-r from-[var(--bg-page)] to-transparent">
                                    <div>
                                        <p className="text-base font-bold text-[var(--text-primary)] flex items-center gap-2">
                                            <Sparkles className="w-5 h-5 text-[var(--primary)]" />
                                            Extracted Dataset
                                        </p>
                                        <p className="text-xs font-medium text-[var(--text-muted)] mt-1 tracking-wide">EDIT INLINE TO CORRECT CONFIDENCE ERRORS.</p>
                                    </div>
                                    {previewBusy ? <span className="text-xs font-bold premium-text animate-pulse bg-[var(--primary)]/10 px-3 py-1.5 rounded-full">Processing Vision API...</span> : null}
                                </div>
                                
                                {previewErrors.length > 0 && (
                                    <div className="mx-6 mt-4 rounded-xl border border-[var(--warning)]/30 bg-warning-subtle px-4 py-3 text-xs font-semibold text-[var(--warning)] shadow-inner">
                                        {previewErrors.join(" ")}
                                    </div>
                                )}
                                
                                <div className="p-2 sm:p-6 overflow-x-auto">
                                    <table className="w-full min-w-[600px] border-collapse">
                                        <thead>
                                            <tr className="border-b-2 border-[var(--border)] text-[10px] sm:text-xs font-black text-[var(--text-muted)] tracking-wider">
                                                <th className="pb-3 px-3 text-left w-1/3">EDUCATOR NAME</th>
                                                <th className="pb-3 px-3 text-left w-1/3">EMAIL ADDRESS</th>
                                                <th className="pb-3 px-3 text-left w-1/3">INITIAL PASSWORD</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {(previewRows as TeacherPreviewRow[]).map((row, idx) => (
                                                <tr key={`${row.email}-${idx}`} className="border-b border-[var(--border-light)] group hover:bg-[var(--bg-card)] transition-colors">
                                                    <td className="p-2">
                                                        <input
                                                            value={row.name}
                                                            onChange={(e) => updatePreviewRow(idx, "name", e.target.value)}
                                                            className="w-full text-sm font-semibold text-[var(--text-primary)] bg-transparent border-b-2 border-transparent focus:border-[var(--primary)] focus:bg-[var(--bg-page)] focus:outline-none transition-all px-2 py-2 rounded-t"
                                                        />
                                                    </td>
                                                    <td className="p-2">
                                                        <input
                                                            value={row.email}
                                                            onChange={(e) => updatePreviewRow(idx, "email", e.target.value)}
                                                            className="w-full text-sm font-medium text-[var(--text-secondary)] bg-transparent border-b-2 border-transparent focus:border-[var(--primary)] focus:bg-[var(--bg-page)] focus:outline-none transition-all px-2 py-2 rounded-t"
                                                        />
                                                    </td>
                                                    <td className="p-2">
                                                        <input
                                                            value={row.password}
                                                            onChange={(e) => updatePreviewRow(idx, "password", e.target.value)}
                                                            className="w-full text-sm font-mono text-[var(--text-muted)] bg-transparent border-b-2 border-transparent focus:border-[var(--primary)] focus:bg-[var(--bg-page)] focus:outline-none transition-all px-2 py-2 rounded-t"
                                                        />
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="px-6 py-5 border-t border-[var(--border)] bg-gradient-to-r from-[var(--bg-page)] to-[var(--bg-card)] flex flex-wrap gap-4">
                                    <button
                                        onClick={() => void confirmPreviewImport()}
                                        disabled={busy || previewBusy}
                                        className="px-8 py-3 text-sm font-bold bg-[var(--primary)] text-white rounded-full hover:bg-[var(--primary-hover)] transition-colors disabled:opacity-60 shadow-[0_0_15px_rgba(var(--primary-rgb),0.3)] hover:scale-105"
                                    >
                                        Execute Import
                                    </button>
                                    <button
                                        onClick={resetPreview}
                                        className="px-8 py-3 text-sm font-bold glass-panel border-[var(--border-strong)] rounded-full text-[var(--text-secondary)] hover:border-[var(--text-primary)] hover:text-[var(--text-primary)] transition-colors"
                                    >
                                        Discard Dataset
                                    </button>
                                </div>
                            </div>
                        ) : null}
                    </div>
                )}

                {/* Step 3: Students */}
                {step === 3 && (
                    <div className="space-y-6 relative z-10 animate-fade-in">
                        <div>
                            <h2 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight">Onboard Learners</h2>
                            <p className="text-sm text-[var(--text-secondary)] mt-2 font-medium">
                                Inject student nodes. Cohort mapping will auto-generate if missing.
                            </p>
                        </div>
                        
                        {!previewMode && (
                            <div className="flex flex-col sm:flex-row gap-5 pt-4">
                                <label className="flex-1 group relative cursor-pointer">
                                    <div className="absolute inset-0 bg-gradient-to-br from-amber-500 to-orange-500 rounded-3xl blur opacity-20 group-hover:opacity-40 transition-opacity" />
                                    <div className="relative h-full flex flex-col items-center justify-center p-8 glass-panel border-[var(--border-strong)] rounded-3xl group-hover:border-amber-500 transition-colors text-center shadow-lg">
                                        <div className="w-14 h-14 bg-amber-500/10 text-amber-500 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                            <Upload className="w-7 h-7" />
                                        </div>
                                        <h3 className="text-lg font-bold text-[var(--text-primary)] mb-1">Optical Extraction</h3>
                                        <p className="text-sm font-medium text-[var(--text-secondary)]">Drop CSV or Excel Screenshot</p>
                                    </div>
                                    <input
                                        type="file"
                                        accept=".csv,image/*"
                                        capture="environment"
                                        className="hidden"
                                        onChange={(e) => {
                                            const file = e.target.files?.[0];
                                            if (file) handlePreviewUpload("/api/admin/onboard-students", file, "students");
                                        }}
                                        disabled={busy}
                                    />
                                </label>

                                <button
                                    onClick={() => downloadTemplate("students")}
                                    className="flex-1 flex flex-col items-center justify-center p-8 glass-panel rounded-3xl hover:bg-[var(--bg-page)] transition-colors text-center group border-[var(--border-strong)]"
                                >
                                    <div className="w-14 h-14 bg-[var(--bg-page)] border border-[var(--border)] text-[var(--text-secondary)] rounded-full flex items-center justify-center mb-4 group-hover:text-amber-500 transition-colors">
                                        <Download className="w-7 h-7" />
                                    </div>
                                    <h3 className="text-lg font-bold text-[var(--text-primary)] mb-1">CSV Template</h3>
                                    <p className="text-sm font-medium text-[var(--text-secondary)]">Download strict format</p>
                                </button>
                            </div>
                        )}

                        {previewMode === "students" && previewRows.length > 0 ? (
                            <div className="mt-6 rounded-3xl border border-[var(--border-strong)] bg-[var(--bg-page)]/80 backdrop-blur-md overflow-hidden shadow-2xl">
                                <div className="px-6 py-5 border-b border-[var(--border)] flex flex-wrap gap-4 items-center justify-between bg-gradient-to-r from-[var(--bg-page)] to-transparent">
                                    <div>
                                        <p className="text-base font-bold text-[var(--text-primary)] flex items-center gap-2">
                                            <Sparkles className="w-5 h-5 text-amber-500" />
                                            Extracted Dataset
                                        </p>
                                        <p className="text-xs font-medium text-[var(--text-muted)] mt-1 tracking-wide">EDIT INLINE ANOMALIES BEFORE COMMITMENT.</p>
                                    </div>
                                    {previewBusy ? <span className="text-xs font-bold text-amber-500 animate-pulse bg-amber-500/10 px-3 py-1.5 rounded-full">Processing Vision API...</span> : null}
                                </div>
                                
                                {previewErrors.length > 0 && (
                                    <div className="mx-6 mt-4 rounded-xl border border-[var(--warning)]/30 bg-warning-subtle px-4 py-3 text-xs font-semibold text-[var(--warning)] shadow-inner">
                                        {previewErrors.join(" ")}
                                    </div>
                                )}
                                
                                <div className="p-2 sm:p-6 overflow-x-auto">
                                    <table className="w-full min-w-[800px] border-collapse">
                                        <thead>
                                            <tr className="border-b-2 border-[var(--border)] text-[10px] sm:text-xs font-black text-[var(--text-muted)] tracking-wider">
                                                <th className="pb-3 px-3 text-left w-1/4">FULL NAME</th>
                                                <th className="pb-3 px-3 text-left w-1/4">EMAIL</th>
                                                <th className="pb-3 px-3 text-left w-1/4">INITIAL PASSWORD</th>
                                                <th className="pb-3 px-3 text-left w-1/4">COHORT ID</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {(previewRows as StudentPreviewRow[]).map((row, idx) => (
                                                <tr key={`${row.email}-${idx}`} className="border-b border-[var(--border-light)] group hover:bg-[var(--bg-card)] transition-colors">
                                                    <td className="p-2">
                                                        <input
                                                            value={row.full_name}
                                                            onChange={(e) => updatePreviewRow(idx, "full_name", e.target.value)}
                                                            className="w-full text-sm font-semibold text-[var(--text-primary)] bg-transparent border-b-2 border-transparent focus:border-amber-500 focus:bg-[var(--bg-page)] focus:outline-none transition-all px-2 py-2 rounded-t"
                                                        />
                                                    </td>
                                                    <td className="p-2">
                                                        <input
                                                            value={row.email}
                                                            onChange={(e) => updatePreviewRow(idx, "email", e.target.value)}
                                                            className="w-full text-sm font-medium text-[var(--text-secondary)] bg-transparent border-b-2 border-transparent focus:border-amber-500 focus:bg-[var(--bg-page)] focus:outline-none transition-all px-2 py-2 rounded-t"
                                                        />
                                                    </td>
                                                    <td className="p-2">
                                                        <input
                                                            value={row.password}
                                                            onChange={(e) => updatePreviewRow(idx, "password", e.target.value)}
                                                            className="w-full text-sm font-mono text-[var(--text-muted)] bg-transparent border-b-2 border-transparent focus:border-amber-500 focus:bg-[var(--bg-page)] focus:outline-none transition-all px-2 py-2 rounded-t"
                                                        />
                                                    </td>
                                                    <td className="p-2">
                                                        <input
                                                            value={row.class_name}
                                                            onChange={(e) => updatePreviewRow(idx, "class_name", e.target.value)}
                                                            className="w-full inline-flex items-center px-3 py-1.5 rounded-xl border border-[var(--border-strong)] bg-[var(--bg-page)] text-xs font-bold text-[var(--text-primary)] focus:border-amber-500 focus:outline-none shadow-sm transition-all"
                                                        />
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="px-6 py-5 border-t border-[var(--border)] bg-gradient-to-r from-[var(--bg-page)] to-[var(--bg-card)] flex flex-wrap gap-4">
                                    <button
                                        onClick={() => void confirmPreviewImport()}
                                        disabled={busy || previewBusy}
                                        className="px-8 py-3 text-sm font-bold bg-amber-500 text-white rounded-full hover:bg-amber-600 transition-colors disabled:opacity-60 shadow-[0_0_15px_rgba(245,158,11,0.3)] hover:scale-105"
                                    >
                                        Execute Import
                                    </button>
                                    <button
                                        onClick={resetPreview}
                                        className="px-8 py-3 text-sm font-bold glass-panel border-[var(--border-strong)] rounded-full text-[var(--text-secondary)] hover:border-[var(--text-primary)] hover:text-[var(--text-primary)] transition-colors"
                                    >
                                        Discard Dataset
                                    </button>
                                </div>
                            </div>
                        ) : null}
                    </div>
                )}

                {/* Step 4: Timetable */}
                {step === 4 && (
                    <div className="space-y-6 relative z-10 animate-fade-in">
                        <div>
                            <h2 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight">Sync Schedules</h2>
                            <p className="text-sm text-[var(--text-secondary)] mt-2 font-medium">
                                Map teachers and subjects to specific cohorts globally.
                            </p>
                        </div>
                        <div className="p-12 rounded-3xl glass-panel border-[var(--border-strong)] text-center shadow-inner mt-4 relative overflow-hidden group">
                            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5" />
                            <div className="absolute -inset-2 bg-gradient-to-br from-purple-500/20 to-pink-500/20 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
                            
                            <div className="relative z-10">
                                <div className="w-24 h-24 bg-gradient-to-br from-[var(--bg-card)] to-[var(--bg-page)] border border-[var(--border-strong)] rounded-full flex items-center justify-center mx-auto mb-8 shadow-xl shadow-purple-500/10 group-hover:scale-110 transition-transform duration-500">
                                    <Clock className="w-10 h-10 text-[var(--text-primary)]" />
                                </div>
                                <h3 className="text-2xl font-black text-[var(--text-primary)] mb-3 tracking-tight">Timetable Protocol Required</h3>
                                <p className="text-base text-[var(--text-secondary)] max-w-sm mx-auto mb-10 leading-relaxed">
                                    Schedule generation requires complex matrix mapping. Please utilize the dedicated Master Timetable utility to assign rosters.
                                </p>
                                <Link
                                    href="/admin/timetable"
                                    className="inline-flex items-center gap-3 px-8 py-4 bg-[var(--text-primary)] text-[var(--bg-page)] text-sm font-bold rounded-full hover:scale-105 transition-transform shadow-xl hover:shadow-[0_0_20px_rgba(255,255,255,0.2)]"
                                >
                                    Launch Timetable Engine
                                    <ArrowRight className="w-5 h-5" />
                                </Link>
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 5: Done */}
                {step === 5 && (
                    <div className="text-center py-16 space-y-8 relative z-10 animate-fade-in">
                        <div className="relative w-32 h-32 mx-auto">
                            <div className="absolute inset-0 bg-emerald-500 blur-2xl opacity-40 rounded-full animate-pulse" />
                            <div className="relative w-full h-full rounded-[2rem] bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-2xl shadow-emerald-500/40">
                                <CheckCircle2 className="w-14 h-14 text-white" />
                            </div>
                        </div>
                        <div>
                            <h2 className="text-4xl md:text-5xl font-extrabold text-[var(--text-primary)] tracking-tight">System Online</h2>
                            <p className="text-lg text-[var(--text-secondary)] max-w-md mx-auto mt-4 leading-relaxed font-medium">
                                The institution graph has been initialized. Credentials have been primed for distribution.
                            </p>
                        </div>
                        <div className="flex flex-col sm:flex-row justify-center gap-5 pt-8">
                            <Link
                                href="/admin/dashboard"
                                className="inline-flex items-center justify-center gap-3 px-10 py-4 bg-[var(--primary)] text-white text-base font-bold rounded-full hover:bg-[var(--primary-hover)] transition-all shadow-xl shadow-[var(--primary)]/30 hover:scale-105"
                            >
                                Enter Admin Terminal
                                <ArrowRight className="w-5 h-5" />
                            </Link>
                            <Link
                                href="/admin/users"
                                className="inline-flex items-center justify-center gap-3 px-10 py-4 glass-panel border-[var(--border-strong)] text-[var(--text-primary)] text-base font-bold rounded-full hover:border-[var(--text-primary)] transition-all hover:-translate-y-1 shadow-md"
                            >
                                Inspect Users Node
                            </Link>
                        </div>
                    </div>
                )}
            </div>

            {/* ─── Navigation buttons ─── */}
            {step < 5 && (
                <div className="flex justify-between mt-10 stagger-5 px-2">
                    <button
                        onClick={prev}
                        disabled={step === 0}
                        className="flex items-center gap-2 px-8 py-3.5 text-sm font-bold text-[var(--text-secondary)] rounded-full glass-panel border-[var(--border-strong)] hover:border-[var(--text-primary)] hover:text-[var(--text-primary)] transition-all disabled:opacity-30 disabled:pointer-events-none shadow-md"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        Retreat
                    </button>
                    <button
                        onClick={next}
                        className="flex items-center gap-2 px-8 py-3.5 text-sm font-bold bg-[var(--text-primary)] text-[var(--bg-page)] rounded-full hover:scale-105 transition-transform shadow-xl shadow-[var(--text-primary)]/10"
                    >
                        {step === 4 ? "Finalize Submittal" : "Advance Pipeline"}
                        <ArrowRight className="w-5 h-5" />
                    </button>
                </div>
            )}
        </div>
    );
}
