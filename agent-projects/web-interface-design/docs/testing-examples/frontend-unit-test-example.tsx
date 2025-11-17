/**
 * Frontend Unit Test Example
 * Demonstrates best practices for testing React components with Jest and React Testing Library.
 *
 * This example shows:
 * - Component rendering tests
 * - User interaction tests
 * - Async behavior tests
 * - Mocking API calls
 * - Accessibility testing
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StoryCard } from "@/components/StoryCard";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { Story } from "@/types/story";

// === MOCK DATA ===

const mockStory: Story = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  title: "Sample Horror Story",
  description:
    "A dark atmospheric horror adventure with minimal combat and heavy exploration",
  theme_id: "warhammer40k",
  is_sample: false,
  created_at: "2025-11-12T10:00:00Z",
  updated_at: "2025-11-12T10:00:00Z",
  current_version: 1,
  total_iterations: 0,
  play_count: 5,
  last_played: "2025-11-12T15:30:00Z",
  scene_count: 8,
  item_count: 12,
  npc_count: 3,
  puzzle_count: 2,
  tags: ["horror", "atmospheric", "combat-light"],
};

const mockIncompleteStory: Story = {
  ...mockStory,
  id: "660e8400-e29b-41d4-a716-446655440001",
  title: "Incomplete Story",
  status: "generating",
  scene_count: 0,
};

const mockStoryWithIterations: Story = {
  ...mockStory,
  id: "770e8400-e29b-41d4-a716-446655440002",
  title: "Story with Iterations",
  total_iterations: 3,
};

// === TEST HELPERS ===

/**
 * Render component with theme provider wrapper
 */
function renderWithTheme(component: React.ReactElement) {
  return render(<ThemeProvider>{component}</ThemeProvider>);
}

// === RENDERING TESTS ===

describe("StoryCard - Rendering", () => {
  it("renders story title and description", () => {
    /**
     * Test that basic story information is displayed.
     *
     * Steps:
     * 1. Render StoryCard with mock story
     * 2. Verify title displayed
     * 3. Verify description displayed
     */
    renderWithTheme(<StoryCard story={mockStory} />);

    expect(screen.getByText("Sample Horror Story")).toBeInTheDocument();
    expect(
      screen.getByText(/dark atmospheric horror adventure/i),
    ).toBeInTheDocument();
  });

  it("displays story statistics", () => {
    /**
     * Test that story statistics are rendered correctly.
     *
     * Expected:
     * - Scene count shown
     * - Play count shown
     * - Item/NPC counts shown
     */
    renderWithTheme(<StoryCard story={mockStory} />);

    expect(screen.getByText("8 scenes")).toBeInTheDocument();
    expect(screen.getByText(/played 5 times/i)).toBeInTheDocument();
    expect(screen.getByText("12 items")).toBeInTheDocument();
    expect(screen.getByText("3 NPCs")).toBeInTheDocument();
  });

  it("shows theme badge with correct styling", () => {
    /**
     * Test that theme badge is displayed and styled.
     */
    renderWithTheme(<StoryCard story={mockStory} />);

    const themeBadge = screen.getByText("warhammer40k");
    expect(themeBadge).toBeInTheDocument();
    expect(themeBadge).toHaveClass("theme-badge");
  });

  it("displays tags as badges", () => {
    /**
     * Test that story tags are rendered as individual badges.
     */
    renderWithTheme(<StoryCard story={mockStory} />);

    expect(screen.getByText("horror")).toBeInTheDocument();
    expect(screen.getByText("atmospheric")).toBeInTheDocument();
    expect(screen.getByText("combat-light")).toBeInTheDocument();
  });

  it("shows play button for complete stories", () => {
    /**
     * Test that play button is visible for complete stories.
     */
    renderWithTheme(<StoryCard story={mockStory} />);

    const playButton = screen.getByRole("button", { name: /play/i });
    expect(playButton).toBeInTheDocument();
    expect(playButton).not.toBeDisabled();
  });

  it("disables play button for incomplete stories", () => {
    /**
     * Test that play button is disabled during generation.
     *
     * Expected:
     * - Play button present but disabled
     * - Generating status indicator shown
     */
    renderWithTheme(<StoryCard story={mockIncompleteStory} />);

    const playButton = screen.getByRole("button", { name: /play/i });
    expect(playButton).toBeDisabled();
    expect(screen.getByText(/generating/i)).toBeInTheDocument();
  });

  it("shows iteration button with count when iterations exist", () => {
    /**
     * Test that iteration button shows count correctly.
     */
    renderWithTheme(<StoryCard story={mockStoryWithIterations} />);

    expect(screen.getByText("3 iterations")).toBeInTheDocument();
    const iterateButton = screen.getByRole("button", { name: /iterate/i });
    expect(iterateButton).toBeInTheDocument();
  });

  it("hides iteration button when no iterations", () => {
    /**
     * Test that iteration button is hidden for first version.
     */
    renderWithTheme(<StoryCard story={mockStory} />);

    expect(screen.queryByText(/iterations/i)).not.toBeInTheDocument();
  });

  it("displays created date in human-readable format", () => {
    /**
     * Test that date is formatted correctly (e.g., "2 days ago").
     */
    renderWithTheme(<StoryCard story={mockStory} />);

    // Assuming date formatting utility is used
    expect(screen.getByText(/created/i)).toBeInTheDocument();
  });
});

// === USER INTERACTION TESTS ===

describe("StoryCard - User Interactions", () => {
  it("calls onPlay when play button clicked", () => {
    /**
     * Test play button callback.
     *
     * Steps:
     * 1. Render with onPlay mock
     * 2. Click play button
     * 3. Verify onPlay called with story ID
     */
    const onPlay = jest.fn();
    renderWithTheme(<StoryCard story={mockStory} onPlay={onPlay} />);

    const playButton = screen.getByRole("button", { name: /play/i });
    fireEvent.click(playButton);

    expect(onPlay).toHaveBeenCalledTimes(1);
    expect(onPlay).toHaveBeenCalledWith(mockStory.id);
  });

  it("calls onIterate when iterate button clicked", () => {
    /**
     * Test iterate button callback.
     */
    const onIterate = jest.fn();
    renderWithTheme(
      <StoryCard story={mockStoryWithIterations} onIterate={onIterate} />,
    );

    const iterateButton = screen.getByRole("button", { name: /iterate/i });
    fireEvent.click(iterateButton);

    expect(onIterate).toHaveBeenCalledTimes(1);
    expect(onIterate).toHaveBeenCalledWith(mockStoryWithIterations.id);
  });

  it("calls onDelete when delete button clicked", async () => {
    /**
     * Test delete confirmation flow.
     *
     * Steps:
     * 1. Click delete button
     * 2. Verify confirmation modal appears
     * 3. Confirm deletion
     * 4. Verify onDelete called
     */
    const onDelete = jest.fn();
    renderWithTheme(<StoryCard story={mockStory} onDelete={onDelete} />);

    // Click delete button (may be in dropdown menu)
    const deleteButton = screen.getByRole("button", { name: /delete/i });
    fireEvent.click(deleteButton);

    // Wait for confirmation modal
    await waitFor(() => {
      expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
    });

    // Confirm deletion
    const confirmButton = screen.getByRole("button", { name: /confirm/i });
    fireEvent.click(confirmButton);

    expect(onDelete).toHaveBeenCalledWith(mockStory.id);
  });

  it('expands description when "Read More" clicked', async () => {
    /**
     * Test expandable description for long text.
     *
     * Steps:
     * 1. Render with long description (truncated)
     * 2. Click "Read More"
     * 3. Verify full description shown
     */
    const longDescriptionStory: Story = {
      ...mockStory,
      description: "A".repeat(300), // Long description
    };

    renderWithTheme(<StoryCard story={longDescriptionStory} />);

    // Initially truncated
    expect(screen.getByText(/read more/i)).toBeInTheDocument();

    // Click to expand
    const readMoreButton = screen.getByText(/read more/i);
    fireEvent.click(readMoreButton);

    // Full text should be visible
    await waitFor(() => {
      expect(screen.getByText(/read less/i)).toBeInTheDocument();
    });
  });

  it("navigates to story details on card click", () => {
    /**
     * Test that clicking card navigates to detail view.
     */
    const mockNavigate = jest.fn();
    // Mock useNavigate hook
    jest.mock("react-router-dom", () => ({
      ...jest.requireActual("react-router-dom"),
      useNavigate: () => mockNavigate,
    }));

    renderWithTheme(<StoryCard story={mockStory} />);

    const card = screen.getByTestId("story-card");
    fireEvent.click(card);

    expect(mockNavigate).toHaveBeenCalledWith(`/stories/${mockStory.id}`);
  });
});

// === ASYNC BEHAVIOR TESTS ===

describe("StoryCard - Async Operations", () => {
  it("shows loading state during play initialization", async () => {
    /**
     * Test loading indicator while starting game.
     *
     * Steps:
     * 1. Click play button
     * 2. Verify loading indicator shown
     * 3. Wait for completion
     * 4. Verify navigation
     */
    const onPlay = jest.fn(
      () => new Promise((resolve) => setTimeout(resolve, 100)),
    );
    renderWithTheme(<StoryCard story={mockStory} onPlay={onPlay} />);

    const playButton = screen.getByRole("button", { name: /play/i });
    fireEvent.click(playButton);

    // Loading state should appear
    expect(screen.getByTestId("loading-spinner")).toBeInTheDocument();

    // Wait for completion
    await waitFor(() => {
      expect(screen.queryByTestId("loading-spinner")).not.toBeInTheDocument();
    });
  });

  it("displays error message on play failure", async () => {
    /**
     * Test error handling when play action fails.
     *
     * Expected:
     * - Error message displayed
     * - User can dismiss error
     * - Play button re-enabled
     */
    const onPlay = jest.fn(() =>
      Promise.reject(new Error("Failed to start game")),
    );
    renderWithTheme(<StoryCard story={mockStory} onPlay={onPlay} />);

    const playButton = screen.getByRole("button", { name: /play/i });
    fireEvent.click(playButton);

    // Error should appear
    await waitFor(() => {
      expect(screen.getByText(/failed to start game/i)).toBeInTheDocument();
    });

    // Error should be dismissable
    const closeButton = screen.getByRole("button", { name: /close/i });
    fireEvent.click(closeButton);

    expect(screen.queryByText(/failed to start game/i)).not.toBeInTheDocument();
  });
});

// === CONDITIONAL RENDERING TESTS ===

describe("StoryCard - Conditional Rendering", () => {
  it("shows sample badge for sample stories", () => {
    /**
     * Test that sample stories are marked appropriately.
     */
    const sampleStory: Story = { ...mockStory, is_sample: true };
    renderWithTheme(<StoryCard story={sampleStory} />);

    expect(screen.getByText(/sample/i)).toBeInTheDocument();
  });

  it("hides delete button for sample stories", () => {
    /**
     * Test that sample stories cannot be deleted.
     */
    const sampleStory: Story = { ...mockStory, is_sample: true };
    renderWithTheme(<StoryCard story={sampleStory} />);

    expect(
      screen.queryByRole("button", { name: /delete/i }),
    ).not.toBeInTheDocument();
  });

  it('shows "Never played" when play_count is 0', () => {
    /**
     * Test display for unplayed stories.
     */
    const unplayedStory: Story = { ...mockStory, play_count: 0 };
    renderWithTheme(<StoryCard story={unplayedStory} />);

    expect(screen.getByText(/never played/i)).toBeInTheDocument();
  });

  it("shows iteration limit warning at 5 iterations", () => {
    /**
     * Test that max iteration warning is displayed.
     */
    const maxIterationStory: Story = {
      ...mockStory,
      total_iterations: 5,
    };
    renderWithTheme(<StoryCard story={maxIterationStory} />);

    expect(screen.getByText(/maximum iterations reached/i)).toBeInTheDocument();
    const iterateButton = screen.getByRole("button", { name: /iterate/i });
    expect(iterateButton).toBeDisabled();
  });
});

// === ACCESSIBILITY TESTS ===

describe("StoryCard - Accessibility", () => {
  it("has accessible name for play button", () => {
    /**
     * Test that buttons have proper ARIA labels.
     */
    renderWithTheme(<StoryCard story={mockStory} />);

    const playButton = screen.getByRole("button", {
      name: /play.*sample horror story/i,
    });
    expect(playButton).toBeInTheDocument();
  });

  it("supports keyboard navigation", async () => {
    /**
     * Test that card is keyboard accessible.
     *
     * Steps:
     * 1. Tab to play button
     * 2. Press Enter
     * 3. Verify action triggered
     */
    const user = userEvent.setup();
    const onPlay = jest.fn();
    renderWithTheme(<StoryCard story={mockStory} onPlay={onPlay} />);

    // Tab to play button
    await user.tab();
    const playButton = screen.getByRole("button", { name: /play/i });
    expect(playButton).toHaveFocus();

    // Press Enter
    await user.keyboard("{Enter}");
    expect(onPlay).toHaveBeenCalled();
  });

  it("has proper semantic HTML structure", () => {
    /**
     * Test that card uses semantic HTML elements.
     */
    const { container } = renderWithTheme(<StoryCard story={mockStory} />);

    const article = container.querySelector("article");
    expect(article).toBeInTheDocument();

    const heading = screen.getByRole("heading", {
      name: "Sample Horror Story",
    });
    expect(heading).toBeInTheDocument();
  });

  it("has sufficient color contrast", () => {
    /**
     * Test that text has adequate contrast (manual check or axe-core).
     */
    const { container } = renderWithTheme(<StoryCard story={mockStory} />);

    // This would use axe-core in real tests
    // import { axe } from 'jest-axe';
    // const results = await axe(container);
    // expect(results).toHaveNoViolations();

    // For this example, just verify contrast class applied
    const card = screen.getByTestId("story-card");
    expect(card).toHaveClass("high-contrast");
  });

  it("announces status changes to screen readers", async () => {
    /**
     * Test that dynamic status updates are announced.
     */
    const { rerender } = renderWithTheme(
      <StoryCard story={mockIncompleteStory} />,
    );

    // Initially generating
    expect(screen.getByText(/generating/i)).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent(/generating/i);

    // Update to complete
    const completeStory: Story = { ...mockIncompleteStory, status: "complete" };
    rerender(
      <ThemeProvider>
        <StoryCard story={completeStory} />
      </ThemeProvider>,
    );

    // Status should be announced
    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(/complete/i);
    });
  });
});

// === SNAPSHOT TESTS ===

describe("StoryCard - Snapshots", () => {
  it("matches snapshot for complete story", () => {
    /**
     * Test that component structure remains consistent.
     */
    const { container } = renderWithTheme(<StoryCard story={mockStory} />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it("matches snapshot for generating story", () => {
    const { container } = renderWithTheme(
      <StoryCard story={mockIncompleteStory} />,
    );
    expect(container.firstChild).toMatchSnapshot();
  });

  it("matches snapshot for story with iterations", () => {
    const { container } = renderWithTheme(
      <StoryCard story={mockStoryWithIterations} />,
    );
    expect(container.firstChild).toMatchSnapshot();
  });
});

// === INTEGRATION TESTS (Component + Context) ===

describe("StoryCard - Integration with ThemeContext", () => {
  it("applies theme styling when theme changes", async () => {
    /**
     * Test that card responds to theme changes.
     *
     * Steps:
     * 1. Render with default theme
     * 2. Change theme
     * 3. Verify styling updated
     */
    const { container } = renderWithTheme(<StoryCard story={mockStory} />);

    // Initial theme (warhammer40k)
    const card = screen.getByTestId("story-card");
    expect(card).toHaveStyle({ backgroundColor: "var(--color-bg-primary)" });

    // Change theme (simulate via context)
    // This would require ThemeContext mock or test utility
    // For brevity, verifying CSS variable is applied

    const computedStyle = window.getComputedStyle(card);
    expect(computedStyle.getPropertyValue("--color-bg-primary")).toBeTruthy();
  });
});

// === PERFORMANCE TESTS ===

describe("StoryCard - Performance", () => {
  it("renders efficiently with many cards", () => {
    /**
     * Test that multiple cards render without performance issues.
     */
    const stories = Array.from({ length: 100 }, (_, i) => ({
      ...mockStory,
      id: `story-${i}`,
      title: `Story ${i}`,
    }));

    const start = performance.now();
    renderWithTheme(
      <>
        {stories.map((story) => (
          <StoryCard key={story.id} story={story} />
        ))}
      </>,
    );
    const duration = performance.now() - start;

    // Should render in reasonable time (<1 second for 100 cards)
    expect(duration).toBeLessThan(1000);
  });

  it("memoizes and avoids unnecessary re-renders", () => {
    /**
     * Test that component uses React.memo or similar optimization.
     */
    const { rerender } = renderWithTheme(<StoryCard story={mockStory} />);

    // Re-render with same props
    rerender(
      <ThemeProvider>
        <StoryCard story={mockStory} />
      </ThemeProvider>,
    );

    // Component should not re-render if props haven't changed
    // This would use React DevTools Profiler API in real tests
  });
});

export {};
