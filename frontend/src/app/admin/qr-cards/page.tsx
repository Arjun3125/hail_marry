"use client";

import { useEffect, useMemo, useState } from "react";
import { QrCode, RefreshCcw, Printer, AlertTriangle } from "lucide-react";
import { QRCodeCanvas } from "qrcode.react";

import { api } from "@/lib/api";

type ClassItem = {
    id: string;
    name: string;
    grade: string;
};

type StudentItem = {
    id: string;
    name: string;
    email: string;
    class_id: string | null;
    class_name: string | null;
    is_active: boolean;
};

type QrToken = {
    student_id: string;
    student_name: string;
    email: string;
    class_name: string | null;
    qr_token: string;
    expires_at: string | null;
    login_url: string;
};

export default function AdminQrCardsPage() {
    const [classes, setClasses] = useState<ClassItem[]>([]);
    const [students, setStudents] = useState<StudentItem[]>([]);
    const [selectedClassId, setSelectedClassId] = useState("all");
    const [expiresInDays, setExpiresInDays] = useState(30);
    const [regenerate, setRegenerate] = useState(false);
    const [tokens, setTokens] = useState<QrToken[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const origin = typeof window !== "undefined" ? window.location.origin : "";

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const [classPayload, studentPayload] = await Promise.all([
                    api.admin.classes(),
                    api.admin.students(),
                ]);
                setClasses((classPayload || []) as ClassItem[]);
                setStudents((studentPayload || []) as StudentItem[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load students");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const filteredStudents = useMemo(() => {
        if (selectedClassId === "all") {
            return students;
        }
        return students.filter((student) => student.class_id === selectedClassId);
    }, [students, selectedClassId]);

    const generateTokens = async () => {
        try {
            setGenerating(true);
            setError(null);
            const response = await api.admin.generateQrTokens({
                student_ids: filteredStudents.map((student) => student.id),
                expires_in_days: expiresInDays,
                regenerate,
            }) as { tokens?: QrToken[] };
            setTokens(response.tokens || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to generate QR codes");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">QR Login Cards</h1>
                    <p className="text-sm text-[var(--text-secondary)]">
                        Generate QR codes for students and print login cards.
                    </p>
                </div>
                <div className="flex flex-wrap gap-2">
                    <button
                        onClick={() => window.print()}
                        className="px-4 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] bg-[var(--bg-card)] hover:bg-[var(--bg-hover)] flex items-center gap-2"
                        disabled={tokens.length === 0}
                    >
                        <Printer className="w-4 h-4" /> Print
                    </button>
                    <button
                        onClick={() => void generateTokens()}
                        disabled={generating || loading || filteredStudents.length === 0}
                        className="px-4 py-2 text-sm bg-[var(--primary)] text-white rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] flex items-center gap-2 disabled:opacity-60"
                    >
                        <QrCode className="w-4 h-4" /> Generate QR Codes
                    </button>
                </div>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 mt-0.5" />
                    {error}
                </div>
            ) : null}

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4 space-y-4">
                <div className="grid gap-3 sm:grid-cols-[1fr_160px_160px_auto]">
                    <select
                        className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                        value={selectedClassId}
                        onChange={(e) => setSelectedClassId(e.target.value)}
                        disabled={loading}
                    >
                        <option value="all">All classes</option>
                        {classes.map((cls) => (
                            <option key={cls.id} value={cls.id}>
                                {cls.name} (Grade {cls.grade})
                            </option>
                        ))}
                    </select>
                    <input
                        type="number"
                        min={1}
                        value={expiresInDays}
                        onChange={(e) => setExpiresInDays(Number(e.target.value))}
                        className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                        placeholder="Expiry (days)"
                    />
                    <label className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                        <input
                            type="checkbox"
                            checked={regenerate}
                            onChange={(e) => setRegenerate(e.target.checked)}
                        />
                        Regenerate tokens
                    </label>
                    <button
                        onClick={() => void generateTokens()}
                        disabled={generating || loading || filteredStudents.length === 0}
                        className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] flex items-center gap-2 hover:bg-[var(--bg-hover)] disabled:opacity-60"
                    >
                        <RefreshCcw className="w-4 h-4" />
                        Refresh
                    </button>
                </div>
                <p className="text-xs text-[var(--text-muted)]">
                    QR codes link to one-time login URLs. Regenerate to invalidate old cards.
                </p>
            </div>

            {loading ? (
                <div className="text-sm text-[var(--text-muted)]">Loading students...</div>
            ) : tokens.length === 0 ? (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6 text-sm text-[var(--text-muted)]">
                    Generate QR codes to preview printable cards.
                </div>
            ) : (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {tokens.map((token) => {
                        const qrValue = origin ? `${origin}${token.login_url}` : token.login_url;
                        return (
                            <div key={token.student_id} className="rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                                <div className="flex items-center justify-between mb-3">
                                    <div>
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">{token.student_name}</p>
                                        <p className="text-[10px] text-[var(--text-muted)]">{token.email}</p>
                                    </div>
                                    {token.class_name ? (
                                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-info-badge text-status-blue">
                                            {token.class_name}
                                        </span>
                                    ) : null}
                                </div>
                                <div className="flex items-center gap-4">
                                    <QRCodeCanvas value={qrValue} size={100} includeMargin />
                                    <div className="text-xs text-[var(--text-secondary)] space-y-1">
                                        <p className="font-semibold text-[var(--text-primary)]">Login code</p>
                                        <p className="break-all text-[10px]">{token.qr_token}</p>
                                        {token.expires_at ? (
                                            <p className="text-[10px] text-[var(--text-muted)]">
                                                Expires: {new Date(token.expires_at).toLocaleDateString()}
                                            </p>
                                        ) : null}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
