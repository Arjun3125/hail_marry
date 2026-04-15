import { cache } from "react";
import { cookies } from "next/headers";
import type { BrandingConfig } from "@/components/theme/branding";

const RAW_API_BASE = (
    process.env.API_ORIGIN ??
    process.env.NEXT_PUBLIC_API_URL ??
    "http://127.0.0.1:8000"
).trim().replace(/\/+$/, "");

function getServerApiBase() {
    return RAW_API_BASE || "http://127.0.0.1:8000";
}

async function getRequestCookieHeader() {
    try {
        const cookieStore = await cookies();
        return cookieStore
            .getAll()
            .map(({ name, value }) => `${name}=${value}`)
            .join("; ");
    } catch {
        // cookies() throws DYNAMIC_SERVER_USAGE during Next.js build-time
        // static generation probes. Return empty string so the fetch can
        // proceed (and fail gracefully via its own try/catch).
        return "";
    }
}

export async function serverApiFetch<T>(
    path: string,
    init: RequestInit & {
        cookieHeader?: string;
    } = {},
): Promise<T | null> {
    const { cookieHeader, headers, ...rest } = init;
    const mergedHeaders = new Headers(headers || {});
    const resolvedCookieHeader = cookieHeader ?? await getRequestCookieHeader();

    if (resolvedCookieHeader) {
        mergedHeaders.set("cookie", resolvedCookieHeader);
    }
    if (!mergedHeaders.has("content-type")) {
        mergedHeaders.set("content-type", "application/json");
    }

    try {
        const response = await fetch(`${getServerApiBase()}${path}`, {
            ...rest,
            headers: mergedHeaders,
            cache: "no-store",
            signal: AbortSignal.timeout(1500),
        });

        if (!response.ok) {
            console.error(`[ERROR] serverApiFetch status ${response.status} for ${path}`);
            return null;
        }

        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error: unknown) {
        // no-store fetch throws DYNAMIC_SERVER_USAGE during Next.js build-time
        // static generation probes — this is expected, not a real failure.
        const isDynamic =
            error != null &&
            typeof error === "object" &&
            "digest" in error &&
            (error as { digest: string }).digest === "DYNAMIC_SERVER_USAGE";
        if (!isDynamic) {
            console.error(`[ERROR] serverApiFetch failed for ${path}:`, error);
        }
        return null;
    }
}

export const getServerBrandingConfig = cache(async () => {
    return await serverApiFetch<BrandingConfig>("/api/branding/config");
});
