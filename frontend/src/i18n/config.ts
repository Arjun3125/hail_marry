export type Language = "en" | "hi";

export const LANGUAGE_COOKIE_KEY = "vidyaos-lang";

export function resolveLanguage(value: string | null | undefined): Language {
  return value === "hi" ? "hi" : "en";
}
