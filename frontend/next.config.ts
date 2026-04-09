import type { NextConfig } from "next";

const RAW_API_ORIGIN = process.env.API_ORIGIN ?? process.env.NEXT_PUBLIC_API_URL;

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
    typescript: {
        // Type safety is enforced explicitly by `npm run typecheck` in the build
        // pipeline so production builds do not depend on Next.js spawning a
        // separate type-check worker in constrained environments.
        ignoreBuildErrors: true,
    },
    async rewrites() {
        const apiBaseUrl = normalizeApiBaseUrl(RAW_API_ORIGIN);
        if (!apiBaseUrl) {
            console.warn("Skipping /api rewrite because API_ORIGIN/NEXT_PUBLIC_API_URL is invalid.");
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
