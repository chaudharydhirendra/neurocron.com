import { MetadataRoute } from "next";

const baseUrl = "https://neurocron.com";

// Blog posts - in production, fetch from CMS/database
const blogPosts = [
  { slug: "future-of-ai-marketing-2025", lastModified: "2024-11-28" },
  { slug: "10x-productivity-with-autocron", lastModified: "2024-11-25" },
  { slug: "ai-content-generation-best-practices", lastModified: "2024-11-22" },
  { slug: "case-study-techscale-3x-roi", lastModified: "2024-11-18" },
  { slug: "neuroplan-v2-announcement", lastModified: "2024-11-15" },
  { slug: "marketing-automation-mistakes", lastModified: "2024-11-12" },
  { slug: "predictive-analytics-guide", lastModified: "2024-11-08" },
];

// Documentation pages
const docPages = [
  "quick-start",
  "account-setup",
  "integrations",
  "first-campaign",
  "neuroplan",
  "autocron",
  "contentforge",
  "insightcortex",
  "flowbuilder",
  "api/auth",
  "api/campaigns",
  "api/content",
  "api/webhooks",
  "security",
  "security/gdpr",
  "security/soc2",
];

type ChangeFrequency = "weekly" | "monthly" | "always" | "hourly" | "daily" | "yearly" | "never";

export default function sitemap(): MetadataRoute.Sitemap {
  // Static marketing pages
  const staticPages = [
    { path: "", frequency: "weekly" as ChangeFrequency, priority: 1 },
    { path: "/features", frequency: "monthly" as ChangeFrequency, priority: 0.9 },
    { path: "/pricing", frequency: "monthly" as ChangeFrequency, priority: 0.9 },
    { path: "/about", frequency: "monthly" as ChangeFrequency, priority: 0.8 },
    { path: "/blog", frequency: "weekly" as ChangeFrequency, priority: 0.8 },
    { path: "/docs", frequency: "monthly" as ChangeFrequency, priority: 0.8 },
    { path: "/demo", frequency: "monthly" as ChangeFrequency, priority: 0.8 },
    { path: "/contact", frequency: "monthly" as ChangeFrequency, priority: 0.7 },
    { path: "/login", frequency: "monthly" as ChangeFrequency, priority: 0.5 },
    { path: "/register", frequency: "monthly" as ChangeFrequency, priority: 0.6 },
    { path: "/privacy", frequency: "yearly" as ChangeFrequency, priority: 0.3 },
    { path: "/terms", frequency: "yearly" as ChangeFrequency, priority: 0.3 },
  ];

  const staticPageEntries: MetadataRoute.Sitemap = staticPages.map((page) => ({
    url: `${baseUrl}${page.path}`,
    lastModified: new Date(),
    changeFrequency: page.frequency,
    priority: page.priority,
  }));

  // Blog posts
  const blogEntries: MetadataRoute.Sitemap = blogPosts.map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.lastModified),
    changeFrequency: "weekly" as ChangeFrequency,
    priority: 0.7,
  }));

  // Documentation pages
  const docEntries: MetadataRoute.Sitemap = docPages.map((page) => ({
    url: `${baseUrl}/docs/${page}`,
    lastModified: new Date(),
    changeFrequency: "monthly" as ChangeFrequency,
    priority: 0.6,
  }));

  // Feature anchors for better SEO
  const featureAnchors = [
    "/features#strategy",
    "/features#execution",
    "/features#analytics",
    "/features#intelligence",
  ];

  const featureEntries: MetadataRoute.Sitemap = featureAnchors.map((anchor) => ({
    url: `${baseUrl}${anchor}`,
    lastModified: new Date(),
    changeFrequency: "monthly" as ChangeFrequency,
    priority: 0.8,
  }));

  return [
    ...staticPageEntries,
    ...featureEntries,
    ...blogEntries,
    ...docEntries,
  ];
}

