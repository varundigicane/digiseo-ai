import { expect, test } from "@playwright/test";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function uniqueEmail() {
  return `e2e+${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;
}

test.beforeAll(async ({ request }) => {
  const health = await request.get(`${API}/health`);
  expect(health.ok(), `API must be running at ${API}`).toBeTruthy();
});

test.describe("Auth (E2E-P0-01..04, NF-01)", () => {
  test("landing loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("DigiSEO AI").first()).toBeVisible();
  });

  test("signup lands on app with starter credits", async ({ page }) => {
    const email = uniqueEmail();
    await page.goto("/signup");
    await page.locator('input[name="full_name"]').fill("Playwright User");
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill("password123");
    await page.locator('input[name="organization_name"]').fill("PW Org");
    await page.locator('input[name="workspace_name"]').fill("Default");
    await page.getByRole("button", { name: /Create account/i }).click();
    await expect(page).toHaveURL(/\/app/, { timeout: 30_000 });
    await expect(page.getByText(/starter/i).first()).toBeVisible({ timeout: 20_000 });
    await expect(page.getByText(/credits/i).first()).toBeVisible();
  });

  test("invalid login stays on login", async ({ page }) => {
    await page.goto("/login");
    await page.locator('input[name="email"]').fill("nobody@example.com");
    await page.locator('input[name="password"]').fill("wrongpass1");
    await page.getByRole("button", { name: /Sign in/i }).click();
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator("p").filter({ hasText: /.+/ }).first()).toBeVisible({
      timeout: 10_000,
    });
    const session = await page.evaluate(() => localStorage.getItem("digiseo_session"));
    expect(session).toBeNull();
  });

  test("unauthenticated /app redirects to login", async ({ page }) => {
    await page.goto("/app");
    await page.evaluate(() => localStorage.clear());
    await page.goto("/app");
    await expect(page).toHaveURL(/\/login/, { timeout: 15_000 });
  });

  test("logout and login again", async ({ page }) => {
    const email = uniqueEmail();
    const password = "password123";
    await page.goto("/signup");
    await page.locator('input[name="full_name"]').fill("Round Trip");
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.locator('input[name="organization_name"]').fill("RT Org");
    await page.getByRole("button", { name: /Create account/i }).click();
    await expect(page).toHaveURL(/\/app/);
    await page.getByRole("button", { name: /Sign out/i }).click();
    await expect(page).toHaveURL(/\/login/);
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole("button", { name: /Sign in/i }).click();
    await expect(page).toHaveURL(/\/app/, { timeout: 20_000 });
  });
});
