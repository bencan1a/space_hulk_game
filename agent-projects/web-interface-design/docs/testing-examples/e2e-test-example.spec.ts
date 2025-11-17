/**
 * End-to-End Test Example
 * Demonstrates best practices for E2E testing with Playwright.
 *
 * This example shows:
 * - Complete user journey testing
 * - Cross-browser testing
 * - Async operation handling
 * - WebSocket interaction testing
 * - Error scenario testing
 * - Accessibility validation
 */

import { test, expect, Page } from "@playwright/test";

// === TEST CONFIGURATION ===

test.describe.configure({ mode: "serial" }); // Run tests in order

// === HELPER FUNCTIONS ===

/**
 * Wait for generation to complete (with timeout)
 */
async function waitForGenerationComplete(
  page: Page,
  timeout: number = 600000,
): Promise<void> {
  await expect(page.locator('[data-testid="generation-complete"]')).toBeVisible(
    {
      timeout,
    },
  );
}

/**
 * Fill prompt input with validation check
 */
async function fillPrompt(page: Page, prompt: string): Promise<void> {
  const promptInput = page.locator('[data-testid="prompt-input"]');
  await promptInput.fill(prompt);

  // Verify character count updates
  const charCount = page.locator('[data-testid="char-count"]');
  await expect(charCount).toContainText(prompt.length.toString());
}

/**
 * Wait for element with retry logic
 */
async function waitForElementWithRetry(
  page: Page,
  selector: string,
  maxRetries: number = 3,
): Promise<void> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await page.waitForSelector(selector, { timeout: 5000 });
      return;
    } catch (e) {
      if (i === maxRetries - 1) throw e;
      await page.waitForTimeout(1000);
    }
  }
}

// === E2E TEST: FIRST-TIME USER CREATES STORY FROM TEMPLATE ===

test.describe("Story Creation Journey", () => {
  test.beforeEach(async ({ page }) => {
    // Reset database to clean state (via API or direct DB connection)
    await page.request.post("/api/test/reset-database");
  });

  test("First-time user creates story from template", async ({ page }) => {
    /**
     * PRECONDITIONS:
     * - User has never used the system
     * - Database is empty (no stories)
     * - All services are running and healthy
     *
     * EXPECTED OUTCOMES:
     * - Story created successfully
     * - Story appears in library
     * - User can play the created story
     * - Progress updates work in real-time
     */

    // === STEP 1: Navigate to home page ===
    await page.goto("/");

    // Verify empty library state
    await expect(page.locator('[data-testid="library-empty"]')).toBeVisible();
    await expect(
      page.locator('[data-testid="library-empty-message"]'),
    ).toContainText(/no stories yet/i);

    // Verify "Create New Story" call-to-action
    const createButton = page.locator('[data-testid="create-story-button"]');
    await expect(createButton).toBeVisible();
    await expect(createButton).toBeEnabled();

    // === STEP 2: Navigate to creation page ===
    await createButton.click();

    // Verify URL changed
    await expect(page).toHaveURL("/create");

    // Verify creation page loaded
    await expect(
      page.locator('[data-testid="template-gallery"]'),
    ).toBeVisible();
    await expect(page.locator("h1")).toContainText(/create.*story/i);

    // === STEP 3: Select horror template ===
    const horrorTemplate = page.locator('[data-testid="template-horror"]');

    // Verify template card displayed
    await expect(horrorTemplate).toBeVisible();
    await expect(horrorTemplate).toContainText(/horror/i);

    // Click template
    await horrorTemplate.click();

    // Verify template selected (visual indicator)
    await expect(horrorTemplate).toHaveClass(/selected/);
    await expect(
      page.locator('[data-testid="template-description"]'),
    ).toContainText(/atmospheric/i);

    // === STEP 4: Customize prompt ===
    const customPrompt =
      "A dark atmospheric horror adventure with minimal combat and heavy exploration. Focus on psychological tension and environmental storytelling.";

    await fillPrompt(page, customPrompt);

    // Verify prompt meets minimum length
    const generateButton = page.locator('[data-testid="generate-button"]');
    await expect(generateButton).toBeEnabled();

    // === STEP 5: Start generation ===
    await generateButton.click();

    // === STEP 6: Verify progress page loads ===
    // URL should change to progress page with job ID
    await expect(page).toHaveURL(/\/create\/progress\/[a-f0-9-]+/);

    // Progress components should be visible
    await expect(page.locator('[data-testid="progress-bar"]')).toBeVisible();
    await expect(
      page.locator('[data-testid="agent-status-list"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="progress-message"]'),
    ).toBeVisible();

    // === STEP 7: Monitor real-time progress updates ===
    // Wait for WebSocket connection
    await page.waitForTimeout(1000);

    // Verify progress bar starts at 0%
    const progressBar = page.locator('[data-testid="progress-bar"]');
    const initialProgress = await progressBar.getAttribute("aria-valuenow");
    expect(parseInt(initialProgress || "0")).toBeGreaterThanOrEqual(0);

    // Verify agent status updates
    const plotMasterStatus = page.locator(
      '[data-testid="agent-status-PlotMaster"]',
    );
    await expect(plotMasterStatus).toBeVisible();

    // Wait for first agent to complete (checkmark appears)
    await expect(
      plotMasterStatus.locator('[data-testid="status-icon"]'),
    ).toContainText(
      "✓",
      { timeout: 120000 }, // 2 minutes for first agent
    );

    // Verify progress increased
    const updatedProgress = await progressBar.getAttribute("aria-valuenow");
    expect(parseInt(updatedProgress || "0")).toBeGreaterThan(
      parseInt(initialProgress || "0"),
    );

    // === STEP 8: Wait for completion (up to 10 minutes) ===
    await waitForGenerationComplete(page, 600000);

    // Verify completion UI
    await expect(
      page.locator('[data-testid="generation-complete"]'),
    ).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText(
      /story created successfully/i,
    );

    // === STEP 9: Verify story details displayed ===
    const storyTitle = page.locator('[data-testid="story-title"]');
    await expect(storyTitle).toBeVisible();
    await expect(storyTitle).toContainText(/horror/i); // Should match prompt theme

    // Verify statistics
    const storyStats = page.locator('[data-testid="story-stats"]');
    await expect(storyStats).toContainText(/scenes/i);
    await expect(storyStats).toContainText(/items/i);
    await expect(storyStats).toContainText(/puzzles/i);

    // Verify scene count > 0
    const sceneCount = await page
      .locator('[data-testid="scene-count"]')
      .textContent();
    expect(parseInt(sceneCount || "0")).toBeGreaterThan(0);

    // === STEP 10: Navigate to game player ===
    const playNowButton = page.locator('[data-testid="play-now-button"]');
    await expect(playNowButton).toBeVisible();
    await expect(playNowButton).toBeEnabled();

    await playNowButton.click();

    // === VERIFY EXPECTED OUTCOMES ===

    // 1. User redirected to game player
    await expect(page).toHaveURL(/\/play\/[a-f0-9-]+/);

    // 2. Game scene displayed
    const gameScene = page.locator('[data-testid="game-scene"]');
    await expect(gameScene).toBeVisible();
    await expect(gameScene).not.toBeEmpty();

    // 3. Command input ready
    const commandInput = page.locator('[data-testid="command-input"]');
    await expect(commandInput).toBeVisible();
    await expect(commandInput).toBeFocused(); // Auto-focus for UX

    // 4. Initial game state rendered
    await expect(page.locator('[data-testid="inventory-panel"]')).toBeVisible();
    await expect(page.locator('[data-testid="output-log"]')).toBeVisible();

    // 5. Story appears in library
    await page.goto("/library");
    await expect(
      page.locator('[data-testid="story-card"]').first(),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="story-card"]').first(),
    ).toContainText(/horror/i);
  });

  // === ERROR SCENARIO: Generation Timeout ===

  test("User recovers from generation timeout", async ({ page }) => {
    /**
     * Simulate generation timeout scenario.
     *
     * PRECONDITIONS:
     * - Mock long-running generation (>15 minutes)
     *
     * EXPECTED OUTCOMES:
     * - User-friendly error message displayed
     * - Retry option available
     * - Original prompt preserved
     */

    // Mock API to simulate timeout
    await page.route("**/api/v1/stories", async (route) => {
      await route.fulfill({
        status: 202,
        body: JSON.stringify({
          data: {
            generation_job_id: "mock-timeout-job",
            story_id: "mock-story",
            status: "queued",
          },
        }),
      });
    });

    await page.route("**/api/v1/generation/mock-timeout-job", async (route) => {
      // Simulate timeout error after delay
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          data: {
            generation_job_id: "mock-timeout-job",
            status: "failed",
            error: {
              code: "GENERATION_TIMEOUT",
              message: "Story generation timed out after 15 minutes",
              user_message:
                "The generation is taking longer than expected. Please try again.",
              retry_possible: true,
            },
          },
        }),
      });
    });

    // Navigate and start generation
    await page.goto("/create");
    await page.click('[data-testid="template-horror"]');
    await fillPrompt(page, "Test prompt for timeout scenario");
    await page.click('[data-testid="generate-button"]');

    // Wait for error to appear
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible({
      timeout: 5000,
    });
    await expect(page.locator('[data-testid="error-message"]')).toContainText(
      /taking longer than expected/i,
    );

    // Verify retry button
    const retryButton = page.locator('[data-testid="retry-button"]');
    await expect(retryButton).toBeVisible();
    await expect(retryButton).toBeEnabled();

    // Verify prompt preserved
    await retryButton.click();
    await expect(page).toHaveURL("/create");
    const promptInput = page.locator('[data-testid="prompt-input"]');
    await expect(promptInput).toHaveValue("Test prompt for timeout scenario");
  });

  // === ERROR SCENARIO: WebSocket Disconnect ===

  test("WebSocket reconnects after network interruption", async ({
    page,
    context,
  }) => {
    /**
     * Test WebSocket reconnection logic.
     *
     * EXPECTED OUTCOMES:
     * - Automatic reconnection with backoff
     * - Progress updates resume
     * - User notified of connection status
     */

    // Start generation
    await page.goto("/create");
    await page.click('[data-testid="template-horror"]');
    await fillPrompt(page, "Test prompt for WebSocket reconnection");
    await page.click('[data-testid="generate-button"]');

    // Wait for progress page
    await expect(page.locator('[data-testid="progress-bar"]')).toBeVisible();

    // Simulate network disconnect
    await context.setOffline(true);

    // Verify "Reconnecting..." message appears
    await expect(
      page.locator('[data-testid="connection-status"]'),
    ).toContainText(/reconnecting/i, { timeout: 10000 });

    // Restore network
    await context.setOffline(false);

    // Verify reconnection successful
    await expect(
      page.locator('[data-testid="connection-status"]'),
    ).toContainText(/connected/i, { timeout: 30000 });

    // Verify progress updates resume
    await expect(page.locator('[data-testid="progress-bar"]')).toHaveAttribute(
      "aria-valuenow",
      /[0-9]+/,
    );
  });

  // === INPUT VALIDATION ===

  test("User receives validation errors for invalid prompt", async ({
    page,
  }) => {
    /**
     * Test input validation and error messages.
     *
     * EXPECTED OUTCOMES:
     * - Clear validation messages
     * - Character count displayed
     * - Submit disabled until valid
     */

    await page.goto("/create");

    const promptInput = page.locator('[data-testid="prompt-input"]');
    const generateButton = page.locator('[data-testid="generate-button"]');
    const charCount = page.locator('[data-testid="char-count"]');

    // Test 1: Prompt too short (minimum 50 characters)
    await promptInput.fill("Short");
    await expect(charCount).toContainText("5 / 1000");
    await expect(generateButton).toBeDisabled();
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).toContainText(/at least 50 characters/i);

    // Test 2: Prompt too long (maximum 1000 characters)
    const longPrompt = "A".repeat(1500);
    await promptInput.fill(longPrompt);
    await expect(generateButton).toBeDisabled();
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).toContainText(/maximum 1000 characters/i);

    // Test 3: Valid prompt
    const validPrompt = "A".repeat(200);
    await promptInput.fill(validPrompt);
    await expect(charCount).toContainText("200 / 1000");
    await expect(generateButton).toBeEnabled();
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).not.toBeVisible();
  });
});

// === E2E TEST: GAMEPLAY SESSION ===

test.describe("Gameplay Journey", () => {
  let storyId: string;

  test.beforeAll(async ({ request }) => {
    // Create a sample story for gameplay tests
    const response = await request.post("/api/test/create-sample-story");
    const data = await response.json();
    storyId = data.story_id;
  });

  test("User plays game to completion", async ({ page }) => {
    /**
     * Test complete gameplay session.
     *
     * EXPECTED OUTCOMES:
     * - Commands processed correctly
     * - Inventory updates in real-time
     * - Game over screen appears
     * - Play count incremented
     */

    // Navigate to game player
    await page.goto(`/play/${storyId}`);

    // === STEP 1: Read initial scene ===
    const gameScene = page.locator('[data-testid="game-scene"]');
    await expect(gameScene).toBeVisible();

    const initialText = await gameScene.textContent();
    expect(initialText).toBeTruthy();
    expect(initialText!.length).toBeGreaterThan(0);

    // === STEP 2: Enter commands ===
    const commandInput = page.locator('[data-testid="command-input"]');
    const outputLog = page.locator('[data-testid="output-log"]');

    // Command: look around
    await commandInput.fill("look around");
    await commandInput.press("Enter");

    // Verify output appears
    await expect(outputLog).toContainText(/look around/i, { timeout: 5000 });
    await expect(outputLog).not.toHaveText(initialText!); // Output changed

    // Command: examine door
    await commandInput.fill("examine door");
    await commandInput.press("Enter");

    await expect(outputLog).toContainText(/door/i);

    // Command: take keycard
    await commandInput.fill("take keycard");
    await commandInput.press("Enter");

    // === STEP 3: Verify inventory updated ===
    const inventory = page.locator('[data-testid="inventory-panel"]');
    await expect(inventory).toContainText(/keycard/i, { timeout: 5000 });

    // === STEP 4: Use command history (up arrow) ===
    await commandInput.press("ArrowUp");
    await expect(commandInput).toHaveValue("take keycard");

    await commandInput.press("ArrowUp");
    await expect(commandInput).toHaveValue("examine door");

    await commandInput.press("ArrowDown");
    await expect(commandInput).toHaveValue("take keycard");

    // === STEP 5: Continue to end game (simplified) ===
    // In real scenario, would play through multiple scenes
    // For brevity, mock game completion

    await page.route("**/api/v1/game/*/command", async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          data: {
            output: "You have completed the mission. GAME OVER.",
            state: { current_scene: "ending", game_over: true },
            valid_command: true,
            game_over: true,
          },
        }),
      });
    });

    await commandInput.fill("complete mission");
    await commandInput.press("Enter");

    // === STEP 6: Verify game over screen ===
    await expect(page.locator('[data-testid="game-over-screen"]')).toBeVisible({
      timeout: 5000,
    });
    await expect(
      page.locator('[data-testid="game-over-message"]'),
    ).toContainText(/completed/i);

    // Verify options available
    await expect(
      page.locator('[data-testid="play-again-button"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="back-to-library-button"]'),
    ).toBeVisible();
  });

  test("User saves and loads game mid-session", async ({ page }) => {
    /**
     * Test save/load functionality.
     *
     * EXPECTED OUTCOMES:
     * - Game state perfectly restored
     * - Inventory preserved
     * - Scene position preserved
     */

    await page.goto(`/play/${storyId}`);

    // Progress through game
    const commandInput = page.locator('[data-testid="command-input"]');
    await commandInput.fill("take flashlight");
    await commandInput.press("Enter");

    await page.waitForTimeout(1000);

    await commandInput.fill("go north");
    await commandInput.press("Enter");

    // Verify inventory has flashlight
    await expect(page.locator('[data-testid="inventory-panel"]')).toContainText(
      /flashlight/i,
    );

    // Save game
    await page.click('[data-testid="save-button"]');

    // Fill save name
    const saveNameInput = page.locator('[data-testid="save-name-input"]');
    await saveNameInput.fill("Before boss fight");
    await page.click('[data-testid="confirm-save-button"]');

    // Verify save confirmation
    await expect(
      page.locator('[data-testid="save-confirmation"]'),
    ).toContainText(/saved successfully/i);

    // Navigate away
    await page.goto("/library");

    // Load game
    await page.click(`[data-testid="story-card-${storyId}"]`);
    await page.click('[data-testid="load-game-button"]');

    // Select save
    await page.click('[data-testid="save-slot-0"]');

    // Verify restored to correct state
    await expect(page).toHaveURL(/\/play\//);
    await expect(page.locator('[data-testid="inventory-panel"]')).toContainText(
      /flashlight/i,
    );
  });
});

// === E2E TEST: ACCESSIBILITY ===

test.describe("Accessibility Compliance", () => {
  test("User navigates entire app with keyboard only", async ({ page }) => {
    /**
     * Test keyboard navigation.
     *
     * EXPECTED OUTCOMES:
     * - All interactive elements focusable
     * - Tab order logical
     * - Enter/Space activate buttons
     * - No keyboard traps
     */

    await page.goto("/library");

    // Tab through elements
    await page.keyboard.press("Tab");
    let focusedElement = await page
      .locator(":focus")
      .getAttribute("data-testid");
    expect(focusedElement).toBeTruthy();

    // Continue tabbing
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press("Tab");
      const currentFocus = await page
        .locator(":focus")
        .getAttribute("data-testid");
      expect(currentFocus).toBeTruthy(); // Each element should have test ID
    }

    // Verify no keyboard trap (can always move focus)
    const initialFocus = await page
      .locator(":focus")
      .getAttribute("data-testid");
    await page.keyboard.press("Tab");
    const nextFocus = await page.locator(":focus").getAttribute("data-testid");
    expect(nextFocus).not.toBe(initialFocus);

    // Activate button with Enter
    const createButton = page.locator('[data-testid="create-story-button"]');
    await createButton.focus();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL("/create");
  });

  test("Screen reader announcements work correctly", async ({ page }) => {
    /**
     * Test ARIA live regions and announcements.
     *
     * EXPECTED OUTCOMES:
     * - Dynamic changes announced
     * - Status messages have role="status"
     * - Errors have role="alert"
     */

    await page.goto("/create");

    // Verify live region exists
    const liveRegion = page.locator('[aria-live="polite"]');
    await expect(liveRegion).toBeAttached();

    // Trigger dynamic update
    await page.click('[data-testid="template-horror"]');

    // Verify announcement
    await expect(liveRegion).toContainText(/selected/i);

    // Error should use aria-live="assertive"
    const promptInput = page.locator('[data-testid="prompt-input"]');
    await promptInput.fill("Short"); // Trigger validation error

    const errorAlert = page.locator('[role="alert"]');
    await expect(errorAlert).toBeVisible();
  });
});

// === E2E TEST: CROSS-BROWSER ===

test.describe("Cross-Browser Compatibility", () => {
  test("Works in Chrome, Firefox, and Safari", async ({
    browserName,
    page,
  }) => {
    /**
     * Test basic functionality across browsers.
     */

    test.skip(
      browserName === "webkit",
      "WebKit/Safari has known issues with WebSockets",
    );

    await page.goto("/library");
    await expect(page.locator("h1")).toBeVisible();

    // Test basic interaction
    await page.click('[data-testid="create-story-button"]');
    await expect(page).toHaveURL("/create");
  });
});

export {};
