export type BrandingConfig = {
    primary_color?: string | null;
    secondary_color?: string | null;
    accent_color?: string | null;
    font_family?: string | null;
    theme_style?: string | null;
    logo_url?: string | null;
    name?: string | null;
};

export const defaultBrandingConfig: BrandingConfig = {};

export function buildBrandingStyle(config?: BrandingConfig | null): Record<string, string> {
    const style: Record<string, string> = {};

    if (!config) {
        return style;
    }

    if (config.primary_color) {
        style["--primary"] = config.primary_color;
        style["--accent-purple"] = config.primary_color;
    }

    if (config.secondary_color) {
        style["--success"] = config.secondary_color;
    }

    if (config.accent_color) {
        style["--warning"] = config.accent_color;
    }

    if (config.font_family) {
        style["--font-sans"] = `${config.font_family}, system-ui`;
    }

    return style;
}

export function applyBrandingCssVars(root: HTMLElement, config?: BrandingConfig | null) {
    const style = buildBrandingStyle(config);
    for (const [key, value] of Object.entries(style)) {
        root.style.setProperty(key, value);
    }
}
