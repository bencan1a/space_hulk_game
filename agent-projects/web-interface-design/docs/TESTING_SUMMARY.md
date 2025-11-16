# Testing Strategy Summary

## Web Interface Testing Requirements at a Glance

**Version**: 1.0
**Created**: 2025-11-12
**Full Document**: [testing-strategy.md](./testing-strategy.md)

---

## Quick Reference

### Test Count Overview

| Category | Count | Coverage Target |
|----------|-------|-----------------|
| **Backend Unit Tests** | 68 | 90%+ overall, 95%+ critical |
| **Frontend Unit Tests** | 55 | 80%+ overall, 90%+ critical |
| **Integration Tests** | 50 | N/A |
| **End-to-End Tests** | 15 critical journeys | N/A |
| **Performance Tests** | 4 scenarios | N/A |
| **Accessibility Tests** | 20 | WCAG 2.1 AA |
| **Security Tests** | 22 | Zero high/critical issues |
| **TOTAL** | **230+** | - |

### Testing Pyramid Distribution

```
         E2E (10%)
          /\
         /  \
        /    \
   Integration (30%)
      /        \
     /          \
    /____________\
   Unit Tests (60%)
```

### Critical Path Modules (>95% Coverage Required)

**Backend**:

- `app/services/generation_service.py`
- `app/services/game_service.py`
- `app/integrations/crewai_wrapper.py`
- `app/integrations/game_wrapper.py`
- `app/api/routes/stories.py`
- `app/api/routes/gameplay.py`
- `app/api/websocket.py`

**Frontend**:

- `src/contexts/GameContext.tsx`
- `src/contexts/StoryContext.tsx`
- `src/hooks/useWebSocket.ts`
- `src/services/api.ts`
- `src/components/GameDisplay.tsx`
- `src/components/GenerationProgress.tsx`

---

## Test Requirements by Phase

### Phase 1: Foundation (Weeks 1-4)

- **Unit Tests**: 15
- **Integration Tests**: 5
- **Target Coverage**: 85%

**Key Tests**:

- Database migrations (up/down)
- Health check endpoint
- Config loading
- Docker Compose services communication

### Phase 2: Story Library (Weeks 5-6)

- **Unit Tests**: 25 (15 backend + 10 frontend)
- **Integration Tests**: 10
- **Target Coverage**: 90% backend, 80% frontend

**Key Tests**:

- StoryService CRUD (15 tests)
- StoryCard component (8 tests)
- Search/filter API integration

### Phase 3: Story Creation (Weeks 7-10)

- **Unit Tests**: 35 (20 backend + 15 frontend)
- **Integration Tests**: 15
- **E2E Tests**: 3
- **Performance Tests**: 2
- **Target Coverage**: 95% (critical path)

**Key Tests**:

- GenerationService (12 tests)
- CrewAI wrapper (7 tests)
- WebSocket progress (8 tests)
- Complete generation workflow (E2E)

### Phase 4: Iteration System (Weeks 11-12)

- **Unit Tests**: 15
- **Integration Tests**: 5
- **E2E Tests**: 2
- **Target Coverage**: 90%

**Key Tests**:

- IterationService (8 tests)
- Feedback validation
- Iteration flow with context (E2E)

### Phase 5: Gameplay (Weeks 13-15)

- **Unit Tests**: 25 (15 backend + 10 frontend)
- **Integration Tests**: 10
- **E2E Tests**: 5
- **Performance Tests**: 2
- **Target Coverage**: 95% (critical path)

**Key Tests**:

- GameService (10 tests)
- Game wrapper (8 tests)
- GameDisplay component (10 tests)
- Complete gameplay session (E2E)

### Phase 6: Polish (Week 16)

- **E2E Tests**: 5 (complete all 15)
- **Accessibility Tests**: 20
- **Security Tests**: 22
- **Performance Tests**: 4 (complete all)

---

## Test Frameworks & Tools

### Backend

- **Unit**: pytest, pytest-cov, pytest-mock, pytest-asyncio
- **Integration**: pytest with PostgreSQL test instance
- **API**: httpx AsyncClient
- **Security**: Bandit, Safety, Semgrep

### Frontend

- **Unit**: Jest, React Testing Library
- **Integration**: Jest with mock API
- **E2E**: Playwright (recommended) or Cypress
- **Accessibility**: axe-core, Lighthouse

### Performance

- **Load Testing**: k6 or Locust
- **Monitoring**: Grafana, Prometheus

### CI/CD

- **Platform**: GitHub Actions
- **Coverage**: Codecov
- **Containers**: Docker Compose

---

## Key Testing Patterns

### Backend Unit Test Pattern

```python
@pytest.fixture
def service(mock_db):
    return Service(db=mock_db)

def test_method_success(service, sample_data):
    # Arrange
    expected = "result"

    # Act
    result = service.method(sample_data)

    # Assert
    assert result == expected
    service.db.commit.assert_called_once()
```

### Frontend Unit Test Pattern

```typescript
describe('Component', () => {
  it('renders correctly', () => {
    render(<Component {...props} />);
    expect(screen.getByText('Expected')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const onClick = jest.fn();
    render(<Component onClick={onClick} />);

    await userEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalled();
  });
});
```

### Integration Test Pattern

```python
@pytest.mark.integration
async def test_api_workflow(client, db_session):
    # Step 1: Create resource
    response = await client.post("/api/v1/resource", json=data)
    assert response.status_code == 201

    # Step 2: Verify in database
    resource = await db_session.get(Resource, response.json()["id"])
    assert resource is not None

    # Step 3: Update and verify
    # ...
```

### E2E Test Pattern

```typescript
test('user completes workflow', async ({ page }) => {
  // Navigate
  await page.goto('/');

  // Interact
  await page.click('[data-testid="button"]');
  await page.fill('[data-testid="input"]', 'value');
  await page.click('[data-testid="submit"]');

  // Verify
  await expect(page.locator('[data-testid="result"]')).toBeVisible();
  await expect(page).toHaveURL('/success');
});
```

---

## Performance Benchmarks

| Operation | p50 | p95 | p99 |
|-----------|-----|-----|-----|
| GET /api/v1/stories | <50ms | <100ms | <200ms |
| POST /api/v1/stories | <200ms | <500ms | <1s |
| POST /api/v1/game/{id}/command | <100ms | <500ms | <1s |
| Story generation (full) | <5min | <10min | <15min |
| Library page load | <1s | <2s | <3s |

**Concurrent Users**:

- 100 concurrent API users
- 10 concurrent story generations
- 50 concurrent gameplay sessions
- 100 concurrent WebSocket connections

---

## Accessibility Requirements (WCAG 2.1 AA)

**Must Pass**:

- [ ] All interactive elements keyboard accessible
- [ ] Screen reader compatible
- [ ] Color contrast ≥4.5:1
- [ ] Focus indicators visible
- [ ] Alt text for images
- [ ] ARIA labels for dynamic content
- [ ] Form field labels and errors

**Tools**:

- axe-core (automated)
- NVDA, JAWS, VoiceOver (manual)
- Lighthouse audit (score ≥95)

---

## Security Testing Checklist

**Input Validation**:

- [ ] SQL injection blocked
- [ ] XSS injection blocked
- [ ] Path traversal blocked
- [ ] Command injection blocked

**File System**:

- [ ] Access restricted to data/ directory
- [ ] Symlink attacks prevented
- [ ] File permissions correct

**Rate Limiting**:

- [ ] 1 concurrent generation per user
- [ ] API rate limit enforced (future)

**Resource Limits**:

- [ ] Max file size enforced
- [ ] Memory limits
- [ ] Operation timeouts

---

## CI/CD Requirements

**All Tests Must Pass Before Merge**:

- ✅ Backend unit tests (>90% coverage)
- ✅ Frontend unit tests (>80% coverage)
- ✅ Integration tests (all passing)
- ✅ E2E tests (critical journeys)
- ✅ Security scan (no high/critical issues)
- ✅ Accessibility (no blocking violations)

**CI Performance Targets**:

- Unit tests: <5 minutes
- Integration tests: <10 minutes
- E2E tests: <30 minutes
- Full pipeline: <45 minutes

---

## 15 Critical E2E User Journeys

1. ✅ First-time user creates story from template
2. ✅ Veteran user iterates on existing story
3. ✅ User plays game to completion
4. ✅ User saves and loads game
5. ✅ User browses library and filters
6. ✅ User switches themes
7. ✅ Generation timeout error recovery
8. ✅ WebSocket disconnect and reconnect
9. ✅ Invalid prompt validation
10. ✅ Iteration limit reached
11. ✅ Concurrent generation attempt
12. ✅ Sample story cannot be deleted
13. ✅ Large story performance
14. ✅ Mobile browser gameplay
15. ✅ Keyboard navigation (accessibility)

---

## Test Data Management

**Test Database Strategy**:

- Unit tests: SQLite in-memory
- Integration tests: PostgreSQL test instance
- Reset between tests
- Seed with fixtures

**Test Fixtures**:

- `sample_story`: Complete story
- `incomplete_story`: Story in generation
- `generation_job_queued`: Queued job
- `game_session_active`: Active game session
- `sample_game_content`: Valid game.json

**Test Data Files** (`tests/data/`):

- `game-content/`: Valid, minimal, large, invalid game.json
- `themes/`: Valid and invalid theme configs
- `templates/`: Horror, rescue, artifact hunt templates
- `saves/`: Sample save game files

---

## Example Test Files

**Backend Unit Test**: [backend-unit-test-example.py](./testing-examples/backend-unit-test-example.py)

- 15 StoryService tests
- Fixtures, mocks, arrange-act-assert pattern
- Success, error, and edge case tests

**Frontend Unit Test**: [frontend-unit-test-example.tsx](./testing-examples/frontend-unit-test-example.tsx)

- 8 StoryCard rendering tests
- User interaction tests
- Accessibility tests
- Snapshot tests

**Integration Test**: [integration-test-example.py](./testing-examples/integration-test-example.py)

- Complete generation workflow (12 steps)
- Iteration flow with feedback (8 steps)
- Game session lifecycle (10 steps)
- WebSocket progress updates (6 steps)

**E2E Test**: [e2e-test-example.spec.ts](./testing-examples/e2e-test-example.spec.ts)

- First-time user creates story (10 steps)
- Generation timeout recovery
- WebSocket reconnection
- Input validation

---

## Acceptance Criteria Template

Every task in IMPLEMENTATION_PLAN.md must include:

```markdown
**Testing**:
- [ ] N unit tests written (see testing-strategy.md section X.X.X)
- [ ] M integration tests written
- [ ] Coverage >X% (backend) / >Y% (frontend)
- [ ] All tests passing in CI
- [ ] Test data fixtures created
```

**Example for Task 2.1 (Story Service)**:

```markdown
**Testing**:
- [ ] 15 unit tests written (see testing-strategy.md section 2.1.1)
- [ ] 100% coverage of public methods
- [ ] All success, error, and edge cases tested
- [ ] Mock database session used
- [ ] All tests passing in CI
```

---

## Quick Start

### Run All Tests

```bash
# Backend
pytest tests/ -v --cov=app --cov-report=html

# Frontend
npm run test:coverage

# E2E
npm run test:e2e

# Performance
k6 run tests/performance/load-test.js
```

### Run Specific Test Category

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v -m integration

# E2E critical journeys
npm run test:e2e -- --grep "Critical"

# Accessibility
npm run test:a11y
```

### Check Coverage

```bash
# Backend coverage threshold
pytest --cov=app --cov-fail-under=90

# Frontend coverage threshold
npm run test:coverage -- --coverageThreshold='{"global":{"lines":80}}'
```

---

## Resources

**Full Documentation**:

- [Complete Testing Strategy](./testing-strategy.md) (20+ pages)
- [Backend Unit Test Example](./testing-examples/backend-unit-test-example.py)
- [Frontend Unit Test Example](./testing-examples/frontend-unit-test-example.tsx)
- [Integration Test Example](./testing-examples/integration-test-example.py)
- [E2E Test Example](./testing-examples/e2e-test-example.spec.ts)

**Related Documents**:

- [Architectural Design](../ARCHITECTURAL_DESIGN.md)
- [Implementation Plan](../IMPLEMENTATION_PLAN.md)
- [API Specification](../API_SPECIFICATION.md)

---

**Status**: ✅ Ready for Implementation
**Last Updated**: 2025-11-12
