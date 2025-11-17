# ADR 001: Technology Stack Finalization

**Status**: Accepted
**Date**: 2025-11-12
**Decision Makers**: Engineering Lead, Principal Engineer
**Context**: Architecture review identified multiple undecided technology choices

---

## Context

The web interface architecture documentation listed several technology choices as "decision needed" or "to be determined." Before implementation begins in Phase 1, these decisions must be finalized to:

- Enable consistent development environment setup
- Avoid mid-implementation technology switches
- Establish clear dependencies and build tooling
- Provide concrete examples in implementation guides

**Decisions Needed**:

1. Frontend UI Component Library
2. Frontend State Management Approach
3. Frontend Build Tool
4. Production Deployment Platform

---

## Decision 1: Frontend UI Component Library

### Choice: **Material-UI v5 (MUI)**

### Alternatives Considered

| Option                 | Pros                                                                                                                    | Cons                                                                       | Score      |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------- |
| **Material-UI v5**     | Mature ecosystem, excellent TypeScript support, comprehensive component library, active maintenance, good documentation | Larger bundle size, opinionated design system                              | ⭐⭐⭐⭐⭐ |
| Chakra UI              | Modern, good accessibility, smaller bundle, composable                                                                  | Smaller community, fewer pre-built components, less mature                 | ⭐⭐⭐⭐☆  |
| Ant Design             | Very comprehensive, enterprise-ready, good for data-heavy UIs                                                           | Heavy bundle, Chinese-first documentation, less flexible theming           | ⭐⭐⭐☆☆   |
| Headless UI + Tailwind | Maximum flexibility, smallest bundle, full control                                                                      | Requires more custom implementation, steeper learning curve                | ⭐⭐⭐☆☆   |
| Custom Components      | Full control, perfect fit, learning opportunity                                                                         | Significant development time, maintenance burden, accessibility challenges | ⭐⭐☆☆☆    |

### Rationale

1. **TypeScript Support**: MUI has first-class TypeScript support with excellent type definitions, reducing runtime errors
2. **Component Coverage**: 50+ components out-of-box (buttons, modals, forms, data grids) accelerate development
3. **Theme System**: Built-in theming aligns with our multi-genre requirements (Warhammer 40K, Cyberpunk, Fantasy)
4. **Accessibility**: WCAG 2.1 AA compliant by default, meets our accessibility requirements
5. **Community & Support**: 80K+ GitHub stars, active maintenance, extensive Stack Overflow resources
6. **Bundle Size Trade-off**: Acceptable (~300KB gzipped with tree-shaking) for comprehensive features
7. **Migration Path**: Easy to migrate to custom components later if needed (MUI provides primitives)

### Implementation Details

```bash
# Installation
npm install @mui/material @emotion/react @emotion/styled

# Theme customization for multi-genre support
import { createTheme, ThemeProvider } from '@mui/material/styles';

const warhammer40kTheme = createTheme({
  palette: {
    primary: { main: '#8B0000' },
    secondary: { main: '#B8860B' },
    background: { default: '#1a1a1a', paper: '#2d2d2d' }
  }
});
```

### Consequences

- ✅ Faster development with pre-built components
- ✅ Consistent design language across application
- ✅ Strong TypeScript integration reduces bugs
- ⚠️ Bundle size ~300KB (acceptable for desktop-first MVP)
- ⚠️ Team must learn MUI patterns and conventions
- ⚠️ Theme customization requires understanding MUI theme structure

---

## Decision 2: State Management

### Choice: **React Context API + useReducer (All Phases)**

### Alternatives Considered

| Option                       | Pros                                                                          | Cons                                                                   | Score      |
| ---------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------- |
| **Context API + useReducer** | Built-in, zero dependencies, sufficient for single-user, simpler mental model | Not optimized for frequent updates, no time-travel debugging           | ⭐⭐⭐⭐⭐ |
| Redux Toolkit                | Powerful dev tools, time-travel debugging, large ecosystem                    | Overkill for single-user, boilerplate overhead, steeper learning curve | ⭐⭐⭐☆☆   |
| Zustand                      | Simple, minimal boilerplate, good performance                                 | Additional dependency, less familiar to React developers               | ⭐⭐⭐⭐☆  |
| Jotai/Recoil                 | Atomic state management, fine-grained reactivity                              | Unfamiliar API, smaller community, additional concepts                 | ⭐⭐⭐☆☆   |
| MobX                         | Reactive, minimal boilerplate, intuitive                                      | Different paradigm (reactive vs immutable), smaller community          | ⭐⭐⭐☆☆   |

### Rationale

1. **YAGNI Principle**: Single-user MVP doesn't need Redux's complexity
2. **No External Dependencies**: Built into React 18, zero bundle cost
3. **Sufficient Complexity**: 4 contexts handle our needs:
   - `ThemeContext`: Current theme configuration
   - `StoryContext`: Story library and active story
   - `GenerationContext`: Active generation job and progress
   - `GameContext`: Active gameplay session and state
4. **Simple Mental Model**: Team already knows Context API, no learning curve
5. **Migration Path Clear**: Can migrate to Redux Toolkit if multi-user scaling reveals performance issues

### When to Migrate to Redux

**Triggers for migration** (evaluate in Phase 4-5):

- Frequent state updates causing re-renders (>100ms UI lag)
- Need for time-travel debugging during complex bug investigation
- Multi-user features requiring normalized state with entity adapters
- Complex async state management (thunks, sagas needed)

**Current assessment**: None of these triggers apply to single-user MVP.

### Implementation Details

```typescript
// contexts/StoryContext.tsx
interface StoryState {
  stories: Story[];
  loading: boolean;
  error: Error | null;
}

type StoryAction =
  | { type: "FETCH_SUCCESS"; payload: Story[] }
  | { type: "FETCH_ERROR"; payload: Error }
  | { type: "ADD_STORY"; payload: Story };

function storyReducer(state: StoryState, action: StoryAction): StoryState {
  switch (action.type) {
    case "FETCH_SUCCESS":
      return { ...state, stories: action.payload, loading: false };
    case "FETCH_ERROR":
      return { ...state, error: action.payload, loading: false };
    case "ADD_STORY":
      return { ...state, stories: [action.payload, ...state.stories] };
    default:
      return state;
  }
}

export const StoryProvider: React.FC = ({ children }) => {
  const [state, dispatch] = useReducer(storyReducer, initialState);
  // ... provider implementation
};
```

### Consequences

- ✅ Zero dependencies, smaller bundle
- ✅ Team familiar with Context API
- ✅ Simpler codebase, easier onboarding
- ✅ Can migrate to Redux later if needed
- ⚠️ Manual optimization needed for frequently updating state (React.memo, useMemo)
- ⚠️ No time-travel debugging (acceptable trade-off)

---

## Decision 3: Frontend Build Tool

### Choice: **Vite**

### Alternatives Considered

| Option           | Pros                                                                                          | Cons                                                                         | Score      |
| ---------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------- |
| **Vite**         | Fastest dev server (instant HMR), modern ESM-based, excellent DX, optimized production builds | Newer (less battle-tested), fewer plugins than webpack                       | ⭐⭐⭐⭐⭐ |
| Create React App | Mature, zero-config, widely used, good documentation                                          | Slow dev server, webpack-based (slower), ejecting required for customization | ⭐⭐⭐☆☆   |
| Next.js          | Full-stack framework, excellent performance, SSR/SSG built-in                                 | Overkill for SPA, opinionated structure, heavier                             | ⭐⭐⭐☆☆   |
| Webpack (custom) | Maximum flexibility, mature ecosystem, powerful                                               | Complex configuration, slow dev server, steep learning curve                 | ⭐⭐☆☆☆    |

### Rationale

1. **Development Speed**: Dev server starts in <1s, HMR updates in <50ms (webpack: 5-10s, 1-2s)
2. **Modern Architecture**: Native ESM, no bundling in dev (faster iteration)
3. **TypeScript First-Class**: Zero config TypeScript support
4. **Production Optimization**: Rollup-based builds with excellent tree-shaking
5. **Developer Experience**: Instant feedback loop critical for UI-heavy development
6. **Future-Proof**: ESM is the JavaScript standard, Vite aligns with ecosystem direction
7. **React 18 Support**: Excellent support for concurrent features, suspense, transitions

### Performance Comparison

| Metric           | Vite                          | Create React App |
| ---------------- | ----------------------------- | ---------------- |
| Cold Start       | 0.5s                          | 8s               |
| HMR Update       | 20ms                          | 800ms            |
| Production Build | 15s                           | 45s              |
| Bundle Size      | Smaller (better tree-shaking) | Larger           |

### Implementation Details

```bash
# Create project
npm create vite@latest frontend -- --template react-ts

# Install dependencies
cd frontend
npm install

# Dev server (instant start)
npm run dev  # http://localhost:5173

# Production build
npm run build  # → dist/
```

**Configuration** (`vite.config.ts`):

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": "http://localhost:8000", // Backend proxy
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          mui: ["@mui/material", "@mui/icons-material"],
          "react-vendor": ["react", "react-dom", "react-router-dom"],
        },
      },
    },
  },
});
```

### Consequences

- ✅ Significantly faster development iteration (10x faster HMR)
- ✅ Better developer experience, less waiting
- ✅ Smaller production bundles (better tree-shaking)
- ✅ Modern architecture, future-proof
- ⚠️ Newer tool (less Stack Overflow answers than webpack)
- ⚠️ Some webpack plugins have no Vite equivalent (rare, mostly legacy)

---

## Decision 4: Deployment Platform

### Choice: **Docker Compose + Self-Hosted (MVP), Cloud-Ready Architecture**

### Alternatives Considered

| Option                                | Pros                                                                         | Cons                                                               | Score      |
| ------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------ | ---------- |
| **Docker + Self-Hosted**              | Full control, no vendor lock-in, cost-effective for single user, educational | Manual server management, security responsibility, scaling manual  | ⭐⭐⭐⭐⭐ |
| Railway                               | Easy deployment, good DX, auto-scaling, managed services                     | Monthly cost ($20+), vendor lock-in, overkill for single user      | ⭐⭐⭐⭐☆  |
| Render                                | Simple, free tier, managed DB/Redis, easy GitHub integration                 | Performance limits on free tier, vendor lock-in                    | ⭐⭐⭐⭐☆  |
| Vercel (frontend) + Railway (backend) | Best-in-class frontend hosting, auto-preview, fast CDN                       | Split infrastructure, more complex, higher cost                    | ⭐⭐⭐☆☆   |
| AWS (ECS/Fargate)                     | Enterprise-grade, unlimited scaling, full AWS ecosystem                      | Complex setup, overkill for MVP, steep learning curve, higher cost | ⭐⭐☆☆☆    |

### Rationale

1. **MVP Scope**: Single-user deployment prioritizes simplicity over scale
2. **Learning Opportunity**: Understanding Docker deployments is valuable skill
3. **Cost**: $5-10/month VPS (DigitalOcean, Linode) vs $20+/month managed platform
4. **Flexibility**: Can migrate to Railway/Render later with same Docker images
5. **Control**: Full control over nginx config, SSL, caching, monitoring
6. **Cloud-Ready**: Architecture designed for easy cloud migration (Phase 2)

### Implementation Details

**Development** (`docker-compose.yml`):

```yaml
version: "3.8"
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    volumes: ["./frontend:/app"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres/db
      - REDIS_URL=redis://redis:6379

  postgres:
    image: postgres:15
    volumes: ["postgres_data:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine

  celery:
    build: ./backend
    command: celery -A app.celery_app worker
```

**Production** (`docker-compose.prod.yml`):

```yaml
version: "3.8"
services:
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

  backend:
    image: space-hulk-backend:latest
    environment:
      - DATABASE_URL=postgresql://...
    deploy:
      replicas: 2 # Can scale horizontally
```

**Deployment Steps**:

1. Provision VPS (2GB RAM, 2 vCPU minimum)
2. Install Docker + Docker Compose
3. Clone repository, configure `.env`
4. Run `docker-compose -f docker-compose.prod.yml up -d`
5. Configure nginx with SSL (Let's Encrypt)
6. Set up monitoring (Prometheus + Grafana or simple logging)

### Migration Path to Cloud

**When to migrate** (evaluate in Phase 2):

- Need auto-scaling (multiple concurrent users)
- Want managed database/Redis (reduce ops burden)
- Require CDN for global users
- Need high availability (99.9%+ uptime)

**Migration effort**: 1-2 days (Docker images work on any platform)

### Consequences

- ✅ Full control over deployment
- ✅ Cost-effective for single user ($5-10/month)
- ✅ Educational value (learn Docker, nginx, SSL)
- ✅ Easy migration to cloud later (same Docker images)
- ⚠️ Manual server management required
- ⚠️ Security responsibility (updates, firewalls, SSL)
- ⚠️ Limited to single server (acceptable for MVP)

---

## Summary of Decisions

| Technology           | Decision             | Rationale                                               |
| -------------------- | -------------------- | ------------------------------------------------------- |
| **UI Library**       | Material-UI v5       | Comprehensive, TypeScript-first, good accessibility     |
| **State Management** | React Context API    | Built-in, sufficient for single-user, zero dependencies |
| **Build Tool**       | Vite                 | 10x faster dev server, modern ESM-based, better DX      |
| **Deployment**       | Docker + Self-Hosted | Full control, cost-effective, cloud-ready architecture  |

---

## Action Items

- [x] Document decisions in ADR
- [ ] Update IMPLEMENTATION_PLAN.md Task 1.3 with Vite setup commands
- [ ] Update ARCHITECTURAL_DESIGN.md Section 9.2 with MUI rationale
- [ ] Create `docker-compose.yml` and `docker-compose.prod.yml` templates
- [ ] Add Material-UI theme examples to THEMING_SYSTEM.md
- [ ] Update README.md with final technology stack

---

## Review and Approval

**Approved By**: Engineering Lead (pending)
**Date**: 2025-11-12
**Next Review**: After Phase 3 (evaluate state management performance)

---

**This ADR is now the canonical source for technology stack decisions. All implementation should follow these choices unless a new ADR supersedes this one.**
