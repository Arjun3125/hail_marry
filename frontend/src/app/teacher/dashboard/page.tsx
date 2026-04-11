import { serverApiFetch } from "@/lib/server-api";
import { TeacherDashboardClient } from "./TeacherDashboardClient";

export default async function TeacherDashboardPage() {
    let initialData: Record<string, unknown> | null = null;

    try {
        initialData = await serverApiFetch<Record<string, unknown>>("/api/teacher/dashboard");
    } catch {
        initialData = null;
    }

    return <TeacherDashboardClient initialData={initialData} />;
}
