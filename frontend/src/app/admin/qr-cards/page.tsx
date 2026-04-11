"use client";

import { useEffect, useMemo, useState } from "react";
import { Printer, QrCode, RefreshCcw } from "lucide-react";
import { QRCodeCanvas } from "qrcode.react";

import EmptyState from "@/components/EmptyState";
import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
    PrismSectionHeader,
} from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
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
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <QrCode className="h-3.5 w-3.5" />
                            Student Access Cards
                        </PrismHeroKicker>
                    )}
                    title="Issue QR login cards that keep classroom access simple"
                    description="Generate student QR cards for guided sign-in, reissue them when needed, and print a clean set for distribution without exposing the rest of the admin workflow."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Classes loaded</span>
                        <strong className="prism-status-value">{classes.length}</strong>
                        <span className="prism-status-detail">Available class groups for QR distribution</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Students in scope</span>
                        <strong className="prism-status-value">{filteredStudents.length}</strong>
                        <span className="prism-status-detail">Students included in the current card generation view</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Cards generated</span>
                        <strong className="prism-status-value">{tokens.length}</strong>
                        <span className="prism-status-detail">Printable access cards prepared for this session</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation error={error} scope="admin-qr-cards" onRetry={() => window.location.reload()} />
                ) : null}

                <PrismPanel className="space-y-5 p-5">
                    <PrismSectionHeader
                        title="Generation settings"
                        description="Filter by class, choose how long the cards should stay active, and regenerate only when older cards need to be invalidated."
                        actions={(
                            <div className="flex flex-wrap gap-2">
                                <button
                                    onClick={() => window.print()}
                                    className="prism-action-secondary"
                                    disabled={tokens.length === 0}
                                    type="button"
                                >
                                    <Printer className="h-4 w-4" />
                                    Print
                                </button>
                                <button
                                    onClick={() => void generateTokens()}
                                    disabled={generating || loading || filteredStudents.length === 0}
                                    className="prism-action"
                                    type="button"
                                >
                                    <QrCode className="h-4 w-4" />
                                    Generate QR codes
                                </button>
                            </div>
                        )}
                    />

                    <div className="grid gap-3 sm:grid-cols-[1fr_180px_180px_auto]">
                        <select
                            className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-3 text-sm text-[var(--text-primary)]"
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
                            onChange={(e) => {
                                const parsed = Number.parseInt(e.target.value, 10);
                                setExpiresInDays(Number.isNaN(parsed) ? 1 : Math.max(1, parsed));
                            }}
                            className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-3 text-sm text-[var(--text-primary)]"
                            placeholder="Expiry (days)"
                        />
                        <label className="flex items-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-3 text-sm text-[var(--text-secondary)]">
                            <input
                                type="checkbox"
                                checked={regenerate}
                                onChange={(e) => setRegenerate(e.target.checked)}
                            />
                            Regenerate cards
                        </label>
                        <button
                            onClick={() => void generateTokens()}
                            disabled={generating || loading || filteredStudents.length === 0}
                            className="prism-action-secondary"
                            type="button"
                        >
                            <RefreshCcw className="h-4 w-4" />
                            Refresh
                        </button>
                    </div>
                    <p className="text-xs leading-5 text-[var(--text-secondary)]">
                        QR cards link to one-time login routes. Regenerate when an older batch should stop working.
                    </p>
                </PrismPanel>

                {loading ? (
                    <PrismPanel className="p-8">
                        <p className="text-sm text-[var(--text-secondary)]">Loading class and student roster...</p>
                    </PrismPanel>
                ) : tokens.length === 0 ? (
                    <PrismPanel className="p-6">
                        <EmptyState
                            icon={QrCode}
                            title="No QR cards generated yet"
                            description="Generate cards to preview a printable batch for students in the selected class scope."
                            eyebrow="Ready for access setup"
                            scopeNote="This page only prepares sign-in cards. It does not change student records until the cards are actually used."
                        />
                    </PrismPanel>
                ) : (
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        {tokens.map((token) => {
                            const qrValue = origin ? `${origin}${token.login_url}` : token.login_url;
                            return (
                                <PrismPanel key={token.student_id} className="p-4">
                                    <div className="mb-4 flex items-start justify-between gap-3">
                                        <div>
                                            <p className="text-sm font-semibold text-[var(--text-primary)]">{token.student_name}</p>
                                            <p className="text-[10px] text-[var(--text-muted)]">{token.email}</p>
                                        </div>
                                        {token.class_name ? (
                                            <span className="rounded-full bg-info-badge px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-status-blue">
                                                {token.class_name}
                                            </span>
                                        ) : null}
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <QRCodeCanvas value={qrValue} size={100} includeMargin />
                                        <div className="space-y-1 text-xs text-[var(--text-secondary)]">
                                            <p className="font-semibold text-[var(--text-primary)]">Login code</p>
                                            <p className="break-all text-[10px]">{token.qr_token}</p>
                                            {token.expires_at ? (
                                                <p className="text-[10px] text-[var(--text-muted)]">
                                                    Expires {new Date(token.expires_at).toLocaleDateString()}
                                                </p>
                                            ) : null}
                                        </div>
                                    </div>
                                </PrismPanel>
                            );
                        })}
                    </div>
                )}
            </PrismSection>
        </PrismPage>
    );
}
