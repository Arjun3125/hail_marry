import type { Metadata } from "next";
import { cookies } from "next/headers";
import { existsSync, readFileSync } from "fs";
import { join } from "path";
import "./globals.css";
import "katex/dist/katex.min.css";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import { LanguageProvider } from "@/i18n/LanguageProvider";
import { LANGUAGE_COOKIE_KEY, resolveLanguage } from "@/i18n/config";
import { BrandingProvider } from "@/components/theme/BrandingProvider";
import DemoToolbarWrapper from "@/components/DemoToolbarWrapper";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { PostHogProvider } from "@/providers/PostHogProvider";
import { PrismBackdrop } from "@/components/prism/PrismBackdrop";
import { configureBoneyard, registerBones } from "boneyard-js/react";
import { Analytics } from "@vercel/analytics/next";

// Initialize Boneyard global defaults
configureBoneyard({
  animate: "pulse",
  darkColor: "rgba(255, 255, 255, 0.03)",
  color: "rgba(0, 0, 0, 0.05)",
});

// Load skeleton registry if built
try {
  const registryPath = join(process.cwd(), "skeleton-registry.json");
  if (existsSync(registryPath)) {
    const registry = JSON.parse(readFileSync(registryPath, "utf-8"));
    registerBones(registry);
  }
} catch {
  // Registry not yet built, skeletons will auto-generate or use fallbacks
}

export const metadata: Metadata = {
  title: "ModernHustlers — AI-Powered Learning Infrastructure",
  description:
    "Document intelligence platform. Grounded answers, citation-enforced, multi-tenant, privacy-first.",
  keywords: ["AI", "education", "school", "ERP", "learning", "NotebookLM"],
  manifest: "/manifest.json",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const initialLang = resolveLanguage(cookieStore.get(LANGUAGE_COOKIE_KEY)?.value);

  return (
      <html
      lang={initialLang}
      style={{
        ["--font-body" as string]:
          '"Segoe UI", Tahoma, Verdana, "Noto Sans", sans-serif',
        ["--font-display" as string]:
          'Georgia, Cambria, "Times New Roman", serif',
      }}
      suppressHydrationWarning
    >
      <head>
        <meta name="theme-color" content="#0f172a" />
        <script
          src="https://accounts.google.com/gsi/client"
          async
          defer
        />
      </head>
      <body className="prism-app antialiased bg-[var(--bg-page)] text-[var(--text-primary)] transition-colors duration-300" suppressHydrationWarning>
        <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:px-4 focus:py-2 focus:bg-[var(--bg-page)] focus:text-[var(--text-primary)] focus:outline focus:outline-2 focus:rounded">
          Skip to main content
        </a>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          storageKey="vidyaos-theme"
          disableTransitionOnChange
        >
          <PostHogProvider>
            <LanguageProvider initialLang={initialLang}>
              <QueryProvider>
                <BrandingProvider>
                  <PrismBackdrop />
                  <main id="main-content" className="prism-main relative z-10">
                    {children}
                  </main>
                  <DemoToolbarWrapper />
                  <div aria-live="polite" aria-atomic="true" className="sr-only" id="screen-reader-announcer" />
                  <Analytics />
                </BrandingProvider>
              </QueryProvider>
            </LanguageProvider>
          </PostHogProvider>
        </ThemeProvider>
        <script
          dangerouslySetInnerHTML={{
            __html: `if('serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('/sw.js').catch(()=>{})})}`,
          }}
        />
      </body>
    </html>
  );
}
