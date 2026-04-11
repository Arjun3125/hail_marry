"use client";

import { useEffect, useState } from "react";
import { Users, BookOpen, CheckSquare, BarChart3, QrCode, Megaphone, X, Download, Upload } from "lucide-react";
import QRCode from "react-qr-code";

import { PrismInput, PrismTableShell, PrismTextarea } from "@/components/prism/PrismControls";
import { PrismDialog, PrismDialogFooter, PrismDialogHeader, PrismOverlay } from "@/components/prism/PrismOverlays";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type TeacherClass = {
    id: string;
    name: string;
    grade: string;
    students: Array<{ id: string; name: string; email: string; roll_number: string | null }>;
    subjects: Array<{ id: string; name: string }>;
};

type StudentPreviewRow = {
    name: string;
    email: string;
    password: string;
};

type QrTokensPayload = {
    tokens?: Array<{ student_id: string; student_name: string; login_token: string }>;
};

function sanitizePrintMarkup(markup: string) {
    if (typeof window === "undefined" || !markup) {
        return "";
    }

    const doc = new DOMParser().parseFromString(markup, "text/html");
    doc.querySelectorAll("script, style, iframe, object, embed, link, meta").forEach((node) => node.remove());
    doc.body.querySelectorAll("*").forEach((element) => {
        Array.from(element.attributes).forEach((attribute) => {
            const name = attribute.name.toLowerCase();
            const value = attribute.value.trim().toLowerCase();
            if (name.startsWith("on")) {
                element.removeAttribute(attribute.name);
                return;
            }
            if ((name === "href" || name === "src") && value.startsWith("javascript:")) {
                element.removeAttribute(attribute.name);
            }
        });
    });
    return doc.body.innerHTML;
}

export default function TeacherClassesPage() {
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const [qrModalOpen, setQrModalOpen] = useState(false);
    const [selectedClassId, setSelectedClassId] = useState<string | null>(null);
    const [selectedClassName, setSelectedClassName] = useState<string | null>(null);
    const [qrTokens, setQrTokens] = useState<Array<{ student_id: string; student_name: string; login_token: string }>>([]);
    const [loadingQr, setLoadingQr] = useState(false);

    const [broadcastModalOpen, setBroadcastModalOpen] = useState(false);
    const [broadcastMessage, setBroadcastMessage] = useState("");
    const [sendingBroadcast, setSendingBroadcast] = useState(false);
    const [broadcastError, setBroadcastError] = useState<string | null>(null);
    const [broadcastSuccess, setBroadcastSuccess] = useState(false);
    const [rosterModalOpen, setRosterModalOpen] = useState(false);
    const [rosterBusy, setRosterBusy] = useState(false);
    const [rosterRows, setRosterRows] = useState<StudentPreviewRow[]>([]);
    const [rosterErrors, setRosterErrors] = useState<string[]>([]);
    const [rosterNotice, setRosterNotice] = useState<string | null>(null);
    const [rosterImportedCount, setRosterImportedCount] = useState<number | null>(null);

    const refreshClasses = async () => {
        const payload = await api.teacher.classes();
        setClasses((payload || []) as TeacherClass[]);
    };

    const escapeCsvValue = (value: string) => {
        if (value.includes(",") || value.includes("\"") || value.includes("\n")) {
            return `"${value.replace(/"/g, "\"\"")}"`;
        }
        return value;
    };

    const buildCsvFromRows = (rows: StudentPreviewRow[]) => {
        const header = ["name", "email", "password"];
        const lines = rows.map((row) => [row.name, row.email, row.password].map((value) => escapeCsvValue(value || "")).join(","));
        return `${header.join(",")}\n${lines.join("\n")}\n`;
    };

    const updateRosterRow = (index: number, field: keyof StudentPreviewRow, value: string) => {
        setRosterRows((prev) => prev.map((row, idx) => (idx === index ? { ...row, [field]: value } : row)));
    };

    const handleRosterPreview = async (file: File) => {
        try {
            setRosterBusy(true);
            setError(null);
            setSuccess(null);
            setRosterErrors([]);
            setRosterRows([]);
            setRosterImportedCount(null);
            const formData = new FormData();
            formData.append("file", file);
            const payload = await api.teacher.previewStudentOnboarding(formData) as {
                preview_rows?: StudentPreviewRow[];
                errors?: string[];
                ocr_review_required?: boolean;
                ocr_warning?: string | null;
                ocr_confidence?: number | null;
                ocr_unmatched_lines?: string[] | number;
            };
            const rows = Array.isArray(payload.preview_rows) ? payload.preview_rows : [];
            if (!rows.length) {
                throw new Error("No rows detected in the preview.");
            }
            const reviewRequired = Boolean(payload.ocr_review_required);
            const warning = typeof payload.ocr_warning === "string" ? payload.ocr_warning : null;
            const confidence = typeof payload.ocr_confidence === "number" ? payload.ocr_confidence : null;
            const unmatchedLines = Array.isArray(payload.ocr_unmatched_lines)
                ? payload.ocr_unmatched_lines.length
                : Number(payload.ocr_unmatched_lines || 0);
            const parts = ["Preview extracted student rows from OCR."];
            if (confidence !== null) parts.push(`OCR confidence ${(confidence * 100).toFixed(0)}%.`);
            if (reviewRequired) parts.push("Review recommended before final import.");
            if (unmatchedLines) parts.push(`${unmatchedLines} line${unmatchedLines === 1 ? "" : "s"} need manual cleanup.`);
            if (warning) parts.push(warning);
            setRosterRows(rows);
            setRosterErrors(Array.isArray(payload.errors) ? payload.errors : []);
            setRosterNotice(parts.join(" "));
            setRosterModalOpen(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Preview failed");
        } finally {
            setRosterBusy(false);
        }
    };

    const confirmRosterImport = async () => {
        if (!rosterRows.length) return;
        try {
            setRosterBusy(true);
            setError(null);
            const csv = buildCsvFromRows(rosterRows);
            const formData = new FormData();
            formData.append("file", new File([csv], "teacher-student-import.csv", { type: "text/csv" }));
            const payload = await api.teacher.onboardStudents(formData) as {
                created_count?: number;
                message?: string;
                ocr_review_required?: boolean;
                ocr_warning?: string | null;
                ocr_confidence?: number | null;
                ocr_unmatched_lines?: string[] | number;
            };
            const createdCount = Number(payload.created_count || 0);
            const reviewRequired = Boolean(payload.ocr_review_required);
            const warning = typeof payload.ocr_warning === "string" ? payload.ocr_warning : null;
            const confidence = typeof payload.ocr_confidence === "number" ? payload.ocr_confidence : null;
            const unmatchedLines = Array.isArray(payload.ocr_unmatched_lines)
                ? payload.ocr_unmatched_lines.length
                : Number(payload.ocr_unmatched_lines || 0);
            const parts = [`Imported ${createdCount} students successfully.`];
            if (confidence !== null) parts.push(`OCR confidence ${(confidence * 100).toFixed(0)}%.`);
            if (reviewRequired) parts.push("Review follow-up recommended.");
            if (unmatchedLines) parts.push(`${unmatchedLines} OCR line${unmatchedLines === 1 ? "" : "s"} still need manual cleanup.`);
            if (warning) parts.push(warning);
            setRosterImportedCount(createdCount);
            setRosterNotice(parts.join(" "));
            setSuccess(payload.message || `Imported ${createdCount} students successfully.`);
            await refreshClasses();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Import failed");
        } finally {
            setRosterBusy(false);
        }
    };

    const handleOpenQr = async (classId: string, className: string) => {
        setSelectedClassId(classId);
        setSelectedClassName(className);
        setQrModalOpen(true);
        try {
            setLoadingQr(true);
            const payload = await api.teacher.getQrTokens(classId) as QrTokensPayload;
            setQrTokens(payload.tokens || []);
        } catch (err) {
            console.error("Failed to fetch QR tokens", err);
        } finally {
            setLoadingQr(false);
        }
    };

    const handleOpenBroadcast = (classId: string, className: string) => {
        setSelectedClassId(classId);
        setSelectedClassName(className);
        setBroadcastMessage("");
        setBroadcastError(null);
        setBroadcastSuccess(false);
        setBroadcastModalOpen(true);
    };

    const handleCloseBroadcastModal = () => {
        setBroadcastModalOpen(false);
        setBroadcastError(null);
        setBroadcastSuccess(false);
    };

    const handleSendBroadcast = async () => {
        if (!selectedClassId || !broadcastMessage.trim()) return;
        try {
            setSendingBroadcast(true);
            setBroadcastError(null);
            await api.teacher.broadcast({ class_id: selectedClassId, message: broadcastMessage });
            setBroadcastError(null);
            setBroadcastSuccess(true);
            setTimeout(() => {
                handleCloseBroadcastModal();
            }, 2000);
        } catch (err) {
            console.error("Broadcast failed", err);
            setBroadcastError(err instanceof Error ? err.message : "Broadcast failed");
        } finally {
            setSendingBroadcast(false);
        }
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await refreshClasses();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load classes");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    useEffect(() => {
        if (typeof window === "undefined") return;
        window.localStorage.setItem(
            "mascotPageContext",
            JSON.stringify({
                route: "/teacher/classes",
                current_page_entity: "student_onboarding",
                current_page_entity_id: null,
                metadata: {
                    import_kind: "teacher_roster_import",
                },
            }),
        );
    }, []);

    return (
        <PrismPage variant="workspace" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Users className="h-3.5 w-3.5" />
                            Class Management
                        </PrismHeroKicker>
                    )}
                    title="Operate class rosters and parent-facing actions from one desk"
                    description="Review class groups, open QR access, send urgent broadcasts, and import student rosters without losing control of the active teacher workflow."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Best use</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Keep roster imports explicit, use QR access only for the intended class, and treat broadcast as a high-importance parent communication action.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Assigned classes</span>
                        <span className="prism-status-value">{classes.length}</span>
                        <span className="prism-status-detail">Class groups currently assigned to the teacher account.</span>
                    </div>
                </div>

                <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                        <h2 className="text-base font-semibold text-[var(--text-primary)]">Class directory</h2>
                        <p className="text-sm text-[var(--text-secondary)]">Manage active classes, roster onboarding, QR access, and parent alerts.</p>
                    </div>
                    <label className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-[var(--radius-sm)] border border-[var(--primary)]/20 bg-[var(--primary-light)] px-4 py-2 text-sm font-medium text-[var(--primary)] transition-colors hover:bg-[var(--primary)] hover:text-white">
                    <Upload className="h-4 w-4" />
                    Import Student Roster
                    <input
                        type="file"
                        accept=".csv,.txt,.jpg,.jpeg,.png"
                        className="hidden"
                        onChange={(e) => {
                            const file = e.target.files?.[0];
                            e.currentTarget.value = "";
                            if (file) {
                                void handleRosterPreview(file);
                            }
                        }}
                    />
                    </label>
                </div>

                {error ? <ErrorRemediation error={error} scope="teacher-classes" onRetry={() => void refreshClasses()} /> : null}
            {success ? (
                <div className="rounded-[var(--radius)] border border-[var(--success)]/30 bg-success-subtle px-4 py-3 text-sm text-[var(--success)] mb-4">
                    {success}
                </div>
            ) : null}

            <div className="grid md:grid-cols-2 gap-4">
                {loading ? (
                    <PrismPanel className="p-5 text-sm text-[var(--text-muted)]">
                        Loading classes...
                    </PrismPanel>
                ) : classes.length === 0 ? (
                    <PrismPanel className="p-5 text-sm text-[var(--text-muted)]">
                        No classes assigned.
                    </PrismPanel>
                ) : classes.map((cls) => (
                    <PrismPanel key={cls.id} className="p-5">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)]">{cls.name}</h3>
                            <span className="flex items-center gap-1 text-sm text-[var(--text-secondary)]">
                                <Users className="w-4 h-4" /> {cls.students.length}
                            </span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {cls.subjects.map((subject) => (
                                <span key={subject.id} className="text-xs bg-[var(--primary-light)] text-[var(--primary)] px-2.5 py-1 rounded-full font-medium">
                                    {subject.name}
                                </span>
                            ))}
                        </div>
                        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                            <div className="text-center p-2 bg-[var(--bg-page)] rounded-[var(--radius-sm)]">
                                <CheckSquare className="w-4 h-4 mx-auto text-[var(--success)] mb-1" />
                                <p className="text-[10px] text-[var(--text-muted)]">Attendance</p>
                            </div>
                            <div className="text-center p-2 bg-[var(--bg-page)] rounded-[var(--radius-sm)]">
                                <BookOpen className="w-4 h-4 mx-auto text-[var(--primary)] mb-1" />
                                <p className="text-[10px] text-[var(--text-muted)]">Marks</p>
                            </div>
                            <div className="text-center p-2 bg-[var(--bg-page)] rounded-[var(--radius-sm)]">
                                <BarChart3 className="w-4 h-4 mx-auto text-[var(--warning)] mb-1" />
                                <p className="text-[10px] text-[var(--text-muted)]">Insights</p>
                            </div>
                        </div>
                        <div className="mt-4 flex gap-2 border-t border-[var(--border)] pt-4">
                            <button
                                onClick={() => handleOpenQr(cls.id, cls.name)}
                                className="flex-1 py-1.5 text-xs bg-[var(--bg-page)] border border-[var(--border)] rounded flex items-center justify-center gap-1 hover:bg-[var(--bg-hover)]"
                            >
                                <QrCode className="w-3 h-3" /> Magic QR
                            </button>
                            <button
                                onClick={() => handleOpenBroadcast(cls.id, cls.name)}
                                className="group flex flex-1 items-center justify-center gap-1 rounded border border-[var(--error)]/20 bg-error-subtle py-1.5 text-xs text-[var(--error)] transition-colors hover:bg-[var(--error)] hover:text-white"
                            >
                                <Megaphone className="h-3 w-3 transition-colors group-hover:text-white" /> <span className="transition-colors group-hover:text-white">Broadcast</span>
                            </button>
                        </div>
                    </PrismPanel>
                ))}
            </div>

            {rosterModalOpen && (
                <PrismOverlay className="z-50">
                    <PrismDialog className="flex max-h-[90vh] w-full max-w-4xl flex-col">
                        <PrismDialogHeader>
                            <div>
                                <h2 className="text-lg font-bold text-[var(--text-primary)]">Review Extracted Students</h2>
                                <p className="text-sm text-[var(--text-secondary)]">
                                    OCR imports are editable before any student accounts are created.
                                </p>
                            </div>
                            <button
                                onClick={() => setRosterModalOpen(false)}
                                className="text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                            >
                                <X className="h-5 w-5" />
                            </button>
                        </PrismDialogHeader>
                        <div className="flex-1 overflow-auto p-4">
                            <p className="mb-4 text-sm text-[var(--text-secondary)]">{rosterRows.length} student row{rosterRows.length === 1 ? "" : "s"} staged for review.</p>
                            {rosterNotice ? (
                                <div className="mb-4 rounded-[var(--radius-sm)] border border-[var(--warning)]/30 bg-warning-subtle px-4 py-3 text-sm text-[var(--warning)]">
                                    {rosterNotice}
                                </div>
                            ) : null}
                            {rosterErrors.length > 0 ? (
                                <div className="mb-4 rounded-[var(--radius-sm)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                                    {rosterErrors.join(" ")}
                                </div>
                            ) : null}
                            <PrismTableShell>
                                <table className="prism-table w-full min-w-[720px]">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Email</th>
                                            <th>Password</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rosterRows.map((row, index) => (
                                            <tr key={`${row.email}-${index}`} className="border-b border-[var(--border-light)]">
                                                <td>
                                                    <PrismInput
                                                        value={row.name}
                                                        onChange={(e) => updateRosterRow(index, "name", e.target.value)}
                                                        className="text-sm"
                                                    />
                                                </td>
                                                <td>
                                                    <PrismInput
                                                        value={row.email}
                                                        onChange={(e) => updateRosterRow(index, "email", e.target.value)}
                                                        className="text-sm"
                                                    />
                                                </td>
                                                <td>
                                                    <PrismInput
                                                        value={row.password}
                                                        onChange={(e) => updateRosterRow(index, "password", e.target.value)}
                                                        className="text-sm"
                                                    />
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </PrismTableShell>
                            {rosterImportedCount !== null ? (
                                <p className="mt-4 text-sm font-medium text-[var(--success)]">
                                    Imported {rosterImportedCount} student{rosterImportedCount === 1 ? "" : "s"}.
                                </p>
                            ) : null}
                        </div>
                        <PrismDialogFooter>
                            <p className="text-xs text-[var(--text-muted)]">
                                Explicit confirmation is required before OCR-derived student rows are saved.
                            </p>
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={() => setRosterModalOpen(false)}
                                    className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--bg-page)] px-4 py-2 text-sm font-medium hover:bg-[var(--bg-hover)]"
                                >
                                    Close
                                </button>
                                <button
                                    onClick={() => void confirmRosterImport()}
                                    disabled={rosterBusy || rosterRows.length === 0}
                                    className="rounded-[var(--radius-sm)] bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:opacity-60"
                                >
                                    {rosterBusy ? "Importing..." : "Confirm Import"}
                                </button>
                            </div>
                        </PrismDialogFooter>
                    </PrismDialog>
                </PrismOverlay>
            )}

            {/* QR Modal */}
            {qrModalOpen && (
                <PrismOverlay className="z-50">
                    <PrismDialog className="w-full max-w-4xl max-h-[90vh] flex flex-col">
                        <PrismDialogHeader>
                            <h2 className="text-lg font-bold text-[var(--text-primary)]">Print Magic QR Badges - {selectedClassName}</h2>
                            <button onClick={() => setQrModalOpen(false)} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                                <X className="w-5 h-5" />
                            </button>
                        </PrismDialogHeader>
                        <div className="p-4 overflow-auto flex-1 bg-[var(--bg-page)]">
                            <p className="mb-4 text-sm text-[var(--text-secondary)]">{qrTokens.length} QR badge{qrTokens.length === 1 ? "" : "s"} loaded for this class.</p>
                            {loadingQr ? (
                                <p className="text-center text-[var(--text-muted)] py-10">Generating magic tokens...</p>
                            ) : qrTokens.length === 0 ? (
                                <p className="text-center text-[var(--text-muted)] py-10">No students enrolled in this class.</p>
                            ) : (
                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4" id="print-area">
                                    {qrTokens.map(token => (
                                        <div key={token.student_id} className="bg-white text-black p-4 rounded shadow-sm border border-gray-200 flex flex-col items-center text-center">
                                            <div className="font-bold text-sm mb-2">{token.student_name}</div>
                                            <div className="bg-white p-2 rounded">
                                                <QRCode value={token.login_token} size={120} level="M" />
                                            </div>
                                            <div className="text-[10px] text-gray-500 mt-2">Validity: 6 Months</div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        <PrismDialogFooter className="justify-end">
                            <button onClick={() => setQrModalOpen(false)} className="px-4 py-2 bg-[var(--bg-page)] border border-[var(--border)] rounded hover:bg-[var(--bg-hover)] text-sm font-medium">
                                Close
                            </button>
                            <button onClick={() => {
                                const printContent = document.getElementById("print-area");
                                if (!printContent) {
                                    setError("No QR badges are available to print right now.");
                                    return;
                                }
                                const windowPrint = window.open("", "", "width=900,height=650");
                                if (!windowPrint) {
                                    setError("Popup blocked. Allow popups to print QR badges.");
                                    return;
                                }
                                const safeMarkup = sanitizePrintMarkup(printContent.innerHTML);
                                windowPrint.document.write(`
                                    <html>
                                        <head>
                                            <title>Print QR Badges</title>
                                            <style>
                                                body { font-family: sans-serif; padding: 20px; }
                                                .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
                                                .card { border: 1px dashed #ccc; padding: 15px; text-align: center; page-break-inside: avoid; }
                                                .name { font-weight: bold; margin-bottom: 10px; font-size: 14px; }
                                                .token { margin-top: 10px; font-size: 10px; color: #666; }
                                            </style>
                                        </head>
                                        <body>
                                            <div class="grid">${safeMarkup}</div>
                                            <script>window.print(); window.close();</script>
                                        </body>
                                    </html>
                                `);
                                windowPrint.document.close();
                            }} className="px-4 py-2 bg-[var(--primary)] text-white rounded hover:bg-[var(--primary-hover)] flex items-center gap-2 text-sm font-medium">
                                <Download className="w-4 h-4" /> Print Badges
                            </button>
                        </PrismDialogFooter>
                    </PrismDialog>
                </PrismOverlay>
            )}

            {/* Broadcast Modal */}
            {broadcastModalOpen && (
                <PrismOverlay className="z-50">
                    <PrismDialog className="w-full max-w-md p-5">
                        <PrismDialogHeader className="mb-4 border-b-0 px-0 py-0">
                            <h2 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2"><Megaphone className="w-5 h-5 text-[var(--error)]" /> Emergency Broadcast</h2>
                            <button onClick={handleCloseBroadcastModal} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                                <X className="w-5 h-5" />
                            </button>
                        </PrismDialogHeader>
                        {broadcastSuccess ? (
                            <div className="text-center py-6 text-[var(--success)]">
                                <CheckSquare className="w-12 h-12 mx-auto mb-2 opacity-80" />
                                <p className="font-semibold">Broadcast queued successfully!</p>
                                <p className="text-xs opacity-70 mt-1">Parents will receive a WhatsApp message shortly.</p>
                            </div>
                        ) : (
                            <div>
                                <p className="text-sm text-[var(--text-secondary)] mb-4">
                                    Send an urgent WhatsApp alert to all linked parents of <strong>{selectedClassName}</strong>.
                                </p>
                                {broadcastError ? (
                                    <div className="mb-4 rounded-[var(--radius-sm)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                                        {broadcastError}
                                    </div>
                                ) : null}
                                <PrismTextarea
                                    className="mb-4 h-32 text-sm"
                                    placeholder="Type your emergency message or important update here..."
                                    value={broadcastMessage}
                                    onChange={(e) => setBroadcastMessage(e.target.value)}
                                />
                                <button
                                    onClick={handleSendBroadcast}
                                    disabled={sendingBroadcast || !broadcastMessage.trim()}
                                    className="w-full py-2 bg-[var(--error)] text-white font-medium rounded-[var(--radius-sm)] hover:bg-red-600 disabled:opacity-50 flex items-center justify-center gap-2 transition-colors"
                                >
                                    {sendingBroadcast ? "Broadcasting..." : "Send Alert Now"}
                                </button>
                            </div>
                        )}
                    </PrismDialog>
                </PrismOverlay>
            )}
            </PrismSection>
        </PrismPage>
    );
}
