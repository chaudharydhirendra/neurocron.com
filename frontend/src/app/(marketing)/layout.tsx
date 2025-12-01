"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Menu,
  X,
  ChevronDown,
  Sparkles,
  Zap,
  BarChart3,
  Target,
  Shield,
  Users,
  Mail,
  Twitter,
  Linkedin,
  Github,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  {
    name: "Product",
    href: "/features",
    children: [
      { name: "All Features", href: "/features", icon: Sparkles },
      { name: "Strategy Suite", href: "/features#strategy", icon: Brain },
      { name: "Execution Suite", href: "/features#execution", icon: Zap },
      { name: "Analytics Suite", href: "/features#analytics", icon: BarChart3 },
      { name: "Intelligence Suite", href: "/features#intelligence", icon: Target },
    ],
  },
  { name: "Pricing", href: "/pricing" },
  { name: "About", href: "/about" },
  { name: "Blog", href: "/blog" },
  { name: "Docs", href: "/docs" },
];

const footerLinks = {
  product: [
    { name: "Features", href: "/features" },
    { name: "Pricing", href: "/pricing" },
    { name: "Integrations", href: "/features#integrations" },
    { name: "API", href: "/docs/api" },
    { name: "Changelog", href: "/blog/changelog" },
  ],
  company: [
    { name: "About", href: "/about" },
    { name: "Blog", href: "/blog" },
    { name: "Careers", href: "/careers" },
    { name: "Contact", href: "/contact" },
    { name: "Press Kit", href: "/press" },
  ],
  resources: [
    { name: "Documentation", href: "/docs" },
    { name: "Help Center", href: "/docs/help" },
    { name: "Community", href: "/community" },
    { name: "Status", href: "https://status.neurocron.com" },
    { name: "Partners", href: "/partners" },
  ],
  legal: [
    { name: "Privacy Policy", href: "/privacy" },
    { name: "Terms of Service", href: "/terms" },
    { name: "Cookie Policy", href: "/cookies" },
    { name: "GDPR", href: "/gdpr" },
    { name: "Security", href: "/security" },
  ],
};

function NavDropdown({ item }: { item: (typeof navigation)[0] }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div
      className="relative"
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <button className="flex items-center gap-1 text-white/70 hover:text-white transition py-2">
        {item.name}
        <ChevronDown className={cn("w-4 h-4 transition-transform", isOpen && "rotate-180")} />
      </button>
      <AnimatePresence>
        {isOpen && item.children && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full left-0 mt-2 w-64 p-2 rounded-2xl bg-midnight-100 border border-white/10 shadow-2xl"
          >
            {item.children.map((child) => (
              <Link
                key={child.href}
                href={child.href}
                className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition group"
              >
                <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center group-hover:bg-electric/20 transition">
                  <child.icon className="w-5 h-5 text-electric" />
                </div>
                <span className="font-medium text-white/80 group-hover:text-white">
                  {child.name}
                </span>
              </Link>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Header() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        isScrolled
          ? "bg-midnight/80 backdrop-blur-xl border-b border-white/5 py-3"
          : "bg-transparent py-5"
      )}
    >
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-11 h-11 rounded-xl bg-neural-gradient flex items-center justify-center group-hover:scale-105 transition-transform">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">NeuroCron</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden lg:flex items-center gap-8">
          {navigation.map((item) =>
            item.children ? (
              <NavDropdown key={item.name} item={item} />
            ) : (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "text-white/70 hover:text-white transition py-2",
                  pathname === item.href && "text-white"
                )}
              >
                {item.name}
              </Link>
            )
          )}
        </nav>

        {/* CTA Buttons */}
        <div className="hidden lg:flex items-center gap-4">
          <Link
            href="/login"
            className="text-white/70 hover:text-white transition font-medium"
          >
            Log in
          </Link>
          <Link
            href="/register"
            className="btn-primary flex items-center gap-2"
          >
            Start Free Trial
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="lg:hidden p-2 rounded-xl hover:bg-white/5"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden bg-midnight-100 border-t border-white/5"
          >
            <div className="px-6 py-6 space-y-4">
              {navigation.map((item) => (
                <div key={item.name}>
                  <Link
                    href={item.href}
                    className="block py-2 text-lg font-medium"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                  {item.children && (
                    <div className="pl-4 mt-2 space-y-2">
                      {item.children.map((child) => (
                        <Link
                          key={child.href}
                          href={child.href}
                          className="block py-2 text-white/60"
                          onClick={() => setIsMobileMenuOpen(false)}
                        >
                          {child.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div className="pt-4 border-t border-white/10 space-y-3">
                <Link
                  href="/login"
                  className="block w-full text-center py-3 rounded-xl border border-white/10 font-medium"
                >
                  Log in
                </Link>
                <Link
                  href="/register"
                  className="block w-full text-center py-3 rounded-xl bg-neural-gradient font-medium"
                >
                  Start Free Trial
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

function Footer() {
  const [email, setEmail] = useState("");

  const handleNewsletterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Newsletter submission logic
    setEmail("");
  };

  return (
    <footer className="bg-midnight-100 border-t border-white/5">
      {/* Newsletter Section */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-8 p-8 rounded-3xl bg-neural-gradient/5 border border-electric/20">
          <div>
            <h3 className="text-2xl font-bold mb-2">Stay ahead of the curve</h3>
            <p className="text-white/60">
              Get the latest AI marketing insights delivered to your inbox.
            </p>
          </div>
          <form onSubmit={handleNewsletterSubmit} className="flex gap-3 w-full lg:w-auto">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              className="flex-1 lg:w-80 px-5 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none focus:ring-1 focus:ring-electric/50 transition"
              required
            />
            <button
              type="submit"
              className="btn-primary whitespace-nowrap flex items-center gap-2"
            >
              Subscribe
              <Mail className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Links Grid */}
      <div className="max-w-7xl mx-auto px-6 pb-12">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8">
          {/* Brand Column */}
          <div className="col-span-2 md:col-span-4 lg:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-xl bg-neural-gradient flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold">NeuroCron</span>
            </Link>
            <p className="text-white/50 text-sm mb-6">
              The autonomous marketing brain that runs your entire marketing stack.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://twitter.com/neurocron"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-white/10 transition"
              >
                <Twitter className="w-5 h-5 text-white/60" />
              </a>
              <a
                href="https://linkedin.com/company/neurocron"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-white/10 transition"
              >
                <Linkedin className="w-5 h-5 text-white/60" />
              </a>
              <a
                href="https://github.com/neurocron"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-white/10 transition"
              >
                <Github className="w-5 h-5 text-white/60" />
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white/90">Product</h4>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/50 hover:text-white transition text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white/90">Company</h4>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/50 hover:text-white transition text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white/90">Resources</h4>
            <ul className="space-y-3">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/50 hover:text-white transition text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white/90">Legal</h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-white/50 hover:text-white transition text-sm"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-white/40">
            <Shield className="w-4 h-4" />
            <span>SOC 2 Compliant</span>
            <span className="mx-2">•</span>
            <span>GDPR Ready</span>
            <span className="mx-2">•</span>
            <span>CCPA Compliant</span>
          </div>
          <p className="text-sm text-white/40">
            © {new Date().getFullYear()} NeuroCron. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-midnight neural-bg">
      <Header />
      <main>{children}</main>
      <Footer />
    </div>
  );
}

