import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "@/styles/globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-sans",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

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
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-midnight antialiased font-sans">{children}</body>
    </html>
  );
}

