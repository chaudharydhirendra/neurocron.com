import type { Metadata, Viewport } from "next";
import { Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "@/styles/globals.css";
import { AuthProvider } from "@/lib/auth-context";

const spaceGrotesk = Space_Grotesk({ 
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

const siteUrl = "https://neurocron.com";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "NeuroCron - The Autonomous Marketing Brain | AI-Powered Marketing Platform",
    template: "%s | NeuroCron",
  },
  description:
    "NeuroCron is the world's first truly autonomous AI marketing platform. Plan, execute, audit, and optimize your entire marketing automatically. Replace your marketing department with intelligent automation.",
  keywords: [
    "AI marketing platform",
    "autonomous marketing",
    "marketing automation",
    "AI-powered marketing",
    "digital marketing AI",
    "marketing intelligence",
    "campaign automation",
    "content generation AI",
    "marketing analytics",
    "NeuroCron",
    "AutoCron",
    "NeuroPlan",
    "marketing strategy AI",
  ],
  authors: [{ name: "NeuroCron", url: siteUrl }],
  creator: "NeuroCron",
  publisher: "NeuroCron",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  alternates: {
    canonical: siteUrl,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteUrl,
    siteName: "NeuroCron",
    title: "NeuroCron - The Autonomous Marketing Brain",
    description:
      "AI that plans, executes, audits, and optimizes your entire marketing — automatically. One platform. Zero vendor portals. Infinite possibilities.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "NeuroCron - The Autonomous Marketing Brain",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "NeuroCron - The Autonomous Marketing Brain",
    description:
      "AI that plans, executes, audits, and optimizes your entire marketing — automatically.",
    images: ["/og-image.png"],
    creator: "@neurocron",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  manifest: "/site.webmanifest",
  category: "technology",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#0A0A0F" },
    { media: "(prefers-color-scheme: dark)", color: "#0A0A0F" },
  ],
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

// JSON-LD Structured Data
const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${siteUrl}/#organization`,
      name: "NeuroCron",
      url: siteUrl,
      logo: {
        "@type": "ImageObject",
        url: `${siteUrl}/logo.png`,
        width: 512,
        height: 512,
      },
      sameAs: [
        "https://twitter.com/neurocron",
        "https://linkedin.com/company/neurocron",
        "https://github.com/neurocron",
      ],
      contactPoint: {
        "@type": "ContactPoint",
        contactType: "customer service",
        email: "support@neurocron.com",
      },
    },
    {
      "@type": "WebSite",
      "@id": `${siteUrl}/#website`,
      url: siteUrl,
      name: "NeuroCron",
      description: "The Autonomous Marketing Brain - AI-Powered Marketing Platform",
      publisher: {
        "@id": `${siteUrl}/#organization`,
      },
      potentialAction: {
        "@type": "SearchAction",
        target: {
          "@type": "EntryPoint",
          urlTemplate: `${siteUrl}/search?q={search_term_string}`,
        },
        "query-input": "required name=search_term_string",
      },
    },
    {
      "@type": "SoftwareApplication",
      "@id": `${siteUrl}/#software`,
      name: "NeuroCron",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      offers: {
        "@type": "Offer",
        price: "0",
        priceCurrency: "USD",
        description: "Free tier available",
      },
      aggregateRating: {
        "@type": "AggregateRating",
        ratingValue: "4.9",
        ratingCount: "127",
        bestRating: "5",
        worstRating: "1",
      },
      featureList: [
        "AI-powered marketing strategy generation",
        "Autonomous campaign execution",
        "Cross-channel analytics",
        "Content generation",
        "Competitor intelligence",
        "Customer persona creation",
      ],
    },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${jetbrainsMono.variable}`}>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="min-h-screen bg-midnight antialiased font-sans">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
