import { Metadata } from "next";
import Link from "next/link";
import { Calendar, Clock, ArrowLeft, Share2, Twitter, Linkedin, Link2, ChevronRight } from "lucide-react";
import { CTASection } from "@/components/marketing/cta-section";

interface BlogPostPageProps {
  params: Promise<{ slug: string }>;
}

// This would come from a CMS or database
const getPost = async (slug: string) => {
  // Mock data - in production, fetch from API/CMS
  return {
    slug,
    title: "The Future of AI Marketing: What to Expect in 2025",
    excerpt: "Autonomous systems, hyper-personalization, and predictive analytics are reshaping how we think about marketing.",
    content: `
## The Rise of Autonomous Marketing

Marketing is undergoing its biggest transformation since the invention of the internet. AI-powered systems are now capable of not just assisting marketers, but actually running campaigns autonomously.

### What Does Autonomous Marketing Mean?

Autonomous marketing refers to AI systems that can:

- **Plan** - Generate complete marketing strategies based on business goals
- **Execute** - Launch and manage campaigns across multiple channels
- **Optimize** - Continuously improve performance without human intervention
- **Learn** - Adapt to market changes and customer behavior in real-time

This isn't science fiction. It's happening now. Platforms like NeuroCron are already helping hundreds of businesses run their entire marketing operation with minimal human oversight.

## Key Trends for 2025

### 1. Hyper-Personalization at Scale

Traditional personalization—inserting a first name into an email—is becoming obsolete. Next-generation AI can create truly individualized experiences for millions of customers simultaneously.

Expect to see:
- Dynamic content that adapts in real-time based on user behavior
- Personalized pricing and offer strategies
- Custom creative variations generated for each customer segment

### 2. Predictive Analytics Become Standard

The ability to forecast campaign performance before spending a dollar will become a baseline expectation. AI models can now predict:

- Campaign ROI with 80%+ accuracy
- Customer lifetime value from first interaction
- Optimal budget allocation across channels
- Best times to reach each customer segment

### 3. Cross-Channel Orchestration

Siloed channel management is dying. AI systems can now orchestrate campaigns across email, social, ads, and content simultaneously—ensuring consistent messaging and optimal budget allocation.

## Preparing for the AI Marketing Future

To thrive in this new landscape, marketing teams need to:

1. **Embrace AI as a partner**, not a threat
2. **Focus on strategy and creativity** while letting AI handle execution
3. **Invest in data quality** - AI is only as good as the data it learns from
4. **Stay curious** - the technology is evolving rapidly

## Conclusion

The future of marketing is autonomous, but it's not about replacing humans. It's about amplifying human creativity and strategic thinking with AI-powered execution.

The teams that embrace this shift will have an unfair advantage. Those that resist will find themselves outpaced by more agile competitors.

Ready to experience autonomous marketing? [Start your free trial](/register) and see the future today.
    `,
    category: "AI Marketing",
    author: {
      name: "Sarah Martinez",
      role: "CTO",
      bio: "Ex-Google AI researcher. Building the future of autonomous marketing at NeuroCron.",
    },
    publishedAt: "Nov 28, 2024",
    readTime: "8 min read",
    tags: ["AI", "Marketing", "Automation", "Future Trends"],
  };
};

export async function generateMetadata({ params }: BlogPostPageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const post = await getPost(resolvedParams.slug);
  
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: `${post.title} | NeuroCron Blog`,
      description: post.excerpt,
      type: "article",
      publishedTime: post.publishedAt,
      authors: [post.author.name],
    },
  };
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const resolvedParams = await params;
  const post = await getPost(resolvedParams.slug);

  // Schema.org Article markup
  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.excerpt,
    author: {
      "@type": "Person",
      name: post.author.name,
      jobTitle: post.author.role,
    },
    publisher: {
      "@type": "Organization",
      name: "NeuroCron",
      logo: {
        "@type": "ImageObject",
        url: "https://neurocron.com/logo.png",
      },
    },
    datePublished: post.publishedAt,
  };

  return (
    <div className="pt-32">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />

      {/* Header */}
      <article className="px-6">
        <div className="max-w-3xl mx-auto">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-white/50 mb-8">
            <Link href="/blog" className="hover:text-white transition flex items-center gap-1">
              <ArrowLeft className="w-4 h-4" />
              Back to Blog
            </Link>
            <ChevronRight className="w-4 h-4" />
            <span>{post.category}</span>
          </nav>

          {/* Category & Meta */}
          <div className="flex items-center gap-4 mb-6">
            <span className="px-3 py-1 rounded-full bg-electric/10 text-electric text-sm font-medium">
              {post.category}
            </span>
            <span className="flex items-center gap-1 text-sm text-white/50">
              <Calendar className="w-4 h-4" />
              {post.publishedAt}
            </span>
            <span className="flex items-center gap-1 text-sm text-white/50">
              <Clock className="w-4 h-4" />
              {post.readTime}
            </span>
          </div>

          {/* Title */}
          <h1 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
            {post.title}
          </h1>

          {/* Author */}
          <div className="flex items-center gap-4 pb-8 border-b border-white/10">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-electric to-purple-500 flex items-center justify-center text-lg font-bold">
              {post.author.name.charAt(0)}
            </div>
            <div>
              <div className="font-medium">{post.author.name}</div>
              <div className="text-sm text-white/50">{post.author.role}</div>
            </div>
          </div>

          {/* Featured Image */}
          <div className="aspect-video rounded-2xl bg-gradient-to-br from-electric/20 to-purple-500/20 my-8 flex items-center justify-center">
            <span className="text-white/30">Featured Image</span>
          </div>

          {/* Content */}
          <div 
            className="prose prose-invert prose-lg max-w-none
              prose-headings:font-bold prose-headings:text-white
              prose-h2:text-3xl prose-h2:mt-12 prose-h2:mb-4
              prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3
              prose-p:text-white/70 prose-p:leading-relaxed
              prose-a:text-electric prose-a:no-underline hover:prose-a:underline
              prose-strong:text-white
              prose-ul:text-white/70 prose-ol:text-white/70
              prose-li:marker:text-electric"
            dangerouslySetInnerHTML={{ __html: post.content.replace(/\n/g, '<br>').replace(/## /g, '<h2>').replace(/### /g, '<h3>').replace(/<br>- /g, '</li><li>').replace(/<br><br>/g, '</p><p>') }}
          />

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mt-12 pt-8 border-t border-white/10">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="px-3 py-1 rounded-full bg-white/5 text-white/60 text-sm"
              >
                #{tag}
              </span>
            ))}
          </div>

          {/* Share */}
          <div className="flex items-center gap-4 mt-8">
            <span className="text-white/50 flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              Share:
            </span>
            <button className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition">
              <Twitter className="w-5 h-5 text-white/60" />
            </button>
            <button className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition">
              <Linkedin className="w-5 h-5 text-white/60" />
            </button>
            <button className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-white/10 transition">
              <Link2 className="w-5 h-5 text-white/60" />
            </button>
          </div>

          {/* Author Bio */}
          <div className="card mt-12">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-electric to-purple-500 flex items-center justify-center text-2xl font-bold flex-shrink-0">
                {post.author.name.charAt(0)}
              </div>
              <div>
                <div className="font-semibold text-lg">{post.author.name}</div>
                <div className="text-electric text-sm mb-2">{post.author.role}</div>
                <p className="text-white/60">{post.author.bio}</p>
              </div>
            </div>
          </div>
        </div>
      </article>

      {/* Related Posts */}
      <section className="py-20 px-6 mt-12 bg-midnight-50/30">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold mb-8">Related Articles</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { title: "How AutoCron Delivers 10x Marketing Productivity", category: "Automation" },
              { title: "AI Content Generation: Best Practices for 2025", category: "AI Marketing" },
              { title: "5 Marketing Automation Mistakes to Avoid", category: "Strategy" },
            ].map((related, index) => (
              <Link
                key={index}
                href="/blog/related-post"
                className="card group hover:border-electric/30 transition"
              >
                <div className="aspect-video rounded-xl bg-gradient-to-br from-white/5 to-white/0 mb-4" />
                <span className="text-electric text-xs">{related.category}</span>
                <h3 className="font-semibold mt-2 group-hover:text-electric transition">
                  {related.title}
                </h3>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Experience AI Marketing?"
        subtitle="Start your free 14-day trial today"
        primaryCta={{ text: "Start Free Trial", href: "/register" }}
        secondaryCta={{ text: "Book a Demo", href: "/demo" }}
        features={["No credit card required", "Full platform access"]}
      />
    </div>
  );
}

