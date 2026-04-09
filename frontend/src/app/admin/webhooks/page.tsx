"use client";

import { useEffect, useMemo, useState } from "react";
import { Activity, Link2, Loader2, RadioTower, Trash2, Webhook } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismPage, PrismPageIntro, PrismPanel, PrismSection, PrismHeroKicker } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
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

function formatDateTime(value: string | null) {
    if (!value) return "-";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default function AdminWebhooksPage() {
    const [items, setItems] = useState<WebhookItem[]>([]);
    const [deliveries, setDeliveries] = useState<DeliveryItem[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [eventType, setEventType] = useState(EVENT_TYPES[0]);
    const [targetUrl, setTargetUrl] = useState("");
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
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

    const handleCreate = async (event: React.FormEvent) => {
        event.preventDefault();
        try {
            setSubmitting(true);
            setError(null);
            await api.admin.createWebhook({ event_type: eventType, target_url: targetUrl.trim() });
            setTargetUrl("");
            await loadWebhooks();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create webhook");
        } finally {
            setSubmitting(false);
        }
    };

    const handleToggle = async (item: WebhookItem) => {
        try {
            setError(null);
            await api.admin.toggleWebhook(item.id, !item.is_active);
            await loadWebhooks();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update webhook");
        }
    };

    const handleDelete = async (id: string) => {
        try {
            setError(null);
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

    const summary = useMemo(() => ({
        activeCount: items.filter((item) => item.is_active).length,
        selectedDeliveries: deliveries.length,
        lastDelivery: deliveries[0]?.status || "Idle",
    }), [deliveries, items]);

    return (
        <PrismPage variant="dashboard" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Webhook className="h-3.5 w-3.5" />
                            Admin Webhook Surface
                        </PrismHeroKicker>
                    )}
                    title="Keep outbound event delivery visible and reversible"
                    description="Manage outbound subscriptions, enable or disable live callbacks, and inspect recent delivery attempts from one operational admin surface."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Operational rule</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Add only trusted targets, disable before deleting, and inspect recent delivery attempts whenever a downstream integration starts missing events.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Subscriptions</span>
                        <span className="prism-status-value">{items.length}</span>
                        <span className="prism-status-detail">Total outbound webhook subscriptions currently registered.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Active endpoints</span>
                        <span className="prism-status-value">{summary.activeCount}</span>
                        <span className="prism-status-detail">Subscriptions currently allowed to receive live events.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Loaded deliveries</span>
                        <span className="prism-status-value">{summary.selectedDeliveries}</span>
                        <span className="prism-status-detail">Most recent delivery state: {summary.lastDelivery}.</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-webhooks"
                        onRetry={() => {
                            void loadWebhooks();
                        }}
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(340px,0.92fr)]">
                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5">
                            <div className="flex items-center gap-2">
                                <Link2 className="h-4 w-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Add subscription</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Register a trusted target URL and bind it to one event stream.
                            </p>

                            <form onSubmit={handleCreate} className="mt-4 grid gap-3 md:grid-cols-[220px_minmax(0,1fr)_auto]">
                                <select
                                    value={eventType}
                                    onChange={(event) => setEventType(event.target.value)}
                                    className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[rgba(96,165,250,0.4)] focus:bg-[rgba(96,165,250,0.06)]"
                                >
                                    {EVENT_TYPES.map((evt) => (
                                        <option key={evt} value={evt}>{evt}</option>
                                    ))}
                                </select>
                                <input
                                    value={targetUrl}
                                    onChange={(event) => setTargetUrl(event.target.value)}
                                    placeholder="https://your-app.example/webhook"
                                    className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[rgba(96,165,250,0.4)] focus:bg-[rgba(96,165,250,0.06)]"
                                    required
                                />
                                <button
                                    type="submit"
                                    className="prism-action inline-flex items-center gap-2"
                                    disabled={submitting}
                                >
                                    <Webhook className="h-4 w-4" />
                                    {submitting ? "Adding..." : "Add webhook"}
                                </button>
                            </form>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <div className="flex items-center justify-between gap-3">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Subscriptions</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        Toggle, inspect, or delete webhook subscriptions without leaving the integration surface.
                                    </p>
                                </div>
                                <div className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                    {items.length} registered
                                </div>
                            </div>

                            {loading ? (
                                <div className="mt-4 flex items-center gap-2 text-sm text-[var(--text-muted)]">
                                    <Loader2 className="h-4 w-4 animate-spin" /> Loading subscriptions...
                                </div>
                            ) : items.length === 0 ? (
                                <div className="mt-4">
                                    <EmptyState
                                        icon={Webhook}
                                        title="No webhooks configured"
                                        description="Create the first outbound subscription to start streaming tenant events to an external system."
                                        eyebrow="Subscriptions empty"
                                        scopeNote="Each subscription binds one event family to one target URL. Delivery history appears after the first event attempt."
                                    />
                                </div>
                            ) : (
                                <div className="mt-4 space-y-3">
                                    {items.map((item) => (
                                        <div key={item.id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                                                <div className="min-w-0">
                                                    <p className="text-sm font-semibold text-[var(--text-primary)]">{item.event_type}</p>
                                                    <p className="mt-1 break-all text-xs text-[var(--text-muted)]">{item.target_url}</p>
                                                    <p className="mt-2 text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
                                                        Added {formatDateTime(item.created_at)}
                                                    </p>
                                                </div>
                                                <div className="flex flex-wrap items-center gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => setSelectedId(item.id)}
                                                        className="prism-action-secondary inline-flex items-center gap-2"
                                                    >
                                                        <Activity className="h-4 w-4" />
                                                        Deliveries
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => void handleToggle(item)}
                                                        className={`inline-flex items-center gap-2 rounded-2xl px-4 py-2.5 text-sm font-semibold transition ${
                                                            item.is_active
                                                                ? "border border-amber-500/20 bg-amber-500/10 text-amber-400 hover:bg-amber-500/15"
                                                                : "border border-emerald-500/20 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/15"
                                                        }`}
                                                    >
                                                        <RadioTower className="h-4 w-4" />
                                                        {item.is_active ? "Disable" : "Enable"}
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={() => void handleDelete(item.id)}
                                                        className="inline-flex items-center gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-2.5 text-sm font-semibold text-red-400 transition hover:bg-red-500/15"
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                        Delete
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </PrismPanel>
                    </div>

                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5 xl:sticky xl:top-6">
                            <div className="flex items-center gap-2">
                                <Activity className="h-4 w-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Recent deliveries</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Inspect recent delivery outcomes for the currently selected subscription.
                            </p>

                            <div className="mt-4 space-y-3">
                                {!selectedId ? (
                                    <EmptyState
                                        icon={Activity}
                                        title="No subscription selected"
                                        description="Select a webhook subscription to inspect its recent delivery attempts."
                                        eyebrow="Delivery stream idle"
                                        scopeNote="Delivery attempts are grouped per subscription, so the right rail stays focused on one integration at a time."
                                    />
                                ) : deliveries.length === 0 ? (
                                    <EmptyState
                                        icon={RadioTower}
                                        title="No deliveries found"
                                        description="This subscription does not have any recent delivery attempts recorded."
                                        eyebrow="No delivery history"
                                        scopeNote="Webhook history appears after the platform attempts to deliver a matching outbound event."
                                    />
                                ) : (
                                    deliveries.map((delivery) => (
                                        <div key={delivery.id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                            <div className="flex items-center justify-between gap-3">
                                                <p className="text-sm font-semibold text-[var(--text-primary)]">{delivery.event_type}</p>
                                                <span className="text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">{delivery.status}</span>
                                            </div>
                                            <p className="mt-2 text-xs text-[var(--text-secondary)]">
                                                Code {delivery.status_code ?? "-"} · Attempts {delivery.attempt_count}
                                            </p>
                                            <p className="mt-1 text-xs text-[var(--text-muted)]">
                                                Last attempt {formatDateTime(delivery.last_attempt_at)} · Created {formatDateTime(delivery.created_at)}
                                            </p>
                                        </div>
                                    ))
                                )}
                            </div>
                        </PrismPanel>
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}
