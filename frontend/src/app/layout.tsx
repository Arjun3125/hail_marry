import type { Metadata } from "next";
import { Inter_Tight, Geist } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import DemoToolbarWrapper from "@/components/DemoToolbarWrapper";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const interTight = Inter_Tight({
  subsets: ["latin"],
  variable: "--font-inter-tight",
});

export const metadata: Metadata = {
  title: "ModernHustlers — AI-Powered Learning Infrastructure",
  description:
    "Document intelligence platform. Grounded answers, citation-enforced, multi-tenant, privacy-first.",
  keywords: ["AI", "education", "school", "ERP", "learning", "NotebookLM"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <head>
        <script
          src="https://accounts.google.com/gsi/client"
          async
          defer
        />
      </head>
      <body className="antialiased bg-[var(--bg-page)] text-[var(--text-primary)] transition-colors duration-300">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <DemoToolbarWrapper />
        </ThemeProvider>
      </body>
    </html>
  );
}
