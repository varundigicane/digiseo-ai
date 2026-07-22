import { expect, test } from "@playwright/test";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function uniqueEmail() {
  return `e2e+plan-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;
}

test.beforeAll(async ({ request }) => {
  const health = await request.get(`${API}/health`);
  expect(health.ok(), `API must be running at ${API}`).toBeTruthy();
});

async function signup(page: import("@playwright/test").Page) {
  const email = uniqueEmail();
  await page.goto("/signup");
  await page.locator('input[name="full_name"]').fill("Plan Gate User");
  await page.locator('input[name="email"]').fill(email);
  await page.locator('input[name="password"]').fill("password123");
  await page.locator('input[name="organization_name"]').fill(`Plan Org ${Date.now()}`);
  await page.getByRole("button", { name: /Create account/i }).click();
  await expect(page).toHaveURL(/\/app/, { timeout: 45_000 });
  await expect(page.getByText(/credits/i).first()).toBeVisible({ timeout: 20_000 });
  return email;
}

test.describe("Plan gates UI (E2E-P1 / P2)", () => {
  test("billing mock upgrade to professional", async ({ page }) => {
    await signup(page);
    await page.getByRole("link", { name: "Billing" }).click();
    await expect(page.getByText(/starter/i).first()).toBeVisible();
    await page.getByRole("button", { name: /professional/i }).click();
    await expect(page.getByText(/professional|Upgraded/i).first()).toBeVisible({
      timeout: 20_000,
    });
  });

  test("social flow after auto-upgrade from page", async ({ page }) => {
    await signup(page);
    await page.getByRole("link", { name: "Onboarding" }).click();
    await page.locator('input[name="url"]').fill("https://social-demo.example.com");
    await page.getByRole("button", { name: /Connect & crawl/i }).click();
    await expect(page.locator("p.text-accent").filter({ hasText: /pages indexed|GSC connected/i })).toBeVisible({
      timeout: 60_000,
    });

    await page.getByRole("link", { name: "Social" }).click();
    await expect(page.getByRole("heading", { name: /Social/i })).toBeVisible();
    await page.locator('input[name="topic"]').fill("Announce DigiSEO AI");
    await page.getByRole("button", { name: /Generate post/i }).click();
    await expect(page.getByText(/Draft created|Failed|Announce/i).first()).toBeVisible({
      timeout: 60_000,
    });
  });

  test("workflows page launches business template", async ({ page }) => {
    await signup(page);
    await page.getByRole("link", { name: "Onboarding" }).click();
    await page.locator('input[name="url"]').fill("https://workflow-demo.example.com");
    await page.getByRole("button", { name: /Connect & crawl/i }).click();
    await expect(page.locator("p.text-accent").filter({ hasText: /pages indexed|GSC connected/i })).toBeVisible({
      timeout: 60_000,
    });

    await page.getByRole("link", { name: "Workflows" }).click();
    await expect(page.getByRole("heading", { name: /workflow/i })).toBeVisible();
    const launch = page.getByRole("button", { name: /^Launch$/i }).first();
    await expect(launch).toBeVisible({ timeout: 30_000 });
    await launch.click();
    await expect(page.getByText(/completed|Running|Workflow|Failed/i).first()).toBeVisible({
      timeout: 120_000,
    });
  });
});
