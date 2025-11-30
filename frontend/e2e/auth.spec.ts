import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should display login page", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
    await expect(page.getByPlaceholder(/email/i)).toBeVisible();
    await expect(page.getByPlaceholder(/password/i)).toBeVisible();
  });

  test("should display register page", async ({ page }) => {
    await page.goto("/register");
    await expect(
      page.getByRole("heading", { name: /create account/i })
    ).toBeVisible();
    await expect(page.getByPlaceholder(/email/i)).toBeVisible();
    await expect(page.getByPlaceholder(/full name/i)).toBeVisible();
  });

  test("should show error for invalid login", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "invalid@email.com");
    await page.fill('input[type="password"]', "wrongpassword");
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(
      page.getByText(/invalid|error|incorrect/i)
    ).toBeVisible({ timeout: 5000 });
  });

  test("should navigate between login and register", async ({ page }) => {
    await page.goto("/login");
    await page.click("text=Sign up");
    await expect(page).toHaveURL(/register/);

    await page.click("text=Sign in");
    await expect(page).toHaveURL(/login/);
  });
});

test.describe("Authenticated User", () => {
  test.use({
    storageState: "e2e/.auth/user.json",
  });

  test("should access dashboard after login", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByText(/command center/i)).toBeVisible();
  });

  test("should display user info in sidebar", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.locator("aside")).toBeVisible();
    // User avatar should be visible
    await expect(page.locator("aside").getByRole("button")).toBeVisible();
  });
});

