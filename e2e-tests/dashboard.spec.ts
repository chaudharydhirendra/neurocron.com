import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
  test.use({
    storageState: "e2e/.auth/user.json",
  });

  test("should display main dashboard sections", async ({ page }) => {
    await page.goto("/dashboard");

    // Should see Command Center heading
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    // Should have sidebar navigation
    await expect(page.locator("aside")).toBeVisible();
  });

  test("should navigate to campaigns page", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click("text=Campaigns");
    await expect(page).toHaveURL(/campaigns/);
  });

  test("should navigate to NeuroCopilot", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click("text=NeuroCopilot");
    await expect(page).toHaveURL(/copilot/);
  });

  test("should navigate to Analytics", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click("text=Analytics");
    await expect(page).toHaveURL(/analytics/);
  });

  test("should navigate to Settings", async ({ page }) => {
    await page.goto("/dashboard");
    await page.click("text=Settings");
    await expect(page).toHaveURL(/settings/);
  });

  test("should open notification dropdown", async ({ page }) => {
    await page.goto("/dashboard");
    // Click notification bell
    await page.locator("header button").first().click();
    await expect(page.getByText(/notifications/i)).toBeVisible();
  });
});

test.describe("Mobile Dashboard", () => {
  test.use({
    viewport: { width: 375, height: 667 },
    storageState: "e2e/.auth/user.json",
  });

  test("should show hamburger menu on mobile", async ({ page }) => {
    await page.goto("/dashboard");
    // Sidebar should be hidden
    await expect(page.locator("aside")).not.toBeVisible();
    // Hamburger menu should be visible
    await expect(page.locator("header button").first()).toBeVisible();
  });

  test("should open mobile menu", async ({ page }) => {
    await page.goto("/dashboard");
    // Click hamburger
    await page.locator("header button").first().click();
    // Sidebar should now be visible
    await expect(page.locator("aside")).toBeVisible();
  });
});

