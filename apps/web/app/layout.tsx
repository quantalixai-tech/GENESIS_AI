import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  display: "swap",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "GENESIS AI — AI-Driven Software Development Platform",
  description:
    "Create complete software projects from natural-language conversations. GENESIS AI understands your idea, designs the application, generates code, and keeps it working — automatically.",
  keywords: ["AI", "software development", "code generation", "no-code", "AI platform"],
  authors: [{ name: "GENESIS AI" }],
  openGraph: {
    title: "GENESIS AI",
    description: "AI-Driven Software Development Platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
