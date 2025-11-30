// This file configures the initialization of Sentry on the client.
import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    
    // Environment and release
    environment: process.env.NODE_ENV,
    
    // Performance Monitoring
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
    
    // Session Replay
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
    
    // Debug mode (disable in production)
    debug: false,
    
    // Filter breadcrumbs
    beforeBreadcrumb(breadcrumb) {
      // Don't track console breadcrumbs in production
      if (breadcrumb.category === "console" && process.env.NODE_ENV === "production") {
        return null;
      }
      return breadcrumb;
    },
    
    // Filter errors
    beforeSend(event) {
      // Don't send errors for local development
      if (process.env.NODE_ENV === "development") {
        console.log("Sentry error (dev):", event);
        return null;
      }
      return event;
    },
  });
}

