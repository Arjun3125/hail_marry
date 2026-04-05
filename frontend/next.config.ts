import type { NextConfig } from "next";

function normalizeApiBaseUrl(value: string | undefined): string | null {
    const raw = value?.trim();
    if (!raw) {
        return "http://127.0.0.1:8000";
    }

    const withProtocol = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;

    try {
        return new URL(withProtocol).toString().replace(/\/$/, "");
    } catch {
        return null;
    }
}

const nextConfig: NextConfig = {
    async rewrites() {
        const apiBaseUrl = normalizeApiBaseUrl(process.env.NEXT_PUBLIC_API_URL);
        if (!apiBaseUrl) {
            console.warn("Skipping /api rewrite because NEXT_PUBLIC_API_URL is invalid.");
            return [];
        }

        return [
            {
                source: "/api/:path*",
                destination: `${apiBaseUrl}/api/:path*`,
            },
        ];
    },
};

export default nextConfig;
