import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "NeuroCron - The Autonomous Marketing Brain",
  description:
    "AI that plans, executes, audits, and optimizes your entire marketing — automatically.",
  keywords: [
    "AI marketing",
    "marketing automation",
    "autonomous marketing",
    "digital marketing platform",
    "marketing AI",
  ],
  authors: [{ name: "NeuroCron" }],
  openGraph: {
    title: "NeuroCron - The Autonomous Marketing Brain",
    description:
      "AI that plans, executes, audits, and optimizes your entire marketing — automatically.",
    url: "https://neurocron.com",
    siteName: "NeuroCron",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "NeuroCron - The Autonomous Marketing Brain",
    description:
      "AI that plans, executes, audits, and optimizes your entire marketing — automatically.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="min-h-screen bg-midnight antialiased">{children}</body>
    </html>
  );
}

