"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Clock, Send } from "lucide-react";

import { api } from "@/lib/api";

type ComplaintItem = {
    id: string;
    category: string;
    description: string;
    status: "open" | "in_review" | "resolved";
    date: string;
};

const statusIcon = {
    open: <Clock className="w-4 h-4 text-[var(--warning)]" />,
    in_review: <AlertCircle className="w-4 h-4 text-[var(--primary)]" />,
    resolved: <CheckCircle2 className="w-4 h-4 text-[var(--success)]" />,
};

export default function ComplaintsPage() {
    const [complaints, setComplaints] = useState<ComplaintItem[]>([]);
    const [description, setDescription] = useState("");
    const [category, setCategory] = useState("academic");
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadComplaints = async () => {
        const payload = await api.student.complaints();
        setComplaints((payload || []) as ComplaintItem[]);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await loadComplaints();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load complaints");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const handleSubmit = async () => {
        if (!description.trim()) return;

        try {
            setSubmitting(true);
            setError(null);
            await api.student.createComplaint({
                category,
                description: description.trim(),
            });
            setDescription("");
            await loadComplaints();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to submit complaint");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Complaints</h1>
                <p className="text-sm text-[var(--text-secondary)]">Submit and track your complaints.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] mb-6">
                <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">New Complaint</h2>
                <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] mb-3 focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                >
                    <option value="academic">Academic</option>
                    <option value="infrastructure">Infrastructure</option>
                    <option value="behavior">Behavior</option>
                    <option value="other">Other</option>
                </select>
                <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe your complaint..."
                    rows={3}
                    className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] mb-3 focus:outline-none focus:ring-2 focus:ring-[var(--primary)] resize-none"
                />
                <button
                    onClick={() => void handleSubmit()}
                    disabled={submitting || !description.trim()}
                    className="px-5 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] transition-colors flex items-center gap-2 disabled:opacity-60"
                >
                    <Send className="w-4 h-4" /> {submitting ? "Submitting..." : "Submit"}
                </button>
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="px-5 py-3 border-b border-[var(--border)]">
                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Your Complaints</h2>
                </div>
                <div className="divide-y divide-[var(--border-light)]">
                    {loading ? (
                        <div className="px-5 py-4 text-sm text-[var(--text-muted)]">Loading complaints...</div>
                    ) : complaints.length === 0 ? (
                        <div className="px-5 py-4 text-sm text-[var(--text-muted)]">No complaints submitted yet.</div>
                    ) : (
                        complaints.map((complaint) => (
                            <div key={complaint.id} className="px-5 py-4 flex items-start justify-between gap-4">
                                <div>
                                    <p className="text-sm font-medium text-[var(--text-primary)]">{complaint.description}</p>
                                    <p className="text-xs text-[var(--text-muted)] mt-1">
                                        {complaint.category} | {complaint.date}
                                    </p>
                                </div>
                                <span className="flex items-center gap-1.5 text-xs font-medium capitalize whitespace-nowrap">
                                    {statusIcon[complaint.status]}
                                    {complaint.status.replace("_", " ")}
                                </span>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
