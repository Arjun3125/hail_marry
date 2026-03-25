"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type BrandingConfig = {
    primary_color?: string;
    secondary_color?: string;
    accent_color?: string;
    font_family?: string;
    theme_style?: string;
    logo_url?: string;
};

export function BrandingProvider({ children }: { children: React.ReactNode }) {
    const [config, setConfig] = useState<BrandingConfig | null>(null);

    useEffect(() => {
        // Fetch tenant branding on load
        api.admin.brandingConfig()
            .then(data => setConfig(data))
            .catch(() => console.debug("No custom branding config found or not logged in."));
    }, []);

    useEffect(() => {
        if (!config) return;

        const root = document.documentElement;
        
        // Convert tailwind colors using standard CSS variables across the app.
        // VidyaOS CSS already uses --primary for main accents.
        if (config.primary_color) {
            root.style.setProperty('--primary', config.primary_color);
            root.style.setProperty('--accent-purple', config.primary_color); // Override accents as well if desired
        }
        
        if (config.secondary_color) {
            root.style.setProperty('--success', config.secondary_color); // Reusing standard tokens or map freely
        }
        
        if (config.font_family) {
            root.style.setProperty('--font-sans', `${config.font_family}, system-ui`);
        }

    }, [config]);

    return <>{children}</>;
}
