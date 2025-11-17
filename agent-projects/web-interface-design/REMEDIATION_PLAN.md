# Phase 2 Remediation Plan

## ✅ STATUS: COMPLETED

All remediation tasks have been successfully completed. See commit history:

- **Commit ed6bdf7**: Fixed navigation and auto-fetch issues
- **Verified**: Theme system already had CSS variable injection implemented

**Summary**:

- ✅ Priority 1 (Navigation): Fixed in LibraryPage.tsx
- ✅ Priority 2 (Theme System): Verified already implemented in ThemeContext.tsx
- ✅ Priority 3 (HomePage): Implemented redirect to library
- ✅ All acceptance criteria met
- ✅ All tests passing (138/138)

---

## Overview

This document outlines the plan to address the gaps identified in the Phase 2 Gap Analysis and bring Phase 2 to 100% completion.

---

## Priority 1: Fix Navigation (CRITICAL)

### Issue

LibraryPage has commented-out navigation code, preventing users from navigating to play and create pages.

### Changes Required

#### File: `frontend/src/pages/LibraryPage.tsx`

**Change 1: Import useNavigate**

```typescript
// Add import at top of file
import { useNavigate } from "react-router-dom";
```

**Change 2: Initialize navigate hook**

```typescript
// Inside LibraryPage component, after other hooks
const navigate = useNavigate();
```

**Change 3: Implement handleStoryClick**

```typescript
// Replace lines 30-36
const handleStoryClick = (story: Story) => {
  navigate(`/play/${story.id}`);
};
```

**Change 4: Implement handleCreateStory**

```typescript
// Replace lines 38-44
const handleCreateStory = () => {
  navigate("/create");
};
```

**Change 5: Add useEffect for auto-fetch**

```typescript
// Add after state declarations
useEffect(() => {
  fetchStories();
}, [fetchStories]);
```

### Testing

1. Run frontend tests to ensure no regressions
2. Manually test navigation:
   - Click story card → should navigate to `/play/{id}`
   - Click "Create New Story" → should navigate to `/create`

### Estimated Time: 30 minutes

---

## Priority 2: Verify Theme System

### Issue

Need to verify that CSS variables are properly injected when theme changes.

### Investigation Steps

1. Check `frontend/src/contexts/ThemeContext.tsx` for CSS variable injection
2. Test theme switching in browser dev tools
3. Verify CSS variables in document root

### If Not Implemented

#### File: `frontend/src/contexts/ThemeContext.tsx`

**Add CSS variable injection function**:

```typescript
const applyThemeVariables = (theme: ThemeConfig) => {
  const root = document.documentElement;

  // Apply color variables
  Object.entries(theme.colors).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key}`, value);
  });

  // Apply typography variables
  if (theme.typography?.fontFamily) {
    root.style.setProperty("--font-family", theme.typography.fontFamily);
  }
  if (theme.typography?.fontFamilyMono) {
    root.style.setProperty(
      "--font-family-mono",
      theme.typography.fontFamilyMono,
    );
  }
};
```

**Call in setTheme**:

```typescript
const setTheme = async (themeId: string) => {
  // ... existing code ...
  applyThemeVariables(themeConfig);
  // ... existing code ...
};
```

### Testing

1. Open browser dev tools
2. Switch theme
3. Inspect `:root` element → verify CSS variables updated
4. Verify visual changes

### Estimated Time: 1 hour

---

## Priority 3: Improve HomePage (OPTIONAL)

### Issue

HomePage is a minimal stub that doesn't guide users.

### Recommendation: Redirect to Library

This is the simplest approach and aligns with user journey expectations.

#### File: `frontend/src/pages/HomePage.tsx`

**Replace entire file**:

```typescript
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function HomePage() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/library");
  }, [navigate]);

  return null;
}

export default HomePage;
```

### Alternative: Rich Landing Page

If product owner wants a landing page:

- Add hero section with CTA buttons
- Show featured sample stories
- Display "Getting Started" guide

### Estimated Time: 15 minutes (redirect) or 4 hours (rich landing)

---

## Acceptance Criteria

Phase 2 will be considered 100% complete when:

- [x] All backend tests pass (88/88) ✅ Verified passing
- [x] All frontend tests pass (50/50) ✅ Verified passing
- [x] Navigation works from library to play page ✅ Implemented
- [x] Navigation works from library to create page ✅ Implemented
- [x] Stories auto-fetch on library page load ✅ Implemented
- [x] Theme switching visually updates the UI ✅ Already implemented
- [x] No console errors in browser ✅ Verified
- [x] User Journey 2 (Library browsing) works end-to-end ✅ Verified

---

## Implementation Order

1. **Fix Navigation** (30 min)
   - Highest impact
   - Unblocks user testing

2. **Verify/Fix Theme System** (1 hour)
   - Important for visual experience
   - May already be working

3. **Decide on HomePage** (TBD)
   - Can defer to Phase 3
   - Low priority for MVP

---

## Testing Checklist

### Manual Testing

- [x] Start frontend dev server
- [x] Navigate to `/library`
- [x] Verify 5 sample stories appear
- [x] Test search functionality
- [x] Test filter by theme
- [x] Test filter by tags
- [x] Click a story card → verify navigation to `/play/{id}`
- [x] Navigate back to library
- [x] Click "Create New Story" → verify navigation to `/create`
- [x] Test theme selector → verify visual changes

### Automated Testing

- [x] Backend tests: `cd backend && pytest` ✅ 88/88 passing
- [x] Frontend tests: `cd frontend && npm test` ✅ 50/50 passing
- [x] Linting: `cd backend && ruff check .` ✅ Passing
- [x] Type checking: `cd backend && mypy src/` ✅ Passing
- [x] Frontend linting: `cd frontend && npm run lint` ✅ Passing

---

## Risk Assessment

### Low Risk

- Navigation changes are straightforward
- Well-tested components won't be modified
- Changes are additive, not destructive

### Medium Risk

- Theme CSS injection might require debugging
- Need to test across browsers

### Mitigation

- Test thoroughly in dev environment
- Use feature flags if concerned
- Can roll back easily via git

---

## Success Metrics

After remediation:

- Phase 2 completion: **100%** (up from 85%)
- User Journey 2 completion: **90%** (up from 60%)
  - 10% gap remains for Phase 5 (play functionality)
- All critical gaps resolved
- Ready for Phase 3 kickoff

---

**Next Steps**:

1. Review this plan with team
2. Implement Priority 1 (navigation)
3. Test and verify
4. Implement Priority 2 (theme)
5. Update gap analysis with results
6. Mark Phase 2 as complete

---

**Created**: 2025-11-15
**Author**: GitHub Copilot Agent
**Status**: ✅ COMPLETED - All issues remediated
