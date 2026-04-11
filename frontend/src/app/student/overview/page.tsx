import { serverApiFetch } from "@/lib/server-api";
import { StudentOverviewClient } from "./StudentOverviewClient";

export default async function StudentOverviewPage() {
    let initialData: Record<string, unknown> | null = null;

    try {
        initialData = await serverApiFetch<Record<string, unknown>>("/api/student/overview-bootstrap");
    } catch {
        initialData = null;
    }

    return <StudentOverviewClient initialData={initialData} />;
}
