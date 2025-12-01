"use client";

import { useState } from "react";
import {
  Mail,
  MessageSquare,
  MapPin,
  Clock,
  Send,
  Building2,
  HeadphonesIcon,
  FileText,
  Twitter,
  Linkedin,
  Github,
} from "lucide-react";

const contactOptions = [
  {
    icon: HeadphonesIcon,
    title: "Support",
    description: "Get help with your account or technical issues",
    email: "support@neurocron.com",
    responseTime: "< 4 hours",
  },
  {
    icon: Building2,
    title: "Sales",
    description: "Talk to us about enterprise plans and custom solutions",
    email: "sales@neurocron.com",
    responseTime: "< 24 hours",
  },
  {
    icon: FileText,
    title: "Press",
    description: "Media inquiries and partnership opportunities",
    email: "press@neurocron.com",
    responseTime: "< 48 hours",
  },
];

const inquiryTypes = [
  { value: "support", label: "Technical Support" },
  { value: "sales", label: "Sales Inquiry" },
  { value: "enterprise", label: "Enterprise Solutions" },
  { value: "partnership", label: "Partnership" },
  { value: "press", label: "Press / Media" },
  { value: "other", label: "Other" },
];

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    inquiryType: "",
    subject: "",
    message: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    
    setIsSubmitting(false);
    setIsSubmitted(true);
  };

  if (isSubmitted) {
    return (
      <div className="pt-32 min-h-screen flex items-center justify-center px-6">
        <div className="max-w-md text-center">
          <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6">
            <Send className="w-10 h-10 text-green-400" />
          </div>
          <h1 className="text-3xl font-bold mb-4">Message Sent!</h1>
          <p className="text-white/60 mb-8">
            Thanks for reaching out. We&apos;ll get back to you within 24 hours.
          </p>
          <a href="/" className="btn-primary">
            Back to Home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-32">
      {/* Hero */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Get in <span className="gradient-text">Touch</span>
          </h1>
          <p className="text-xl text-white/60">
            Have a question or want to learn more? We&apos;d love to hear from you.
          </p>
        </div>
      </section>

      {/* Contact Options */}
      <section className="px-6 mb-16">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-3 gap-6">
            {contactOptions.map((option) => (
              <div key={option.title} className="card text-center">
                <div className="w-14 h-14 rounded-2xl bg-electric/10 flex items-center justify-center mx-auto mb-4">
                  <option.icon className="w-7 h-7 text-electric" />
                </div>
                <h3 className="font-semibold text-lg mb-2">{option.title}</h3>
                <p className="text-white/60 text-sm mb-4">{option.description}</p>
                <a
                  href={`mailto:${option.email}`}
                  className="text-electric hover:underline font-medium"
                >
                  {option.email}
                </a>
                <p className="text-xs text-white/40 mt-2">
                  Response time: {option.responseTime}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <section className="px-6 pb-24">
        <div className="max-w-5xl mx-auto">
          <div className="grid lg:grid-cols-5 gap-12">
            {/* Form */}
            <div className="lg:col-span-3">
              <div className="card lg:p-8">
                <h2 className="text-2xl font-bold mb-6">Send us a message</h2>
                
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="grid md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-sm text-white/60 mb-2">
                        Your Name *
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) =>
                          setFormData({ ...formData, name: e.target.value })
                        }
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                        placeholder="John Doe"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-white/60 mb-2">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        required
                        value={formData.email}
                        onChange={(e) =>
                          setFormData({ ...formData, email: e.target.value })
                        }
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                        placeholder="john@company.com"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-sm text-white/60 mb-2">
                        Company
                      </label>
                      <input
                        type="text"
                        value={formData.company}
                        onChange={(e) =>
                          setFormData({ ...formData, company: e.target.value })
                        }
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                        placeholder="Your Company"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-white/60 mb-2">
                        Inquiry Type *
                      </label>
                      <select
                        required
                        value={formData.inquiryType}
                        onChange={(e) =>
                          setFormData({ ...formData, inquiryType: e.target.value })
                        }
                        className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                      >
                        <option value="">Select type...</option>
                        {inquiryTypes.map((type) => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-white/60 mb-2">
                      Subject *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.subject}
                      onChange={(e) =>
                        setFormData({ ...formData, subject: e.target.value })
                      }
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition"
                      placeholder="How can we help?"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-white/60 mb-2">
                      Message *
                    </label>
                    <textarea
                      required
                      value={formData.message}
                      onChange={(e) =>
                        setFormData({ ...formData, message: e.target.value })
                      }
                      rows={5}
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 focus:border-electric/50 focus:outline-none transition resize-none"
                      placeholder="Tell us more about your inquiry..."
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full btn-primary flex items-center justify-center gap-2 py-4 disabled:opacity-50"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="w-5 h-5" />
                        Send Message
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-2 space-y-6">
              {/* Office */}
              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-electric/10 flex items-center justify-center">
                    <MapPin className="w-5 h-5 text-electric" />
                  </div>
                  <h3 className="font-semibold">Our Office</h3>
                </div>
                <p className="text-white/60 text-sm leading-relaxed">
                  NeuroCron Inc.
                  <br />
                  548 Market Street, Suite 12345
                  <br />
                  San Francisco, CA 94104
                  <br />
                  United States
                </p>
              </div>

              {/* Hours */}
              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-green-400" />
                  </div>
                  <h3 className="font-semibold">Business Hours</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-white/60">Monday - Friday</span>
                    <span>9:00 AM - 6:00 PM PST</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Saturday - Sunday</span>
                    <span className="text-white/40">Closed</span>
                  </div>
                </div>
              </div>

              {/* Social */}
              <div className="card">
                <h3 className="font-semibold mb-4">Follow Us</h3>
                <div className="flex items-center gap-3">
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

              {/* FAQ Link */}
              <div className="card bg-electric/5 border-electric/20">
                <div className="flex items-center gap-3 mb-3">
                  <MessageSquare className="w-5 h-5 text-electric" />
                  <h3 className="font-semibold">Looking for quick answers?</h3>
                </div>
                <p className="text-white/60 text-sm mb-4">
                  Check out our FAQ section for common questions.
                </p>
                <a
                  href="/docs"
                  className="text-electric hover:underline text-sm font-medium"
                >
                  Visit Help Center →
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

