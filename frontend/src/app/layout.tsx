import type { Metadata } from "next";
import { Inter_Tight } from "next/font/google";
import "./globals.css";
import DemoToolbarWrapper from "@/components/DemoToolbarWrapper";

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
    <html lang="en" className={interTight.variable}>
      <head>
        <script
          src="https://accounts.google.com/gsi/client"
          async
          defer
        />
      </head>
      <body className="antialiased bg-[#0a0a0a] text-[#fafafa]">
        {children}
        <DemoToolbarWrapper />
      </body>
    </html>
  );
}
