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
    const cookieStore = await cookies();
    return cookieStore
        .getAll()
        .map(({ name, value }) => `${name}=${value}`)
        .join("; ");
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
    } catch (error) {
        console.error(`[ERROR] serverApiFetch failed for ${path}:`, error);
        return null;
    }
}

export const getServerBrandingConfig = cache(async () => {
    return await serverApiFetch<BrandingConfig>("/api/branding/config");
});
