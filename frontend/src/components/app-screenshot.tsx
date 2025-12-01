"use client";

import { useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface AppScreenshotProps {
  src: string;
  alt: string;
  className?: string;
  priority?: boolean;
  showBrowserChrome?: boolean;
  glowColor?: "electric" | "purple" | "green" | "orange";
  animate?: boolean;
}

export function AppScreenshot({
  src,
  alt,
  className,
  priority = false,
  showBrowserChrome = true,
  glowColor = "electric",
  animate = true,
}: AppScreenshotProps) {
  const [isLoaded, setIsLoaded] = useState(false);

  const glowColors = {
    electric: "shadow-electric/20",
    purple: "shadow-purple-500/20",
    green: "shadow-green-500/20",
    orange: "shadow-orange-500/20",
  };

  const Wrapper = animate ? motion.div : "div";
  const animationProps = animate
    ? {
        initial: { opacity: 0, y: 40 },
        whileInView: { opacity: 1, y: 0 },
        viewport: { once: true },
        transition: { duration: 0.6 },
      }
    : {};

  return (
    <Wrapper
      className={cn(
        "relative rounded-2xl overflow-hidden",
        `shadow-2xl ${glowColors[glowColor]}`,
        className
      )}
      {...animationProps}
    >
      {/* Browser Chrome */}
      {showBrowserChrome && (
        <div className="bg-midnight-100 border-b border-white/10 px-4 py-3 flex items-center gap-3">
          {/* Traffic Lights */}
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-green-500/80" />
          </div>
          
          {/* URL Bar */}
          <div className="flex-1 mx-4">
            <div className="bg-white/5 rounded-lg px-4 py-1.5 text-sm text-white/40 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span>app.neurocron.com</span>
            </div>
          </div>
        </div>
      )}

      {/* Screenshot */}
      <div className="relative bg-midnight">
        {/* Loading skeleton */}
        {!isLoaded && (
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-white/0 animate-pulse" />
        )}
        
        <Image
          src={src}
          alt={alt}
          width={1920}
          height={1080}
          className={cn(
            "w-full h-auto transition-opacity duration-500",
            isLoaded ? "opacity-100" : "opacity-0"
          )}
          priority={priority}
          onLoad={() => setIsLoaded(true)}
        />
      </div>

      {/* Reflection effect */}
      <div className="absolute inset-0 bg-gradient-to-t from-midnight via-transparent to-transparent opacity-30 pointer-events-none" />
    </Wrapper>
  );
}

interface ScreenshotGalleryProps {
  screenshots: {
    src: string;
    alt: string;
    title: string;
  }[];
  className?: string;
}

export function ScreenshotGallery({ screenshots, className }: ScreenshotGalleryProps) {
  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <div className={cn("space-y-6", className)}>
      {/* Main Screenshot */}
      <AppScreenshot
        src={screenshots[activeIndex].src}
        alt={screenshots[activeIndex].alt}
        priority
        animate={false}
      />

      {/* Thumbnails */}
      <div className="flex items-center justify-center gap-4">
        {screenshots.map((screenshot, index) => (
          <button
            key={index}
            onClick={() => setActiveIndex(index)}
            className={cn(
              "relative w-20 h-14 rounded-lg overflow-hidden border-2 transition-all",
              activeIndex === index
                ? "border-electric scale-105"
                : "border-white/10 opacity-60 hover:opacity-100"
            )}
          >
            <Image
              src={screenshot.src}
              alt={screenshot.title}
              fill
              className="object-cover"
            />
          </button>
        ))}
      </div>

      {/* Caption */}
      <p className="text-center text-white/60">
        {screenshots[activeIndex].title}
      </p>
    </div>
  );
}

