import { Metadata } from "next";
import Link from "next/link";
import { Calendar, Clock, ArrowRight, Search, Tag } from "lucide-react";

export const metadata: Metadata = {
  title: "Blog",
  description: "Latest insights on AI marketing, automation strategies, and growth tactics from the NeuroCron team.",
  openGraph: {
    title: "Blog | NeuroCron",
    description: "AI marketing insights, tips, and best practices.",
  },
};

const categories = [
  { name: "All", slug: "all" },
  { name: "AI Marketing", slug: "ai-marketing" },
  { name: "Automation", slug: "automation" },
  { name: "Strategy", slug: "strategy" },
  { name: "Case Studies", slug: "case-studies" },
  { name: "Product Updates", slug: "product-updates" },
];

const featuredPost = {
  slug: "future-of-ai-marketing-2025",
  title: "The Future of AI Marketing: What to Expect in 2025",
  excerpt: "Autonomous systems, hyper-personalization, and predictive analytics are reshaping how we think about marketing. Here's what's coming next.",
  category: "AI Marketing",
  author: {
    name: "Sarah Martinez",
    role: "CTO",
    avatar: null,
  },
  publishedAt: "Nov 28, 2024",
  readTime: "8 min read",
  image: "/blog/featured.jpg",
};

const posts = [
  {
    slug: "10x-productivity-with-autocron",
    title: "How AutoCron Delivers 10x Marketing Productivity",
    excerpt: "Learn how our autonomous execution engine handles campaigns 24/7, optimizing in real-time without human intervention.",
    category: "Automation",
    author: { name: "Alex Chen", role: "CEO" },
    publishedAt: "Nov 25, 2024",
    readTime: "5 min read",
  },
  {
    slug: "ai-content-generation-best-practices",
    title: "AI Content Generation: Best Practices for 2025",
    excerpt: "Creating high-quality, on-brand content at scale requires the right approach. Here's how to get the most from ContentForge.",
    category: "AI Marketing",
    author: { name: "Emma Thompson", role: "VP Engineering" },
    publishedAt: "Nov 22, 2024",
    readTime: "6 min read",
  },
  {
    slug: "case-study-techscale-3x-roi",
    title: "Case Study: How TechScale Achieved 3x ROI with NeuroCron",
    excerpt: "TechScale replaced 8 marketing tools with NeuroCron and saw a 3x improvement in campaign performance within 60 days.",
    category: "Case Studies",
    author: { name: "David Kim", role: "VP Product" },
    publishedAt: "Nov 18, 2024",
    readTime: "7 min read",
  },
  {
    slug: "neuroplan-v2-announcement",
    title: "Introducing NeuroPlan v2: Smarter Strategies, Faster Results",
    excerpt: "Our latest update brings enhanced competitor analysis, improved budget recommendations, and multi-market support.",
    category: "Product Updates",
    author: { name: "Sarah Martinez", role: "CTO" },
    publishedAt: "Nov 15, 2024",
    readTime: "4 min read",
  },
  {
    slug: "marketing-automation-mistakes",
    title: "5 Marketing Automation Mistakes to Avoid in 2025",
    excerpt: "Common pitfalls that prevent teams from getting the most out of their automation tools, and how to fix them.",
    category: "Strategy",
    author: { name: "Alex Chen", role: "CEO" },
    publishedAt: "Nov 12, 2024",
    readTime: "5 min read",
  },
  {
    slug: "predictive-analytics-guide",
    title: "The Complete Guide to Predictive Analytics in Marketing",
    excerpt: "How AI models can forecast campaign performance, customer behavior, and market trends before you spend a dollar.",
    category: "AI Marketing",
    author: { name: "David Kim", role: "VP Product" },
    publishedAt: "Nov 8, 2024",
    readTime: "10 min read",
  },
];

export default function BlogPage() {
  return (
    <div className="pt-32">
      {/* Hero */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            NeuroCron <span className="gradient-text">Blog</span>
          </h1>
          <p className="text-xl text-white/60 mb-8">
            AI marketing insights, automation strategies, and growth tactics
          </p>

          {/* Search */}
          <div className="relative max-w-md mx-auto">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type="text"
              placeholder="Search articles..."
              className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none focus:ring-1 focus:ring-electric/50 transition"
            />
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="px-6 mb-12">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-wrap items-center justify-center gap-3">
            {categories.map((category, index) => (
              <button
                key={category.slug}
                className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                  index === 0
                    ? "bg-electric text-midnight"
                    : "bg-white/5 text-white/70 hover:bg-white/10"
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Post */}
      <section className="px-6 mb-16">
        <div className="max-w-6xl mx-auto">
          <Link
            href={`/blog/${featuredPost.slug}`}
            className="block group"
          >
            <div className="grid md:grid-cols-2 gap-8 p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-electric/30 transition">
              {/* Image */}
              <div className="aspect-video rounded-xl bg-gradient-to-br from-electric/20 to-purple-500/20 flex items-center justify-center">
                <span className="text-white/30">Featured Image</span>
              </div>

              {/* Content */}
              <div className="flex flex-col justify-center">
                <div className="flex items-center gap-3 mb-4">
                  <span className="px-3 py-1 rounded-full bg-electric/10 text-electric text-xs font-medium">
                    {featuredPost.category}
                  </span>
                  <span className="text-white/40 text-sm">Featured</span>
                </div>

                <h2 className="text-2xl md:text-3xl font-bold mb-3 group-hover:text-electric transition">
                  {featuredPost.title}
                </h2>

                <p className="text-white/60 mb-6">
                  {featuredPost.excerpt}
                </p>

                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-electric to-purple-500 flex items-center justify-center text-sm font-bold">
                      {featuredPost.author.name.charAt(0)}
                    </div>
                    <div>
                      <div className="text-sm font-medium">{featuredPost.author.name}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-white/50">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {featuredPost.publishedAt}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {featuredPost.readTime}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        </div>
      </section>

      {/* Posts Grid */}
      <section className="px-6 pb-24">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {posts.map((post) => (
              <Link
                key={post.slug}
                href={`/blog/${post.slug}`}
                className="card group hover:border-electric/30 transition-all"
              >
                {/* Image placeholder */}
                <div className="aspect-video rounded-xl bg-gradient-to-br from-white/5 to-white/0 mb-4 flex items-center justify-center">
                  <span className="text-white/20 text-sm">Image</span>
                </div>

                {/* Category */}
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-white/5 text-xs text-white/60 mb-3">
                  <Tag className="w-3 h-3" />
                  {post.category}
                </span>

                {/* Title */}
                <h3 className="text-lg font-semibold mb-2 group-hover:text-electric transition line-clamp-2">
                  {post.title}
                </h3>

                {/* Excerpt */}
                <p className="text-white/60 text-sm mb-4 line-clamp-2">
                  {post.excerpt}
                </p>

                {/* Meta */}
                <div className="flex items-center justify-between text-sm text-white/50">
                  <span>{post.author.name}</span>
                  <span>{post.readTime}</span>
                </div>
              </Link>
            ))}
          </div>

          {/* Load More */}
          <div className="text-center mt-12">
            <button className="btn-secondary">
              Load More Articles
            </button>
          </div>
        </div>
      </section>

      {/* Newsletter CTA */}
      <section className="py-20 px-6 bg-midnight-50/30">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            Stay Ahead of the Curve
          </h2>
          <p className="text-white/60 mb-8">
            Get weekly AI marketing insights delivered to your inbox
          </p>
          <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-5 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none"
            />
            <button type="submit" className="btn-primary whitespace-nowrap">
              Subscribe
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}

