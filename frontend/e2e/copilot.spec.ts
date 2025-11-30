import { test, expect } from "@playwright/test";

test.describe("NeuroCopilot", () => {
  test.use({
    storageState: "e2e/.auth/user.json",
  });

  test("should display chat interface", async ({ page }) => {
    await page.goto("/copilot");
    
    // Should see chat input
    await expect(
      page.getByPlaceholder(/ask|message|type/i)
    ).toBeVisible();
  });

  test("should show suggestions", async ({ page }) => {
    await page.goto("/copilot");
    
    // Should see suggestion buttons
    await expect(
      page.getByText(/campaign|create|analyze/i).first()
    ).toBeVisible();
  });

  test("should send message and receive response", async ({ page }) => {
    await page.goto("/copilot");
    
    // Type a message
    await page.fill("textarea", "Hello, what can you help me with?");
    
    // Send message (press Enter or click send)
    await page.keyboard.press("Enter");
    
    // Wait for response
    await expect(
      page.locator('[data-testid="assistant-message"]').first()
    ).toBeVisible({ timeout: 10000 });
  });

  test("should display message history", async ({ page }) => {
    await page.goto("/copilot");
    
    // Send a message
    await page.fill("textarea", "Tell me about marketing automation");
    await page.keyboard.press("Enter");
    
    // User message should appear
    await expect(
      page.getByText("Tell me about marketing automation")
    ).toBeVisible();
  });
});

