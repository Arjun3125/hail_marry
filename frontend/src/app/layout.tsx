import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import { LanguageProvider } from "@/i18n/LanguageProvider";
import { BrandingProvider } from "@/components/theme/BrandingProvider";
import DemoToolbarWrapper from "@/components/DemoToolbarWrapper";



export const metadata: Metadata = {
  title: "ModernHustlers — AI-Powered Learning Infrastructure",
  description:
    "Document intelligence platform. Grounded answers, citation-enforced, multi-tenant, privacy-first.",
  keywords: ["AI", "education", "school", "ERP", "learning", "NotebookLM"],
  manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="font-sans" suppressHydrationWarning>
      <head>
        <meta name="theme-color" content="#0f172a" />
        <script
          src="https://accounts.google.com/gsi/client"
          async
          defer
        />
      </head>
      <body className="antialiased bg-[var(--bg-page)] text-[var(--text-primary)] transition-colors duration-300">
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
          <LanguageProvider>
            <BrandingProvider>
              <main id="main-content">
                {children}
              </main>
              <DemoToolbarWrapper />
              <div aria-live="polite" aria-atomic="true" className="sr-only" id="screen-reader-announcer" />
            </BrandingProvider>
          </LanguageProvider>
        </ThemeProvider>
        <script
          dangerouslySetInnerHTML={{
            __html: `if('serviceWorker' in navigator){window.addEventListener('load',()=>{navigator.serviceWorker.register('/sw.js').catch(()=>{})})}`
          }}
        />
      </body>
    </html>
  );
}
