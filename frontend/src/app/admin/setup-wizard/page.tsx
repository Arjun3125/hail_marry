"use client";

import { useState } from "react";
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

/* ─── Component ───────────────────────────────────────────── */
export default function SetupWizard() {
    const [step, setStep] = useState(0);
    const [schoolName, setSchoolName] = useState("");
    const [board, setBoard] = useState("CBSE");
    const [classes, setClasses] = useState("");

    const [busy, setBusy] = useState(false);
    const [result, setResult] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const next = () => setStep((s) => Math.min(STEPS.length - 1, s + 1));
    const prev = () => setStep((s) => Math.max(0, s - 1));

    const downloadTemplate = (type: string) => {
        const url = `${API_BASE}/api/admin/csv-template/${type}`;
        window.open(url, "_blank");
    };

    const handleCSVUpload = async (endpoint: string, file: File) => {
        setBusy(true);
        setError(null);
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
            setResult(`✅ Imported ${data.created || data.imported || 0} records successfully!`);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Upload failed");
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                    <Sparkles className="w-6 h-6 inline mr-2 text-[var(--primary)]" />
                    School Setup Wizard
                </h1>
                <p className="text-sm text-[var(--text-secondary)] mt-1">
                    Get your school running in minutes. Follow the steps below.
                </p>
            </div>

            {/* ─── Progress bar ─── */}
            <div className="flex items-center gap-1 mb-8">
                {STEPS.map((s, i) => (
                    <div key={s.id} className="flex items-center flex-1">
                        <div
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer ${i === step
                                ? "bg-[var(--primary)] text-white shadow-md"
                                : i < step
                                    ? "bg-success-badge text-status-green"
                                    : "bg-[var(--bg-card)] text-[var(--text-muted)] border border-[var(--border)]"
                                }`}
                            onClick={() => i <= step && setStep(i)}
                        >
                            <s.icon className="w-3.5 h-3.5" />
                            <span className="hidden sm:inline">{s.label}</span>
                        </div>
                        {i < STEPS.length - 1 && (
                            <div className={`h-[2px] flex-1 mx-1 ${i < step ? "bg-green-400" : "bg-[var(--border)]"}`} />
                        )}
                    </div>
                ))}
            </div>

            {/* ─── Feedback ─── */}
            {error && (
                <div className="mb-4 rounded-lg border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            )}
            {result && (
                <div className="mb-4 rounded-lg border border-success-subtle bg-success-subtle px-4 py-3 text-sm text-status-green">
                    {result}
                </div>
            )}

            {/* ─── Step content ─── */}
            <div className="bg-[var(--bg-card)] rounded-xl p-6 shadow-[var(--shadow-card)] min-h-[320px]">

                {/* Step 0: School Info */}
                {step === 0 && (
                    <div className="space-y-5">
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">School Information</h2>
                        <p className="text-sm text-[var(--text-secondary)]">
                            Basic details about your institution.
                        </p>
                        <div>
                            <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">School Name</label>
                            <input
                                type="text"
                                value={schoolName}
                                onChange={(e) => setSchoolName(e.target.value)}
                                placeholder="e.g., Delhi Public School, Pune"
                                className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-[var(--text-primary)] mb-1">Education Board</label>
                            <select
                                value={board}
                                onChange={(e) => setBoard(e.target.value)}
                                className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                            >
                                <option value="CBSE">CBSE</option>
                                <option value="ICSE">ICSE</option>
                                <option value="State Board">State Board</option>
                                <option value="IB">IB (International)</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                    </div>
                )}

                {/* Step 1: Classes */}
                {step === 1 && (
                    <div className="space-y-5">
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Add Classes</h2>
                        <p className="text-sm text-[var(--text-secondary)]">
                            Enter your class names, one per line. Example: Class 1A, Class 2B, etc.
                        </p>
                        <textarea
                            value={classes}
                            onChange={(e) => setClasses(e.target.value)}
                            placeholder={"Class 1A\nClass 1B\nClass 2A\nClass 2B\nClass 3A"}
                            rows={8}
                            className="w-full px-4 py-3 text-sm border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] font-mono"
                        />
                        <p className="text-xs text-[var(--text-muted)]">
                            Tip: You can also add classes later from the Classes page.
                        </p>
                    </div>
                )}

                {/* Step 2: Teachers */}
                {step === 2 && (
                    <div className="space-y-5">
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Add Teachers</h2>
                        <p className="text-sm text-[var(--text-secondary)]">
                            Upload a CSV file with teacher details, or add them manually later.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => downloadTemplate("teachers")}
                                className="flex items-center gap-2 px-4 py-2.5 border border-[var(--border)] rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors"
                            >
                                <Download className="w-4 h-4" />
                                Download Template
                            </button>
                            <label className="flex items-center gap-2 px-4 py-2.5 bg-[var(--primary)] text-white rounded-lg text-sm font-medium cursor-pointer hover:bg-[var(--primary-hover)] transition-colors">
                                <Upload className="w-4 h-4" />
                                Upload CSV
                                <input
                                    type="file"
                                    accept=".csv"
                                    className="hidden"
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) handleCSVUpload("/api/admin/onboard-teachers", file);
                                    }}
                                    disabled={busy}
                                />
                            </label>
                        </div>
                        <div className="p-4 rounded-lg bg-[var(--bg-page)] border border-[var(--border)]">
                            <p className="text-xs font-medium text-[var(--text-primary)] mb-2">CSV Format:</p>
                            <code className="text-xs text-[var(--text-muted)] font-mono">
                                full_name,email,password<br />
                                Priya Sharma,priya@school.com,Welcome@123<br />
                                Raj Patel,raj@school.com,Welcome@123
                            </code>
                        </div>
                    </div>
                )}

                {/* Step 3: Students */}
                {step === 3 && (
                    <div className="space-y-5">
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Add Students</h2>
                        <p className="text-sm text-[var(--text-secondary)]">
                            Upload a CSV file with student details. You can also use the OCR Photo feature later.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => downloadTemplate("students")}
                                className="flex items-center gap-2 px-4 py-2.5 border border-[var(--border)] rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors"
                            >
                                <Download className="w-4 h-4" />
                                Download Template
                            </button>
                            <label className="flex items-center gap-2 px-4 py-2.5 bg-[var(--primary)] text-white rounded-lg text-sm font-medium cursor-pointer hover:bg-[var(--primary-hover)] transition-colors">
                                <Upload className="w-4 h-4" />
                                Upload CSV
                                <input
                                    type="file"
                                    accept=".csv"
                                    className="hidden"
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) handleCSVUpload("/api/admin/onboard-students", file);
                                    }}
                                    disabled={busy}
                                />
                            </label>
                        </div>
                        <div className="p-4 rounded-lg bg-[var(--bg-page)] border border-[var(--border)]">
                            <p className="text-xs font-medium text-[var(--text-primary)] mb-2">CSV Format:</p>
                            <code className="text-xs text-[var(--text-muted)] font-mono">
                                full_name,email,password,class_name<br />
                                Ananya Kumari,ananya@school.com,Student@123,Class 9A<br />
                                Vikram Singh,vikram@school.com,Student@123,Class 9B
                            </code>
                        </div>
                    </div>
                )}

                {/* Step 4: Timetable */}
                {step === 4 && (
                    <div className="space-y-5">
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Setup Timetable</h2>
                        <p className="text-sm text-[var(--text-secondary)]">
                            You can set up each class&apos;s weekly timetable from the Timetable management page.
                        </p>
                        <div className="p-6 rounded-lg bg-[var(--bg-page)] border border-[var(--border)] text-center">
                            <Clock className="w-12 h-12 mx-auto text-[var(--text-muted)] mb-3" />
                            <p className="text-sm text-[var(--text-secondary)] mb-4">
                                Timetable setup requires classes and teachers to be added first.
                            </p>
                            <Link
                                href="/admin/timetable"
                                className="inline-flex items-center gap-2 px-5 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-lg hover:bg-[var(--primary-hover)] transition-colors"
                            >
                                Go to Timetable Manager
                                <ArrowRight className="w-4 h-4" />
                            </Link>
                        </div>
                    </div>
                )}

                {/* Step 5: Done */}
                {step === 5 && (
                    <div className="text-center py-8 space-y-5">
                        <div className="w-20 h-20 mx-auto rounded-full bg-success-badge flex items-center justify-center">
                            <CheckCircle2 className="w-10 h-10 text-green-600" />
                        </div>
                        <h2 className="text-2xl font-bold text-[var(--text-primary)]">Your School is Live! 🎉</h2>
                        <p className="text-sm text-[var(--text-secondary)] max-w-md mx-auto">
                            You can now share login credentials with teachers and students.
                            Visit the dashboard to manage your school.
                        </p>
                        <div className="flex justify-center gap-3 pt-4">
                            <Link
                                href="/admin/dashboard"
                                className="inline-flex items-center gap-2 px-6 py-3 bg-[var(--primary)] text-white text-sm font-medium rounded-lg hover:bg-[var(--primary-hover)] transition-colors"
                            >
                                Go to Dashboard
                                <ArrowRight className="w-4 h-4" />
                            </Link>
                            <Link
                                href="/admin/users"
                                className="inline-flex items-center gap-2 px-6 py-3 border border-[var(--border)] text-[var(--text-secondary)] text-sm font-medium rounded-lg hover:border-[var(--primary)] transition-colors"
                            >
                                Manage Users
                            </Link>
                        </div>
                    </div>
                )}
            </div>

            {/* ─── Navigation buttons ─── */}
            {step < 5 && (
                <div className="flex justify-between mt-6">
                    <button
                        onClick={prev}
                        disabled={step === 0}
                        className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-[var(--text-secondary)] rounded-lg border border-[var(--border)] hover:border-[var(--text-muted)] transition-colors disabled:opacity-40"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back
                    </button>
                    <button
                        onClick={next}
                        className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium bg-[var(--primary)] text-white rounded-lg hover:bg-[var(--primary-hover)] transition-colors"
                    >
                        {step === 4 ? "Finish Setup" : "Next Step"}
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
            )}
        </div>
    );
}
