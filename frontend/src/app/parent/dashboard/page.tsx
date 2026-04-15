import { serverApiFetch } from "@/lib/server-api";
import { ParentDashboardClient } from "./ParentDashboardClient";

export const dynamic = "force-dynamic";

export default async function ParentDashboardPage() {
    let initialData: Record<string, unknown> | null = null;

    try {
        initialData = await serverApiFetch<Record<string, unknown>>("/api/parent/dashboard");
    } catch (err) {
        console.error("Failed to fetch /api/parent/dashboard for parent dashboard page", err);
        initialData = null;
    }

    return <ParentDashboardClient initialData={initialData} />;
}
