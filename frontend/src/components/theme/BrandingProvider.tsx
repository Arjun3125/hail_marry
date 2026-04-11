"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { applyBrandingCssVars, type BrandingConfig } from "./branding";

export function BrandingProvider({
    children,
    initialConfig = null,
}: {
    children: React.ReactNode;
    initialConfig?: BrandingConfig | null;
}) {
    const [config, setConfig] = useState<BrandingConfig | null>(initialConfig);

    useEffect(() => {
        setConfig(initialConfig);
    }, [initialConfig]);

    useEffect(() => {
        if (initialConfig) {
            return;
        }

        api.admin.brandingConfig()
            .then(data => setConfig(data))
            .catch(() => console.debug("No custom branding config found or not logged in."));
    }, [initialConfig]);

    useEffect(() => {
        if (!config) return;

        applyBrandingCssVars(document.documentElement, config);
    }, [config]);

    return <>{children}</>;
}
