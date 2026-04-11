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
): Promise<T> {
    const { cookieHeader, headers, ...rest } = init;
    const mergedHeaders = new Headers(headers || {});
    const resolvedCookieHeader = cookieHeader ?? await getRequestCookieHeader();

    if (resolvedCookieHeader) {
        mergedHeaders.set("cookie", resolvedCookieHeader);
    }
    if (!mergedHeaders.has("content-type")) {
        mergedHeaders.set("content-type", "application/json");
    }

    const response = await fetch(`${getServerApiBase()}${path}`, {
        ...rest,
        headers: mergedHeaders,
        cache: "no-store",
    });

    if (!response.ok) {
        const detail = await response.text().catch(() => "");
        throw new Error(detail || `Failed to load ${path} (${response.status})`);
    }

    if (response.status === 204) {
        return null as T;
    }

    return response.json() as Promise<T>;
}

export const getServerBrandingConfig = cache(async () => {
    return await serverApiFetch<BrandingConfig | null>("/api/branding/config");
});
