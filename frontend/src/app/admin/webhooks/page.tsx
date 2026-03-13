"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";

type WebhookItem = {
    id: string;
    event_type: string;
    target_url: string;
    is_active: boolean;
    created_at: string;
};

type DeliveryItem = {
    id: string;
    event_type: string;
    status: string;
    status_code: number | null;
    attempt_count: number;
    last_attempt_at: string | null;
    created_at: string;
};

const EVENT_TYPES = [
    "student.enrolled",
    "document.ingested",
    "ai.query.completed",
    "exam.results.published",
    "complaint.status.changed",
];

export default function AdminWebhooksPage() {
    const [items, setItems] = useState<WebhookItem[]>([]);
    const [deliveries, setDeliveries] = useState<DeliveryItem[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [eventType, setEventType] = useState(EVENT_TYPES[0]);
    const [targetUrl, setTargetUrl] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadWebhooks = async () => {
        const data = await api.admin.webhooks();
        setItems((data || []) as WebhookItem[]);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await loadWebhooks();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load webhooks");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    useEffect(() => {
        const loadDeliveries = async () => {
            if (!selectedId) {
                setDeliveries([]);
                return;
            }
            try {
                const data = await api.admin.webhookDeliveries(selectedId);
                setDeliveries((data || []) as DeliveryItem[]);
            } catch {
                setDeliveries([]);
            }
        };
        void loadDeliveries();
    }, [selectedId]);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setError(null);
            await api.admin.createWebhook({ event_type: eventType, target_url: targetUrl.trim() });
            setTargetUrl("");
            await loadWebhooks();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create webhook");
        }
    };

    const handleToggle = async (item: WebhookItem) => {
        try {
            await api.admin.toggleWebhook(item.id, !item.is_active);
            await loadWebhooks();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update webhook");
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await api.admin.deleteWebhook(id);
            if (selectedId === id) {
                setSelectedId(null);
                setDeliveries([]);
            }
            await loadWebhooks();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to delete webhook");
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Webhooks</h1>
                <p className="text-sm text-[var(--text-secondary)]">Manage outbound event subscriptions and delivery status.</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <form onSubmit={handleCreate} className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] grid md:grid-cols-3 gap-3">
                <select
                    value={eventType}
                    onChange={(e) => setEventType(e.target.value)}
                    className="px-3 py-2.5 border border-[var(--border)] rounded-[var(--radius-sm)] text-sm"
                >
                    {EVENT_TYPES.map((evt) => (
                        <option key={evt} value={evt}>{evt}</option>
                    ))}
                </select>
                <input
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                    placeholder="https://your-app.example/webhook"
                    className="px-3 py-2.5 border border-[var(--border)] rounded-[var(--radius-sm)] text-sm"
                    required
                />
                <button
                    type="submit"
                    className="px-4 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)]"
                >
                    Add Webhook
                </button>
            </form>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Subscriptions</h2>
                {loading ? (
                    <p className="text-sm text-[var(--text-muted)]">Loading subscriptions...</p>
                ) : items.length === 0 ? (
                    <p className="text-sm text-[var(--text-muted)]">No webhooks configured.</p>
                ) : (
                    <div className="space-y-3">
                        {items.map((item) => (
                            <div key={item.id} className="p-3 rounded-[var(--radius-sm)] border border-[var(--border)]">
                                <div className="flex items-center justify-between gap-3">
                                    <div>
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">{item.event_type}</p>
                                        <p className="text-xs text-[var(--text-muted)] break-all">{item.target_url}</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => setSelectedId(item.id)}
                                            className="px-3 py-1.5 text-xs rounded bg-[var(--bg-page)] text-[var(--text-secondary)]"
                                        >
                                            Deliveries
                                        </button>
                                        <button
                                            onClick={() => handleToggle(item)}
                                            className="px-3 py-1.5 text-xs rounded bg-[var(--primary-light)] text-[var(--primary)]"
                                        >
                                            {item.is_active ? "Disable" : "Enable"}
                                        </button>
                                        <button
                                            onClick={() => handleDelete(item.id)}
                                            className="px-3 py-1.5 text-xs rounded bg-error-subtle text-[var(--error)]"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Recent Deliveries</h2>
                {!selectedId ? (
                    <p className="text-sm text-[var(--text-muted)]">Select a subscription to inspect deliveries.</p>
                ) : deliveries.length === 0 ? (
                    <p className="text-sm text-[var(--text-muted)]">No deliveries found.</p>
                ) : (
                    <div className="space-y-2">
                        {deliveries.map((d) => (
                            <div key={d.id} className="p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)]">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium text-[var(--text-primary)]">{d.event_type}</p>
                                    <span className="text-xs text-[var(--text-muted)]">{d.status.toUpperCase()}</span>
                                </div>
                                <p className="text-xs text-[var(--text-muted)]">
                                    code: {d.status_code ?? "-"} | attempts: {d.attempt_count} | at: {d.last_attempt_at ? new Date(d.last_attempt_at).toLocaleString() : "-"}
                                </p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
