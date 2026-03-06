import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import DemoToolbarWrapper from "@/components/DemoToolbarWrapper";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "AIaaS — AI-Powered Learning for Schools",
  description:
    "Document intelligence platform for educational institutions. Grounded answers, citation-enforced, multi-tenant, privacy-first.",
  keywords: ["AI", "education", "school", "ERP", "learning", "NotebookLM"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <script
          src="https://accounts.google.com/gsi/client"
          async
          defer
        />
      </head>
      <body className="antialiased bg-slate-50 text-slate-900">
        {children}
        <DemoToolbarWrapper />
      </body>
    </html>
  );
}
