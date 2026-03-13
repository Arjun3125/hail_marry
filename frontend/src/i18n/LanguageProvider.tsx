"use client";

import React, { createContext, useContext, useState, useCallback } from "react";
import en from "@/i18n/en.json";
import hi from "@/i18n/hi.json";

type Translations = typeof en;
type Language = "en" | "hi";

const dictionaries: Record<Language, Translations> = { en, hi };

const STORAGE_KEY = "vidyaos-lang";

type LanguageContextType = {
    lang: Language;
    setLang: (lang: Language) => void;
    t: (path: string) => string;
};

const LanguageContext = createContext<LanguageContextType>({
    lang: "en",
    setLang: () => { },
    t: (path: string) => path,
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
    const [lang, setLangState] = useState<Language>(() => {
        if (typeof window === "undefined") return "en";
        const stored = localStorage.getItem(STORAGE_KEY) as Language | null;
        return stored && dictionaries[stored] ? stored : "en";
    });

    const setLang = useCallback((newLang: Language) => {
        setLangState(newLang);
        localStorage.setItem(STORAGE_KEY, newLang);
    }, []);

    const t = useCallback(
        (path: string): string => {
            const keys = path.split(".");
            let value: unknown = dictionaries[lang];
            for (const key of keys) {
                if (value && typeof value === "object" && key in value) {
                    value = (value as Record<string, unknown>)[key];
                } else {
                    // Fallback to English
                    let fallback: unknown = dictionaries.en;
                    for (const k of keys) {
                        if (fallback && typeof fallback === "object" && k in fallback) {
                            fallback = (fallback as Record<string, unknown>)[k];
                        } else {
                            return path; // Return key as-is if not found
                        }
                    }
                    return typeof fallback === "string" ? fallback : path;
                }
            }
            return typeof value === "string" ? value : path;
        },
        [lang],
    );

    return (
        <LanguageContext.Provider value={{ lang, setLang, t }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    return useContext(LanguageContext);
}

export function LanguageToggle() {
    const { lang, setLang } = useLanguage();
    return (
        <button
            onClick={() => setLang(lang === "en" ? "hi" : "en")}
            className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium rounded-lg border border-[var(--border)] text-[var(--text-secondary)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors"
            title={lang === "en" ? "हिंदी में बदलें" : "Switch to English"}
        >
            {lang === "en" ? "🇮🇳 हिंदी" : "🇬🇧 English"}
        </button>
    );
}
