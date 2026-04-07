"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import en from "@/i18n/en.json";
import hi from "@/i18n/hi.json";
import { LANGUAGE_COOKIE_KEY, resolveLanguage, type Language } from "@/i18n/config";

type Translations = typeof en;

const dictionaries: Record<Language, Translations> = { en, hi };

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

function persistLanguage(newLang: Language) {
    document.cookie = `${LANGUAGE_COOKIE_KEY}=${newLang};path=/;max-age=31536000;SameSite=Lax`;
    localStorage.setItem(LANGUAGE_COOKIE_KEY, newLang);
    document.documentElement.lang = newLang;
}

function getClientPreferredLanguage(initialLang: Language): Language {
    if (typeof document === "undefined") {
        return initialLang;
    }

    const cookieMatch = document.cookie
        .split("; ")
        .find((cookie) => cookie.startsWith(`${LANGUAGE_COOKIE_KEY}=`));
    if (cookieMatch) {
        return resolveLanguage(cookieMatch.split("=")[1]);
    }

    return resolveLanguage(localStorage.getItem(LANGUAGE_COOKIE_KEY)) || initialLang;
}

export function LanguageProvider({
    children,
    initialLang,
}: {
    children: React.ReactNode;
    initialLang: Language;
}) {
    const [lang, setLangState] = useState<Language>(() => getClientPreferredLanguage(initialLang));

    useEffect(() => {
        const cookieMatch = document.cookie
            .split("; ")
            .find((cookie) => cookie.startsWith(`${LANGUAGE_COOKIE_KEY}=`));
        const cookieLang = resolveLanguage(cookieMatch?.split("=")[1]);
        const storedLang = resolveLanguage(localStorage.getItem(LANGUAGE_COOKIE_KEY));

        if (cookieLang !== lang || storedLang !== lang) {
            persistLanguage(lang);
            return;
        }

        document.documentElement.lang = lang;
    }, [lang]);

    const setLang = useCallback((newLang: Language) => {
        setLangState(newLang);
        persistLanguage(newLang);
    }, []);

    const t = useCallback(
        (path: string): string => {
            const keys = path.split(".");
            let value: unknown = dictionaries[lang];
            for (const key of keys) {
                if (value && typeof value === "object" && key in value) {
                    value = (value as Record<string, unknown>)[key];
                } else {
                    let fallback: unknown = dictionaries.en;
                    for (const fallbackKey of keys) {
                        if (fallback && typeof fallback === "object" && fallbackKey in fallback) {
                            fallback = (fallback as Record<string, unknown>)[fallbackKey];
                        } else {
                            return path;
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
            className="flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-2.5 py-1.5 text-xs font-medium text-[var(--text-secondary)] transition-colors hover:border-[var(--primary)] hover:text-[var(--primary)]"
            title={lang === "en" ? "हिंदी में बदलें" : "Switch to English"}
        >
            {lang === "en" ? "हिंदी" : "English"}
        </button>
    );
}
