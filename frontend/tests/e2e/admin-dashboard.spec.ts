import { expect, test } from "@playwright/test";

test("admin dashboard shows alerts and dispatches them", async ({ page }) => {
    await page.addInitScript(() => {
        window.localStorage.setItem("vidyaos_access_token", "test-token");
        Object.defineProperty(navigator, "clipboard", {
            value: {
                writeText: async (value: string) => {
                    (window as Window & { __copiedMascotEvidence?: string }).__copiedMascotEvidence = value;
                },
            },
            configurable: true,
        });
    });

    let dispatchCalls = 0;

    await page.route("**/api/whatsapp/release-gate-snapshot?days=7", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                generated_at: "2026-03-30T03:30:00Z",
                period_days: 7,
                analytics: {
                    total_messages: 84,
                    inbound: 42,
                    outbound: 42,
                    unique_users: 12,
                    avg_latency_ms: 920,
                },
                release_gate_metrics: {
                    duplicate_inbound_total: 1,
                    routing_failure_total: 2,
                    visible_failure_total: 1,
                    outbound_retryable_failure_total: 1,
                    upload_ingest_failure_total: 0,
                    link_ingest_failure_total: 0,
                },
                derived_rates: {
                    duplicate_inbound_pct: 2.38,
                    routing_failure_pct: 4.76,
                    visible_failure_pct: 2.38,
                    outbound_retryable_failure_pct: 2.38,
                },
            }),
        });
    });

    await page.route("**/api/mascot/release-gate-snapshot?days=7", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                generated_at: "2026-03-30T03:30:00Z",
                period_days: 7,
                analytics: {
                    total_actions: 126,
                    unique_users: 18,
                },
                release_gate_metrics: {
                    interpretation_success_total: 120,
                    interpretation_failure_total: 2,
                    execution_success_total: 110,
                    execution_failure_total: 3,
                    confirmation_success_total: 8,
                    confirmation_failure_total: 1,
                    confirmation_cancelled_total: 2,
                    upload_success_total: 14,
                    upload_failure_total: 1,
                },
                derived_rates: {
                    interpretation_failure_pct: 1.64,
                    execution_failure_pct: 2.65,
                    upload_failure_pct: 6.67,
                    confirmation_failure_pct: 9.09,
                    overall_failure_pct: 2.84,
                },
                active_alerts: [
                    {
                        code: "mascot_failure_rate_high",
                        severity: "critical",
                        message: "Mascot upload failure rate reached 16.7% over 12 events.",
                    },
                ],
            }),
        });
    });

    await page.route("**/api/mascot/release-gate-evidence?days=7", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                generated_at: "2026-03-30T03:30:00Z",
                filename: "mascot_release_gate_evidence_2026-03-30T03-30-00Z.md",
                markdown: "# Mascot Release Gate Evidence\n\n- total mascot actions: 126\n- execution failure %: 2.65\n",
                snapshot: {
                    generated_at: "2026-03-30T03:30:00Z",
                    period_days: 7,
                    analytics: {
                        total_actions: 126,
                        unique_users: 18,
                    },
                    release_gate_metrics: {
                        interpretation_success_total: 120,
                        interpretation_failure_total: 2,
                        execution_success_total: 110,
                        execution_failure_total: 3,
                        confirmation_success_total: 8,
                        confirmation_failure_total: 1,
                        confirmation_cancelled_total: 2,
                        upload_success_total: 14,
                        upload_failure_total: 1,
                    },
                    derived_rates: {
                        interpretation_failure_pct: 1.64,
                        execution_failure_pct: 2.65,
                        upload_failure_pct: 6.67,
                        confirmation_failure_pct: 9.09,
                        overall_failure_pct: 2.84,
                    },
                    active_alerts: [],
                },
            }),
        });
    });

    await page.route("**/api/mascot/staging-packet?days=7", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                generated_at: "2026-03-30T03:30:00Z",
                filename: "mascot_whatsapp_staging_packet_2026-03-30T03-30-00Z.md",
                markdown: "# Mascot WhatsApp Staging Packet\n\n- total messages: 84\n- total mascot actions: 126\n",
                whatsapp_snapshot: {
                    generated_at: "2026-03-30T03:30:00Z",
                    period_days: 7,
                    analytics: {
                        total_messages: 84,
                        inbound: 42,
                        outbound: 42,
                        unique_users: 12,
                        avg_latency_ms: 920,
                    },
                    release_gate_metrics: {
                        duplicate_inbound_total: 1,
                        routing_failure_total: 2,
                        visible_failure_total: 1,
                        outbound_retryable_failure_total: 1,
                        upload_ingest_failure_total: 0,
                        link_ingest_failure_total: 0,
                    },
                    derived_rates: {
                        duplicate_inbound_pct: 2.38,
                        routing_failure_pct: 4.76,
                        visible_failure_pct: 2.38,
                        outbound_retryable_failure_pct: 2.38,
                    },
                },
                mascot_snapshot: {
                    generated_at: "2026-03-30T03:30:00Z",
                    period_days: 7,
                    analytics: {
                        total_actions: 126,
                        unique_users: 18,
                    },
                    release_gate_metrics: {
                        interpretation_success_total: 120,
                        interpretation_failure_total: 2,
                        execution_success_total: 110,
                        execution_failure_total: 3,
                        confirmation_success_total: 8,
                        confirmation_failure_total: 1,
                        confirmation_cancelled_total: 2,
                        upload_success_total: 14,
                        upload_failure_total: 1,
                    },
                    derived_rates: {
                        interpretation_failure_pct: 1.64,
                        execution_failure_pct: 2.65,
                        upload_failure_pct: 6.67,
                        confirmation_failure_pct: 9.09,
                        overall_failure_pct: 2.84,
                    },
                    active_alerts: [],
                },
            }),
        });
    });

    await page.route("**/api/admin/**", async (route) => {
        const request = route.request();
        const url = new URL(request.url());
        const pathname = url.pathname;

        if (pathname.endsWith("/api/admin/dashboard")) {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    total_students: 120,
                    total_teachers: 14,
                    active_today: 52,
                    ai_queries_today: 31,
                    avg_attendance: 93,
                    avg_performance: 81,
                    open_complaints: 2,
                    queue_pending_depth: 5,
                    queue_processing_depth: 2,
                    queue_failure_rate_pct: 12,
                    queue_stuck_jobs: 1,
                    student_risk_summary: {
                        high_risk_students: 2,
                        medium_risk_students: 3,
                        academic_high_risk: 1,
                        fee_high_risk: 1,
                        dropout_high_risk: 1,
                    },
                    student_risk_alerts: [
                        {
                            student_id: "student-1",
                            student_name: "Aarav Kumar",
                            class_name: "Class 10",
                            dropout_risk: "high",
                            academic_risk: "high",
                            fee_risk: "medium",
                            attendance_pct: 58,
                            overall_score_pct: 39,
                        },
                    ],
                    observability_alerts: [
                        {
                            code: "queue_depth_high",
                            severity: "warning",
                            message: "Queue depth is 5 / 200 for this tenant.",
                        },
                    ],
                }),
            });
            return;
        }

        if (pathname.endsWith("/api/admin/security")) {
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify([]),
            });
            return;
        }

        if (pathname.endsWith("/api/admin/observability/alerts/dispatch")) {
            dispatchCalls += 1;
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                    alerts: [
                        {
                            code: "queue_depth_high",
                            severity: "warning",
                            message: "Queue depth is 5 / 200 for this tenant.",
                        },
                    ],
                    delivered: 1,
                    skipped: 0,
                }),
            });
            return;
        }

        await route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "Unhandled admin route" }) });
    });

    await page.route("**/api/branding/config", async (route) => {
        await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                name: "VidyaOS",
                logo_url: null,
                primary_color: "#2563eb",
                secondary_color: "#0f172a",
                accent_color: "#f59e0b",
                font_family: "Inter",
                theme_style: "modern",
            }),
        });
    });

    await page.goto("/admin/dashboard");

    await expect(page.getByRole("heading", { name: /Run school health from a calm academic control surface/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /WhatsApp release gate/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Mascot release gate/i })).toBeVisible();
    await expect(page.getByRole("heading", { name: /Student risk radar/i })).toBeVisible();
    await expect(page.getByText("Routing failure")).toBeVisible();
    await expect(page.getByText("Overall failure")).toBeVisible();
    await expect(page.getByText("Aarav Kumar")).toBeVisible();
    await expect(page.getByText("Academic high risk")).toBeVisible();
    await expect(page.getByText("126")).toBeVisible();
    await expect(page.getByText("84", { exact: true })).toBeVisible();
    await expect(page.getByText("Queue depth is 5 / 200 for this tenant.")).toBeVisible();
    await expect(page.getByRole("link", { name: "Open reports" })).toBeVisible();
    await page.getByRole("button", { name: "Copy evidence" }).click();
    await expect(page.getByText(/Mascot evidence copied from/i)).toBeVisible();
    await expect.poll(async () => page.evaluate(() => (window as Window & { __copiedMascotEvidence?: string }).__copiedMascotEvidence || "")).toContain("Mascot Release Gate Evidence");
    await page.getByRole("button", { name: "Copy staging packet" }).click();
    await expect(page.getByText(/Combined staging packet copied from/i)).toBeVisible();
    await expect.poll(async () => page.evaluate(() => (window as Window & { __copiedMascotEvidence?: string }).__copiedMascotEvidence || "")).toContain("Mascot WhatsApp Staging Packet");

    await page.getByRole("button", { name: "Dispatch Alerts" }).click();
    await expect.poll(() => dispatchCalls).toBe(1);
});
