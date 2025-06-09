import { expect, test } from "@playwright/test"

test.describe("Creator Dashboard Visual Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Login first to access protected routes
    await page.goto("/login")
    await page.getByPlaceholder("Email").fill("admin@example.com")
    await page.getByPlaceholder("Password").fill("changethis")
    await page.getByRole("button", { name: "Log In" }).click()
    await page.waitForURL("/")
  })

  test("Creator Dashboard - Setup View", async ({ page }) => {
    // Navigate to creator page (should show setup if no creator profile)
    await page.goto("/creator")

    // Wait for the page to load
    await page.waitForSelector("text=Become a Creator", { timeout: 10000 })

    // Take screenshot of the creator setup view
    await expect(page).toHaveScreenshot("creator-setup.png")
  })

  test("Creator Navigation in Sidebar", async ({ page }) => {
    // Check that creator link is visible in sidebar
    await page.goto("/")

    // Wait for sidebar to load
    await page.waitForSelector("text=Creator")

    // Take screenshot of sidebar with creator link
    await expect(
      page
        .locator('[data-testid="sidebar"]')
        .or(page.locator("aside"))
        .or(page.locator("nav")),
    ).toHaveScreenshot("sidebar-with-creator.png")
  })

  test("Templates Discovery Page", async ({ page }) => {
    // Navigate to templates page
    await page.goto("/templates")

    // Wait for the page to load
    await page.waitForSelector("text=Discover Trip Templates")

    // Take screenshot of the templates discovery page
    await expect(page).toHaveScreenshot("templates-discovery.png")
  })

  test("Templates Discovery - Search Functionality", async ({ page }) => {
    await page.goto("/templates")

    // Wait for search box and interact with it
    await page.waitForSelector('input[placeholder*="Search"]')
    await page.fill('input[placeholder*="Search"]', "Hawaii")

    // Wait a moment for any search results to load
    await page.waitForTimeout(1000)

    // Take screenshot of search results
    await expect(page).toHaveScreenshot("templates-search.png")
  })

  test("Creator Dashboard - Mobile View", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    await page.goto("/creator")
    await page.waitForSelector("text=Become a Creator")

    // Take screenshot of mobile creator setup
    await expect(page).toHaveScreenshot("creator-setup-mobile.png")
  })

  test("Templates Discovery - Mobile View", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    await page.goto("/templates")
    await page.waitForSelector("text=Discover Trip Templates")

    // Take screenshot of mobile templates page
    await expect(page).toHaveScreenshot("templates-discovery-mobile.png")
  })
})

test.describe("Creator Dashboard with Data", () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto("/login")
    await page.getByPlaceholder("Email").fill("admin@example.com")
    await page.getByPlaceholder("Password").fill("changethis")
    await page.getByRole("button", { name: "Log In" }).click()
    await page.waitForURL("/")
  })

  test("Creator Dashboard - Empty State", async ({ page }) => {
    await page.goto("/creator")

    // If creator profile exists but no templates
    const hasSetupButton = await page
      .locator("text=Set Up Creator Profile")
      .isVisible()
    const hasCreateButton = await page
      .locator("text=Create Your First Template")
      .isVisible()

    if (hasSetupButton) {
      await expect(page).toHaveScreenshot("creator-setup-state.png")
    } else if (hasCreateButton) {
      await expect(page).toHaveScreenshot("creator-empty-state.png")
    } else {
      // Take screenshot of actual dashboard
      await expect(page).toHaveScreenshot("creator-dashboard.png")
    }
  })

  test("Navigation Flow - Creator to Templates", async ({ page }) => {
    // Start from dashboard
    await page.goto("/")

    // Navigate to creator
    await page.click("text=Creator")
    await page.waitForURL("/creator")
    await page.waitForTimeout(1000)

    // Navigate to templates
    await page.click("text=Templates")
    await page.waitForURL("/templates")
    await page.waitForSelector("text=Discover Trip Templates")

    // Take screenshot of final state
    await expect(page).toHaveScreenshot("navigation-templates-final.png")
  })
})
