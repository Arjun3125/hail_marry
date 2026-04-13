import { serverApiFetch } from "@/lib/server-api";
import { logger } from "@/lib/logger";
import { AdminDashboardClient } from "./AdminDashboardClient";

export default async function AdminDashboardPage() {
    let initialData: Record<string, unknown> | null = null;

    try {
        initialData = await serverApiFetch<Record<string, unknown>>("/api/admin/dashboard-bootstrap");
    } catch (err) {
        logger.error("Failed to fetch /api/admin/dashboard-bootstrap for admin dashboard page", err as Error);
        initialData = null;
    }

    return <AdminDashboardClient initialData={initialData} />;
}
