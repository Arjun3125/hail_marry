"use client";

import { useEffect, useState } from "react";
import { Users, BookOpen, CheckSquare, BarChart3, QrCode, Megaphone, X, Download } from "lucide-react";
import QRCode from "react-qr-code";

import { api } from "@/lib/api";

type TeacherClass = {
    id: string;
    name: string;
    grade: string;
    students: Array<{ id: string; name: string; email: string; roll_number: string | null }>;
    subjects: Array<{ id: string; name: string }>;
};

export default function TeacherClassesPage() {
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [qrModalOpen, setQrModalOpen] = useState(false);
    const [selectedClassId, setSelectedClassId] = useState<string | null>(null);
    const [selectedClassName, setSelectedClassName] = useState<string | null>(null);
    const [qrTokens, setQrTokens] = useState<Array<{ student_id: string; student_name: string; login_token: string }>>([]);
    const [loadingQr, setLoadingQr] = useState(false);

    const [broadcastModalOpen, setBroadcastModalOpen] = useState(false);
    const [broadcastMessage, setBroadcastMessage] = useState("");
    const [sendingBroadcast, setSendingBroadcast] = useState(false);
    const [broadcastSuccess, setBroadcastSuccess] = useState(false);

    const handleOpenQr = async (classId: string, className: string) => {
        setSelectedClassId(classId);
        setSelectedClassName(className);
        setQrModalOpen(true);
        try {
            setLoadingQr(true);
            const payload = await api.teacher.getQrTokens(classId);
            setQrTokens((payload as any).tokens || []);
        } catch (err) {
            console.error("Failed to fetch QR tokens");
        } finally {
            setLoadingQr(false);
        }
    };

    const handleOpenBroadcast = (classId: string, className: string) => {
        setSelectedClassId(classId);
        setSelectedClassName(className);
        setBroadcastMessage("");
        setBroadcastSuccess(false);
        setBroadcastModalOpen(true);
    };

    const handleSendBroadcast = async () => {
        if (!selectedClassId || !broadcastMessage.trim()) return;
        try {
            setSendingBroadcast(true);
            await api.teacher.broadcast({ class_id: selectedClassId, message: broadcastMessage });
            setBroadcastSuccess(true);
            setTimeout(() => {
                setBroadcastModalOpen(false);
            }, 2000);
        } catch (err) {
            console.error("Broadcast failed", err);
        } finally {
            setSendingBroadcast(false);
        }
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.teacher.classes();
                setClasses((payload || []) as TeacherClass[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load classes");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">My Classes</h1>
                <p className="text-sm text-[var(--text-secondary)]">Manage your classes and view student details</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="grid md:grid-cols-2 gap-4">
                {loading ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        Loading classes...
                    </div>
                ) : classes.length === 0 ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        No classes assigned.
                    </div>
                ) : classes.map((cls) => (
                    <div key={cls.id} className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
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
                                className="flex-1 py-1.5 text-xs bg-[var(--primary-light)] text-[var(--primary)] border border-[var(--primary)]/20 rounded flex items-center justify-center gap-1 hover:bg-[var(--primary)] hover:text-white transition-colors"
                            >
                                <Megaphone className="w-3 h-3 text-[var(--error)] group-hover:text-white" /> <span className="text-[var(--error)] group-hover:text-white">Broadcast</span>
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* QR Modal */}
            {qrModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
                            <h2 className="text-lg font-bold text-[var(--text-primary)]">Print Magic QR Badges - {selectedClassName}</h2>
                            <button onClick={() => setQrModalOpen(false)} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 overflow-auto flex-1 bg-[var(--bg-page)]">
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
                        <div className="p-4 border-t border-[var(--border)] flex justify-end gap-3">
                            <button onClick={() => setQrModalOpen(false)} className="px-4 py-2 bg-[var(--bg-page)] border border-[var(--border)] rounded hover:bg-[var(--bg-hover)] text-sm font-medium">
                                Close
                            </button>
                            <button onClick={() => {
                                const printContent = document.getElementById('print-area');
                                const windowPrint = window.open('', '', 'width=900,height=650');
                                windowPrint?.document.write(`
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
                                            <div class="grid">${printContent?.innerHTML || ''}</div>
                                            <script>window.print(); window.close();</script>
                                        </body>
                                    </html>
                                `);
                            }} className="px-4 py-2 bg-[var(--primary)] text-white rounded hover:bg-[var(--primary-hover)] flex items-center gap-2 text-sm font-medium">
                                <Download className="w-4 h-4" /> Print Badges
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Broadcast Modal */}
            {broadcastModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-xl w-full max-w-md p-5">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2"><Megaphone className="w-5 h-5 text-[var(--error)]" /> Emergency Broadcast</h2>
                            <button onClick={() => setBroadcastModalOpen(false)} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
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
                                <textarea
                                    className="w-full h-32 p-3 bg-[var(--bg-page)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm mb-4 focus:outline-none focus:border-[var(--primary)]"
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
                    </div>
                </div>
            )}
        </div>
    );
}
