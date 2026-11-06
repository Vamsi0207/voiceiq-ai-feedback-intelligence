import { test, expect } from "@playwright/test";
test("real API dashboard, filters, navigation, upload and analysis", async ({
  page,
  request,
}) => {
  expect((await request.get("/api/health")).ok()).toBeTruthy();
  const baseline = await (await request.get("/api/dashboard/overview")).json();
  expect(baseline.total).toBeGreaterThanOrEqual(2400);
  await page.goto("/insights");
  await page
    .getByRole("button", { name: "Generate insights", exact: true })
    .click();
  await expect(page.getByText("PRIORITY SCORE").first()).toBeVisible();
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Feedback overview" }),
  ).toBeVisible();
  await expect(
    page.getByText(baseline.total.toLocaleString(), { exact: true }),
  ).toBeVisible();
  await page
    .getByLabel("Category", { exact: true })
    .selectOption("Fraud & Security");
  const filtered = await request.get(
    "/api/dashboard/overview?category=Fraud+%26+Security",
  );
  const stats = await filtered.json();
  await expect(
    page.getByText(stats.total.toLocaleString(), { exact: true }).first(),
  ).toBeVisible();
  await page.getByRole("button", { name: "Reset", exact: true }).click();
  await page.getByRole("link", { name: "Complaints", exact: true }).click();
  await page.getByLabel("Search complaints").fill("VIQ-00001");
  await expect(page.locator("tbody tr")).toHaveCount(1);
  await page.locator(".complaint-link").click();
  await expect(page.getByRole("dialog")).toContainText("Model");
  await page.getByRole("button", { name: "Close details" }).click();
  await page
    .getByRole("link", { name: "Recurring Issues", exact: true })
    .click();
  await page.getByRole("button", { name: "Explore evidence" }).first().click();
  await expect(page.getByRole("dialog")).toContainText("Supporting complaints");
  await page.getByRole("button", { name: "Close details" }).click();
  await page
    .getByRole("link", { name: "Product Insights", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Generate insights", exact: true })
    .click();
  await expect(page.getByText("PRIORITY SCORE").first()).toBeVisible();
  await page
    .getByRole("link", { name: "Model Evaluation", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Confusion matrix" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Upload Data", exact: true }).click();
  await page.getByLabel("Choose CSV file").setInputFiles({
    name: "browser.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(
      "complaint_id,complaint_text,created_at,source\nBROWSER-001,UPI payment failed but money deducted. I am unhappy.,2026-11-01,Browser test\nBROWSER-BAD,,bad,Browser test",
    ),
  });
  await page
    .getByRole("button", { name: "Import feedback", exact: true })
    .click();
  await expect(page.getByText("Import report", { exact: true })).toBeVisible();
  await expect(
    page.getByText("complaint_text must be 1–5,000 characters"),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Analyze pending feedback", exact: true })
    .click();
  await expect(page.locator(".job-status")).toContainText("completed", {
    timeout: 60000,
  });
  await page.getByRole("link", { name: "Settings", exact: true }).click();
  await expect(page.getByText("No-key mode")).toBeVisible();
  await page.goto("/insights");
  await page
    .getByRole("button", { name: "Generate insights", exact: true })
    .click();
  await expect(page.getByText("PRIORITY SCORE").first()).toBeVisible();
  await page.goto("/");
  await expect(
    page.getByText(
      (
        await (await request.get("/api/dashboard/overview")).json()
      ).total.toLocaleString(),
      { exact: true },
    ),
  ).toBeVisible();
  await page.locator(".recharts-surface").first().waitFor();
  await page.screenshot({ path: "../docs/dashboard.png", fullPage: true });
});
