import { redirect } from "next/navigation";

type LegacyAIPageProps = {
    searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

function getSingleValue(value: string | string[] | undefined) {
    return Array.isArray(value) ? value[0] : value;
}

export default async function LegacyStudentAIPage({ searchParams }: LegacyAIPageProps) {
    const resolvedSearchParams = (await searchParams) || {};
    const query = new URLSearchParams();

    Object.entries(resolvedSearchParams).forEach(([key, rawValue]) => {
        const value = getSingleValue(rawValue);
        if (!value) return;
        if (key === "mode") {
            if (!query.has("tool")) {
                query.set("tool", value);
            }
            return;
        }
        query.set(key, value);
    });

    const suffix = query.toString();
    redirect(`/student/ai-studio${suffix ? `?${suffix}` : ""}`);
}
