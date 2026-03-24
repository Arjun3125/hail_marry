"use client";

import { useEffect, useState } from "react";
import { Download, Trash2, FileText, Settings, History, CheckCircle, Clock } from "lucide-react";
import { api } from "@/lib/api";

type ExportRequest = {
    id: string;
    scope_type: string;
    requested_by_name: string;
    status: "pending" | "processing" | "completed" | "failed";
    created_at: string;
    file_path?: string;
};

type DeletionRequest = {
    id: string;
    target_user_name: string;
    reason: string;
    status: "requested" | "processing" | "resolved" | "rejected";
    created_at: string;
};

export default function CompliancePage() {
    const [exports, setExports] = useState<ExportRequest[]>([]);
    const [deletions, setDeletions] = useState<DeletionRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<"exports" | "deletions" | "settings">("exports");

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                const [expData, delData] = await Promise.all([
                    api.enterprise.complianceExports(),
                    api.enterprise.deletionRequests(),
                ]);
                setExports(expData || []);
                setDeletions(delData || []);
            } catch (err) {
                console.error("Failed to load compliance data", err);
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const handleCreateExport = async () => {
        try {
            await api.enterprise.createComplianceExport({ scope_type: "tenant" });
            alert("Export job queued successfully.");
            // Refresh logic
        } catch (err) {
            alert("Failed to queue export.");
        }
    };

    if (loading) return <div className="p-8 text-center text-[var(--text-muted)]">Loading Compliance Dashboard...</div>;

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Compliance & Data Privacy</h1>
                <p className="text-sm text-[var(--text-secondary)]">Manage data exports, deletion requests, and retention policies (GDPR/DPDP)</p>
            </div>

            <div className="flex border-b border-[var(--border)] mb-6">
                <button
                    onClick={() => setActiveTab("exports")}
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                        activeTab === "exports" ? "border-[var(--primary)] text-[var(--primary)]" : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                    }`}
                >
                    <div className="flex items-center gap-2">
                        <Download className="w-4 h-4" /> Data Exports
                    </div>
                </button>
                <button
                    onClick={() => setActiveTab("deletions")}
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                        activeTab === "deletions" ? "border-[var(--primary)] text-[var(--primary)]" : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                    }`}
                >
                    <div className="flex items-center gap-2">
                        <Trash2 className="w-4 h-4" /> Deletion Requests
                    </div>
                </button>
                <button
                    onClick={() => setActiveTab("settings")}
                    className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                        activeTab === "settings" ? "border-[var(--primary)] text-[var(--primary)]" : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                    }`}
                >
                    <div className="flex items-center gap-2">
                        <Settings className="w-4 h-4" /> Policy Settings
                    </div>
                </button>
            </div>

            {activeTab === "exports" && (
                <div className="space-y-4">
                    <div className="flex justify-between items-center bg-[var(--bg-card)] p-4 rounded-[var(--radius)] shadow-[var(--shadow-card)]">
                        <div>
                            <h3 className="text-sm font-semibold text-[var(--text-primary)]">Request Full Data Export</h3>
                            <p className="text-xs text-[var(--text-muted)]">Download all tenant data including student records, grades, and files in a ZIP bundle.</p>
                        </div>
                        <button
                            onClick={handleCreateExport}
                            className="bg-[var(--primary)] text-white px-4 py-2 rounded-[var(--radius)] text-sm font-medium hover:opacity-90"
                        >
                            Request Bundle
                        </button>
                    </div>

                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                        <table className="w-full text-left text-sm">
                            <thead>
                                <tr className="bg-[var(--bg-page)] border-b border-[var(--border)]">
                                    <th className="px-6 py-3 font-medium text-[var(--text-muted)]">Type</th>
                                    <th className="px-6 py-3 font-medium text-[var(--text-muted)]">Status</th>
                                    <th className="px-6 py-3 font-medium text-[var(--text-muted)]">Requested</th>
                                    <th className="px-6 py-3 text-right font-medium text-[var(--text-muted)]">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[var(--border-light)]">
                                {exports.length === 0 ? (
                                    <tr><td colSpan={4} className="px-6 py-8 text-center text-[var(--text-muted)]">No export history.</td></tr>
                                ) : exports.map(exp => (
                                    <tr key={exp.id}>
                                        <td className="px-6 py-4">{exp.scope_type} bundle</td>
                                        <td className="px-6 py-4">
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                                                exp.status === "completed" ? "bg-[var(--success-subtle)] text-[var(--success)]" : "bg-[var(--bg-page)] text-[var(--text-muted)]"
                                            }`}>
                                                {exp.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-xs">{new Date(exp.created_at).toLocaleDateString()}</td>
                                        <td className="px-6 py-4 text-right">
                                            {exp.status === "completed" && (
                                                <button className="text-[var(--primary)] hover:underline font-medium flex items-center gap-1 justify-end ml-auto">
                                                    <Download className="w-3 h-3" /> Download
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {activeTab === "deletions" && (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                    <table className="w-full text-left text-sm">
                        <thead>
                            <tr className="bg-[var(--bg-page)] border-b border-[var(--border)]">
                                <th className="px-6 py-3 font-medium text-[var(--text-muted)]">Target User</th>
                                <th className="px-6 py-3 font-medium text-[var(--text-muted)]">Reason</th>
                                <th className="px-6 py-3 font-medium text-[var(--text-muted)]">Status</th>
                                <th className="px-6 py-3 font-medium text-[var(--text-muted)]">Requested</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[var(--border-light)]">
                            {deletions.length === 0 ? (
                                <tr><td colSpan={4} className="px-6 py-8 text-center text-[var(--text-muted)]">No active deletion requests.</td></tr>
                            ) : deletions.map(del => (
                                <tr key={del.id}>
                                    <td className="px-6 py-4 font-medium">{del.target_user_name}</td>
                                    <td className="px-6 py-4 text-xs text-[var(--text-muted)] italic">"{del.reason}"</td>
                                    <td className="px-6 py-4">
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                                            del.status === "resolved" ? "bg-[var(--success-subtle)] text-[var(--success)]" : "bg-[var(--warning-subtle)] text-[var(--warning)]"
                                        }`}>
                                            {del.status.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-xs">{new Date(del.created_at).toLocaleDateString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {activeTab === "settings" && (
                <div className="bg-[var(--bg-card)] p-6 rounded-[var(--radius)] shadow-[var(--shadow-card)] max-w-2xl">
                    <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Retention & Purge Policies</h3>
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Data Retention Period (Days)</label>
                            <input type="number" className="w-full bg-[var(--bg-page)] border border-[var(--border)] rounded-[var(--radius)] px-4 py-2 text-sm" placeholder="730 (2 Years)" />
                            <p className="text-[10px] text-[var(--text-muted)]">Records matching this age will be automatically archived or purged.</p>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Export Link Expiry (Days)</label>
                            <input type="number" className="w-full bg-[var(--bg-page)] border border-[var(--border)] rounded-[var(--radius)] px-4 py-2 text-sm" placeholder="7" />
                            <p className="text-[10px] text-[var(--text-muted)]">Compliance export ZIPs will be deleted from storage after this period.</p>
                        </div>
                        <div className="pt-4">
                            <button className="bg-[var(--primary)] text-white px-6 py-2 rounded-[var(--radius)] text-sm font-medium hover:opacity-90 transition-opacity">
                                Save Retention Policy
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
