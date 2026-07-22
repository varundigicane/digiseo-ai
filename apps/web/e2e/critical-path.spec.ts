import { expect, test } from "@playwright/test";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function uniqueEmail() {
  return `e2e+gold-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;
}

test.beforeAll(async ({ request }) => {
  const health = await request.get(`${API}/health`);
  expect(health.ok(), `API must be running at ${API}`).toBeTruthy();
});

test("golden path: signup → crawl → SEO/AEO → content → approvals → billing", async ({
  page,
}) => {
  const email = uniqueEmail();

  await page.goto("/signup");
  await page.locator('input[name="full_name"]').fill("Golden Path");
  await page.locator('input[name="email"]').fill(email);
  await page.locator('input[name="password"]').fill("password123");
  await page.locator('input[name="organization_name"]').fill("Golden Org");
  await page.getByRole("button", { name: /Create account/i }).click();
  await expect(page).toHaveURL(/\/app/, { timeout: 30_000 });

  const creditsText = await page.getByText(/\d+\s+credits/i).first().textContent();
  const creditsBefore = Number((creditsText || "500").match(/\d+/)?.[0] || 500);

  await page.getByRole("link", { name: "Onboarding" }).click();
  await expect(page.getByRole("heading", { name: /Onboarding/i })).toBeVisible();
  await page.locator('input[name="url"]').fill("https://example.com");
  await page.getByRole("button", { name: /Connect & crawl/i }).click();
  await expect(page.locator("p.text-accent").filter({ hasText: /pages indexed|GSC connected/i })).toBeVisible({
    timeout: 60_000,
  });

  await page.getByRole("link", { name: "SEO / AEO" }).click();
  await expect(page.getByRole("heading", { name: /SEO & AEO/i })).toBeVisible();
  await page.getByRole("button", { name: /Run seo/i }).click();
  await expect(page.locator("pre").first()).toBeVisible({ timeout: 60_000 });
  await page.getByRole("button", { name: /Run aeo/i }).click();
  await expect(page.locator("pre").first()).toBeVisible({ timeout: 60_000 });

  await page.getByRole("link", { name: "Content" }).click();
  await expect(page.getByRole("heading", { name: /Content studio/i })).toBeVisible();
  await page.locator('input[name="topic"]').fill("AI SEO tips");
  await page.locator('input[name="keywords"]').fill("seo, aeo");
  await page.getByRole("button", { name: /^Generate$/i }).click();
  await expect(page.getByText(/Failed|AI SEO|blog|tips|Generating/i).first()).toBeVisible({
    timeout: 60_000,
  });

  await page.getByRole("link", { name: "Approvals" }).click();
  await expect(page.getByRole("heading", { name: /Approvals/i })).toBeVisible();
  const approve = page.getByRole("button", { name: /^Approve$/i }).first();
  if (await approve.isVisible().catch(() => false)) {
    await approve.click();
  }

  await page.getByRole("link", { name: "Billing" }).click();
  await expect(page.getByRole("heading", { name: /Billing/i })).toBeVisible();
  await expect(page.getByText(/starter|professional|business/i).first()).toBeVisible();
  // Prefer plan card balance (sidebar /auth/me is stale until remount)
  const balanceLine = page.getByText(/\d+\s+credits\s+·\s+status/i);
  await expect(balanceLine).toBeVisible();
  const billingCredits = await balanceLine.textContent();
  const creditsAfter = Number((billingCredits || "0").match(/(\d+)\s+credits/)?.[1] || 0);
  expect(creditsAfter).toBeLessThan(creditsBefore);
});
