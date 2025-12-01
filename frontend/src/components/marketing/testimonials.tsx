"use client";

import { motion } from "framer-motion";
import { Star, Quote } from "lucide-react";
import { cn } from "@/lib/utils";

interface Testimonial {
  id: string;
  content: string;
  author: {
    name: string;
    role: string;
    company: string;
    avatar?: string;
  };
  rating?: number;
}

interface TestimonialsProps {
  title: string;
  subtitle: string;
  testimonials: Testimonial[];
}

export function Testimonials({ title, subtitle, testimonials }: TestimonialsProps) {
  return (
    <section className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">{title}</h2>
          <p className="text-xl text-white/60 max-w-2xl mx-auto">{subtitle}</p>
        </motion.div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="card relative"
            >
              {/* Quote Icon */}
              <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-electric flex items-center justify-center">
                <Quote className="w-4 h-4 text-white" />
              </div>

              {/* Rating */}
              {testimonial.rating && (
                <div className="flex items-center gap-1 mb-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      className={cn(
                        "w-4 h-4",
                        i < testimonial.rating!
                          ? "fill-yellow-400 text-yellow-400"
                          : "text-white/20"
                      )}
                    />
                  ))}
                </div>
              )}

              {/* Content */}
              <p className="text-white/80 mb-6 leading-relaxed">
                &ldquo;{testimonial.content}&rdquo;
              </p>

              {/* Author */}
              <div className="flex items-center gap-3">
                {testimonial.author.avatar ? (
                  <img
                    src={testimonial.author.avatar}
                    alt={testimonial.author.name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-electric to-purple-500 flex items-center justify-center text-lg font-bold">
                    {testimonial.author.name.charAt(0)}
                  </div>
                )}
                <div>
                  <div className="font-semibold">{testimonial.author.name}</div>
                  <div className="text-sm text-white/50">
                    {testimonial.author.role} at {testimonial.author.company}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

interface LogoCloudProps {
  title?: string;
  logos: {
    name: string;
    logo: React.ReactNode;
  }[];
}

export function LogoCloud({ title = "Trusted by leading companies", logos }: LogoCloudProps) {
  return (
    <section className="py-16 px-6 border-y border-white/5">
      <div className="max-w-7xl mx-auto">
        <p className="text-center text-white/40 text-sm mb-8">{title}</p>
        <div className="flex flex-wrap items-center justify-center gap-12">
          {logos.map((logo, index) => (
            <motion.div
              key={logo.name}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              className="opacity-40 hover:opacity-80 transition-opacity grayscale hover:grayscale-0"
            >
              {logo.logo}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

interface StatsProps {
  stats: {
    value: string;
    label: string;
    description?: string;
  }[];
}

export function Stats({ stats }: StatsProps) {
  return (
    <section className="py-20 px-6 bg-neural-gradient/5 border-y border-electric/10">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl font-bold gradient-text mb-2">
                {stat.value}
              </div>
              <div className="text-white/80 font-medium">{stat.label}</div>
              {stat.description && (
                <div className="text-white/50 text-sm mt-1">{stat.description}</div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

