# Theming System Design

## Document Information

**Version**: 1.0
**Created**: 2025-11-12
**Related**: PRD_WEB_INTERFACE.md, ARCHITECTURE_WEB_INTERFACE.md
**Purpose**: Define configurable theming system for multi-genre support

---

## Overview

The web interface must support multiple game genres and aesthetic themes, not just Warhammer 40K. The theming system should be runtime-configurable, allowing the UI to adapt based on the story being created or played.

**Design Principle**: **No hardcoded strings or visual styles**. All theme-related content loaded at runtime from theme configuration files.

---

## Theme Architecture

### Theme Configuration Structure

Each theme is defined in a JSON/YAML configuration file:

```yaml
# themes/warhammer40k.yaml
theme:
  id: "warhammer40k"
  name: "Warhammer 40,000"
  description: "Grimdark sci-fi horror in the far future"

  # Color palette
  colors:
    primary: "#8B0000" # Dark red - accent, CTAs
    secondary: "#B8860B" # Brass/gold - highlights, borders
    background: "#1a1a1a" # Deep gray - main background
    surface: "#2d2d2d" # Dark gray - cards, modals
    textPrimary: "#e0e0e0" # Off-white
    textSecondary: "#a0a0a0" # Light gray
    success: "#2d5016" # Dark green
    warning: "#cc5500" # Orange
    error: "#dc143c" # Crimson red

  # Typography
  typography:
    headingFont: "Roboto Bold, sans-serif"
    bodyFont: "Open Sans, sans-serif"
    monospaceFont: "Courier New, monospace"
    headingSizes:
      h1: "32px"
      h2: "24px"
      h3: "18px"
    bodySize: "16px"

  # UI text and labels
  labels:
    createStory: "Generate New Mission"
    playGame: "Deploy to Mission"
    storyLibrary: "Mission Archives"
    newStory: "New Mission Briefing"
    savedGames: "Mission Logs"

  # Game terminology
  terminology:
    story: "Mission"
    scene: "Location"
    item: "Equipment"
    npc: "Character"
    puzzle: "Objective"
    player: "Space Marine"

  # Visual assets
  assets:
    logo: "/themes/warhammer40k/logo.png"
    background: "/themes/warhammer40k/background.jpg"
    cardBorder: "/themes/warhammer40k/card-border.svg"
    icons:
      combat: "/themes/warhammer40k/icons/combat.svg"
      exploration: "/themes/warhammer40k/icons/exploration.svg"

  # Audio (optional)
  audio:
    ambientMusic: "/themes/warhammer40k/ambient.mp3"
    uiSounds:
      click: "/themes/warhammer40k/sounds/click.mp3"
      success: "/themes/warhammer40k/sounds/success.mp3"
```

### Additional Theme Examples

```yaml
# themes/cyberpunk.yaml
theme:
  id: "cyberpunk"
  name: "Cyberpunk"
  description: "High-tech dystopian future"

  colors:
    primary: "#00ff9f" # Neon green
    secondary: "#ff006e" # Hot pink
    background: "#0a0a0a" # Near black
    surface: "#1a1a2e" # Dark blue-gray
    # ... etc

  labels:
    createStory: "Jack In New Story"
    playGame: "Enter the Matrix"
    # ... etc
```

```yaml
# themes/fantasy.yaml
theme:
  id: "fantasy"
  name: "High Fantasy"
  description: "Medieval fantasy adventure"

  colors:
    primary: "#8B4513" # Brown
    secondary: "#FFD700" # Gold
    background: "#2F4F2F" # Forest green
    # ... etc

  labels:
    createStory: "Weave New Tale"
    playGame: "Begin Adventure"
    # ... etc
```

---

## Frontend Implementation

### Theme Provider Component

```typescript
// contexts/ThemeContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

interface ThemeConfig {
  id: string;
  name: string;
  colors: Record<string, string>;
  typography: Record<string, any>;
  labels: Record<string, string>;
  terminology: Record<string, string>;
  assets: Record<string, any>;
}

interface ThemeContextType {
  theme: ThemeConfig;
  availableThemes: ThemeConfig[];
  setTheme: (themeId: string) => void;
  getLabel: (key: string) => string;
  getTerm: (key: string) => string;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeConfig | null>(null);
  const [availableThemes, setAvailableThemes] = useState<ThemeConfig[]>([]);

  useEffect(() => {
    // Load available themes from API
    fetch('/api/v1/themes')
      .then(res => res.json())
      .then(data => {
        setAvailableThemes(data.themes);
        // Set default theme (from user preference or story metadata)
        const defaultTheme = data.themes.find(t => t.id === 'warhammer40k');
        setThemeState(defaultTheme);
      });
  }, []);

  const setTheme = (themeId: string) => {
    const newTheme = availableThemes.find(t => t.id === themeId);
    if (newTheme) {
      setThemeState(newTheme);
      // Apply CSS variables
      applyCSSVariables(newTheme);
    }
  };

  const getLabel = (key: string): string => {
    return theme?.labels[key] || key;
  };

  const getTerm = (key: string): string => {
    return theme?.terminology[key] || key;
  };

  return (
    <ThemeContext.Provider value={{ theme, availableThemes, setTheme, getLabel, getTerm }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
};

// Helper function to apply theme colors as CSS variables
function applyCSSVariables(theme: ThemeConfig) {
  const root = document.documentElement;
  Object.entries(theme.colors).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key}`, value);
  });
  Object.entries(theme.typography).forEach(([key, value]) => {
    if (typeof value === 'string') {
      root.style.setProperty(`--font-${key}`, value);
    }
  });
}
```

### Using Theme in Components

```typescript
// components/library/StoryCard.tsx
import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

const StoryCard: React.FC<{ story: Story }> = ({ story }) => {
  const { getLabel, getTerm, theme } = useTheme();

  return (
    <div className="story-card" style={{
      backgroundColor: `var(--color-surface)`,
      borderColor: `var(--color-secondary)`
    }}>
      <h3>{story.title}</h3>
      <p>{story.description}</p>
      <div className="metadata">
        <span>{story.sceneCount} {getTerm('scene')}s</span>
        <span>{story.itemCount} {getTerm('item')}s</span>
      </div>
      <button className="btn-primary">
        {getLabel('playGame')}
      </button>
    </div>
  );
};
```

---

## Backend Implementation

### Theme Storage

```python
# backend/app/models/theme.py
from sqlalchemy import Column, String, JSON
from app.storage.database import Base

class Theme(Base):
    """Theme configuration model."""
    __tablename__ = "themes"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    config = Column(JSON, nullable=False)  # Full theme configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
```

### Theme API Endpoints

```python
# backend/app/api/routes/themes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.storage.database import get_db
from app.models.theme import Theme

router = APIRouter()

@router.get("/themes")
async def list_themes(db: Session = Depends(get_db)):
    """List all available themes."""
    themes = db.query(Theme).filter_by(is_active=True).all()
    return {
        "themes": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                **t.config
            }
            for t in themes
        ]
    }

@router.get("/themes/{theme_id}")
async def get_theme(theme_id: str, db: Session = Depends(get_db)):
    """Get specific theme configuration."""
    theme = db.query(Theme).filter_by(id=theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    return {
        "id": theme.id,
        "name": theme.name,
        "description": theme.description,
        **theme.config
    }
```

### Story-Theme Association

```python
# backend/app/models/story.py
from sqlalchemy import Column, String, ForeignKey

class Story(Base):
    __tablename__ = "stories"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    # ... other fields ...
    theme_id = Column(String(50), ForeignKey("themes.id"), default="warhammer40k")
    # Theme can be set during creation or changed later
```

---

## User Experience Flow

### Theme Selection During Story Creation

1. **Template Selection Page**:
   - Each template can have a recommended theme
   - User can override with dropdown: "Choose aesthetic: [Warhammer 40K ▼]"

2. **Custom Prompt Page**:
   - Theme selector at top: "Story theme: [Warhammer 40K ▼]"
   - Selected theme affects template suggestions and examples

3. **Playing Games**:
   - Game interface automatically loads theme associated with story
   - User sees consistent aesthetic from library → creation → gameplay

### Theme Switching

- Library view uses default theme (user preference or system default)
- Clicking on a story card shows theme badge (e.g., "40K", "Cyberpunk", "Fantasy")
- Opening story details or playing game switches to story's theme
- Smooth CSS transition between themes (0.3s fade)

---

## CSS Implementation

### Theme Variables

```css
/* global.css */
:root {
  /* Default theme (Warhammer 40K) */
  --color-primary: #8b0000;
  --color-secondary: #b8860b;
  --color-background: #1a1a1a;
  --color-surface: #2d2d2d;
  --color-text-primary: #e0e0e0;
  --color-text-secondary: #a0a0a0;
  --color-success: #2d5016;
  --color-warning: #cc5500;
  --color-error: #dc143c;

  --font-heading: "Roboto Bold", sans-serif;
  --font-body: "Open Sans", sans-serif;
  --font-monospace: "Courier New", monospace;

  /* Dynamically updated by ThemeProvider */
}

/* Components use CSS variables */
.story-card {
  background-color: var(--color-surface);
  border: 2px solid var(--color-secondary);
  color: var(--color-text-primary);
  font-family: var(--font-body);
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-text-primary);
  font-family: var(--font-heading);
}
```

---

## Requirements Updates

### Functional Requirements - Theming

- **FR-5.1**: System MUST load theme configuration from database/API
- **FR-5.2**: System MUST apply theme to all UI components via CSS variables
- **FR-5.3**: System MUST allow users to select theme during story creation
- **FR-5.4**: System MUST persist theme association with story
- **FR-5.5**: System MUST automatically apply story's theme when playing
- **FR-5.6**: System SHOULD support theme switching in library view (user preference)
- **FR-5.7**: System MUST use theme terminology in all UI labels (no hardcoded strings)

### Non-Functional Requirements - Theming

- **NFR-7.1**: Theme switching MUST complete in <500ms
- **NFR-7.2**: All text labels MUST come from theme configuration (no hardcoded strings)
- **NFR-7.3**: Adding new theme MUST NOT require code changes (config file only)
- **NFR-7.4**: Default theme SHOULD be Warhammer 40K for backward compatibility

---

## Migration Strategy

### Phase 1: Infrastructure (Week 1-2)

- Create Theme database model
- Add theme API endpoints
- Implement ThemeProvider component
- Convert hardcoded colors to CSS variables

### Phase 2: Label Extraction (Week 3-4)

- Identify all hardcoded UI strings
- Create theme label keys
- Update components to use `getLabel()` and `getTerm()`
- Test with Warhammer 40K theme (verify no visual changes)

### Phase 3: Additional Themes (Week 5-6)

- Create cyberpunk theme configuration
- Create fantasy theme configuration
- Test theme switching
- Document theme creation process

### Phase 4: User Features (Week 7-8)

- Add theme selector to story creation
- Add theme badge to story cards
- Implement user preference storage
- Polish theme transitions

---

## Default Themes to Include

### MVP (Phase 1)

1. **Warhammer 40,000** - Grimdark sci-fi (default, existing aesthetic)

### Post-MVP (Phase 2-3)

2. **Cyberpunk** - High-tech dystopia
3. **High Fantasy** - Medieval magic and dragons
4. **Cosmic Horror** - Lovecraftian dread
5. **Space Opera** - Star Trek/Star Wars style
6. **Steampunk** - Victorian sci-fi
7. **Post-Apocalyptic** - Wasteland survival
8. **Noir Detective** - 1940s mystery

---

## Documentation Updates

Update all documentation to clarify:

- Warhammer 40K is the **default** theme, not the only theme
- System designed for multi-genre support
- Theme configuration is runtime-loaded, not hardcoded
- Examples show Warhammer 40K for consistency, but apply to any theme

### Updated Language

**Before**: "Warhammer 40K themed UI with grimdark aesthetic"
**After**: "Themeable UI with configurable aesthetics (default: Warhammer 40K grimdark)"

**Before**: "Gothic horror atmosphere"
**After**: "Genre-appropriate atmosphere based on selected theme"

**Before**: "Space Marine player"
**After**: "Player character (terminology varies by theme)"

---

## Testing Strategy

### Theme Switching Tests

- Verify CSS variables update correctly
- Verify labels change based on theme
- Verify terminology changes throughout UI
- Verify assets load correctly

### Multi-Theme Tests

- Create story with cyberpunk theme
- Play story and verify cyberpunk aesthetic applied
- Return to library and verify default theme restored
- Create second story with fantasy theme
- Verify each story maintains its own theme

### Performance Tests

- Theme switching completes in <500ms
- No visual flicker during theme change
- CSS transitions smooth

---

## Future Enhancements

1. **User-Created Themes**: Allow users to create custom themes
2. **Theme Marketplace**: Share and download community themes
3. **Theme Inheritance**: Base themes can extend other themes
4. **Dynamic Theming**: AI generates theme based on story content
5. **Accessibility Themes**: High contrast, colorblind-friendly variants

---

**This theming system ensures the web interface can support any genre, not just Warhammer 40K, while maintaining a polished, cohesive user experience for each aesthetic.**

**Version**: 1.0
**Last Updated**: 2025-11-12
**Status**: Ready for Implementation
