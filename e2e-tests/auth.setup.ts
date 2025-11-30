import { test as setup, expect } from "@playwright/test";

const authFile = "e2e/.auth/user.json";

setup("authenticate", async ({ page }) => {
  // Go to login page
  await page.goto("/login");
  
  // Fill login form
  await page.fill('input[type="email"]', "demo@neurocron.com");
  await page.fill('input[type="password"]', "demo123");
  
  // Click login
  await page.click('button[type="submit"]');
  
  // Wait for navigation to dashboard
  await page.waitForURL(/dashboard/, { timeout: 10000 });
  
  // Save authenticated state
  await page.context().storageState({ path: authFile });
});

