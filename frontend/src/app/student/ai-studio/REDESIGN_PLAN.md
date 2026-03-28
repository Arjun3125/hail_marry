# AI Study Assistant Redesign Implementation Plan

## Phase 2: Information Architecture (Tool Groups)

### New Grouped Structure:

**Learning Hub** (Primary)
- Q&A - Ask anything about materials
- Study Guide - Comprehensive topic summaries
- Socratic Tutor - Guided discovery learning

**Practice Lab** (Assessment)
- Quiz - Multiple choice questions
- Flashcards - Spaced repetition cards
- Exam Prep - Question variations

**Thinking Studio** (Critical Analysis)
- Debate - Challenge your arguments
- Essay Review - Writing feedback

**Visual Studio** (Diagram Tools)
- Mind Maps - Hierarchical concepts
- Flowcharts - Process visualization
- Concept Maps - Relationship networks

## Phase 3: Layout Redesign

### New 3-Column Layout:

```
┌─────────────────┬──────────────────────────┬─────────────────┐
│                 │                          │                 │
│  TOOL RAIL      │    LEARNING WORKSPACE    │  CONTEXT PANEL  │
│  (Collapsible)  │                          │  (Collapsible)  │
│                 │                          │                 │
│  • Learning     │  ┌────────────────────┐  │  • Citations    │
│  • Practice     │  │                    │  │  • Quick Notes  │
│  • Thinking     │  │   Main Content     │  │  • Suggestions  │
│  • Visual       │  │   (Response/       │  │  • History      │
│                 │  │    Activity)       │  │                 │
│                 │  │                    │  │                 │
│  ─────────────  │  └────────────────────┘  │  ─────────────  │
│                 │                          │                 │
│  AI Assistant   │  ┌────────────────────┐  │  Settings       │
│  (Floating)     │  │  Action Bar         │  │  • Language     │
│                 │  │  [Quiz] [Flash]     │  │  • Length       │
│  ─────────────  │  │  [Mind] [Debate]    │  │  • Expertise    │
│                 │  └────────────────────┘  │                 │
│  Recent         │                          │                 │
│  History        │  ┌────────────────────┐  │                 │
│                 │  │  Input Field        │  │                 │
│                 │  │  [Ask anything...]  │  │                 │
│                 │  └────────────────────┘  │                 │
│                 │                          │                 │
└─────────────────┴──────────────────────────┴─────────────────┘
```

### Component Structure:

```
frontend/src/app/student/ai-studio/
├── page.tsx                    # Main unified page
├── layout.tsx                  # 3-column layout shell
├── components/
│   ├── ToolRail.tsx            # Collapsible left sidebar
│   ├── LearningWorkspace.tsx   # Central content area
│   ├── ContextPanel.tsx         # Right sidebar (citations, notes)
│   ├── FloatingAI.tsx           # Floating assistant button
│   ├── ActionBar.tsx            # Contextual post-response actions
│   ├── ResponseCard.tsx         # Enhanced response display
│   ├── ToolViews/
│   │   ├── QuizView.tsx         # Interactive quiz
│   │   ├── FlashcardDeck.tsx    # Swipeable cards
│   │   ├── MindMapCanvas.tsx    # Interactive D3/Canvas map
│   │   ├── FlowchartRenderer.tsx # Mermaid rendering
│   │   └── ConceptGraph.tsx     # Network visualization
│   ├── FocusMode.tsx            # Distraction-free overlay
│   ├── SmartSuggestions.tsx     # AI recommendations
│   └── ProgressTracker.tsx      # Study session stats
├── hooks/
│   ├── useKeyboardShortcuts.ts
│   ├── useFocusMode.ts
│   └── useStudySession.ts
└── types/
    └── ai-studio.ts
```

## Phase 4: Immersive Features

### Focus Mode
- Full-screen overlay triggered by "F" key or button
- Hides all UI except content
- Dark/light theme optimized for reading
- Progress bar at bottom

### Progressive Reveal
- Responses animate in word-by-word (optional)
- Citations fade in after main content
- Quiz questions reveal one at a time

### Animated Transitions
- Tool switching: slide + fade
- Response loading: typing indicator morphs into content
- Mode change: smooth gradient transition

## Phase 5: Tool Workflow Improvements

### Contextual Action Bar (Appears after AI response):

```
┌─────────────────────────────────────────────────────────┐
│  Continue learning:                                      │
│  [📝 Generate Quiz]  [🗂️ Make Flashcards]              │
│  [🧠 Create Mind Map]  [⚔️ Start Debate]                │
│  [📚 Save to Library]                                    │
└─────────────────────────────────────────────────────────┘
```

### Cross-Tool Flows:
1. Q&A → Flashcards (extract key facts)
2. Study Guide → Quiz (test comprehension)
3. Essay Review → Debate (explore counterarguments)
4. Any tool → Save to Library

## Phase 6: Visual Design System

### New Color Palette:

```css
/* Primary Learning Colors */
--learning-primary: #6366f1;      /* Indigo */
--learning-secondary: #8b5cf6;    /* Violet */
--practice-accent: #10b981;      /* Emerald */
--thinking-accent: #f59e0b;       /* Amber */
--visual-accent: #06b6d4;         /* Cyan */

/* Neutral Scale */
--surface-50: #fafafa;
--surface-100: #f5f5f5;
--surface-200: #e5e5e5;
--surface-800: #262626;
--surface-900: #171717;

/* Semantic Colors */
--success: #22c55e;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;
```

### Typography:
- Headings: Inter, 600-700 weight
- Body: Inter, 400 weight, 1.6 line-height
- Code: JetBrains Mono

### Card Design:
- Border radius: 16px (large), 12px (medium), 8px (small)
- Shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)
- Hover: translateY(-2px) + enhanced shadow

### Glassmorphism Elements:
- Background: rgba(255,255,255,0.8)
- Backdrop filter: blur(12px)
- Border: 1px solid rgba(255,255,255,0.2)

## Phase 7: Smart Assistant Features

### Study Progress Tracker:
- Session timer
- Questions answered count
- Concepts mastered (tracked via quiz performance)
- Streak counter

### Smart Suggestions:
```
"You've studied Photosynthesis for 15 minutes. 
 Ready to test your knowledge with a quiz?"

[Start Quiz] [Continue Reading] [Create Flashcards]
```

### Learning Path:
- Suggested sequence: Study Guide → Q&A → Quiz → Flashcards
- Difficulty auto-adjustment based on quiz scores

## Phase 8: Interaction Design

### Keyboard Shortcuts:

| Key | Action |
|-----|--------|
| `Cmd/Ctrl + K` | Command palette (tool switcher) |
| `F` | Toggle focus mode |
| `Esc` | Exit focus mode / close panels |
| `Cmd/Ctrl + Enter` | Submit query |
| `Cmd/Ctrl + L` | Toggle library panel |
| `1-4` | Quick tool group switch |
| `?` | Show keyboard help |

### Drag & Drop:
- Drag citations to notes panel
- Drag responses to library folders
- Reorder flashcards in deck

### Quick Tool Switcher (Cmd+K):
```
┌─────────────────────────────┐
│  🔍 Search tools...         │
├─────────────────────────────┤
│  Recent                     │
│  • Q&A - Photosynthesis      │
│  • Quiz - Cell Biology       │
│                             │
│  All Tools                  │
│  Learning > Q&A              │
│  Learning > Study Guide      │
│  Practice > Quiz             │
│  ...                        │
└─────────────────────────────┘
```

## Phase 9: Responsive Design

### Breakpoints:
- Mobile: < 640px - Single column, bottom sheet for tools
- Tablet: 640-1024px - Collapsible rail, full context panel
- Desktop: > 1024px - Full 3-column layout

### Mobile Adaptations:
- Tool rail becomes bottom tab bar
- Context panel becomes swipeable drawer
- Floating AI becomes floating action button
- Full-screen focus mode essential

## Phase 10: Implementation Order

### Sprint 1: Foundation
1. Create new page structure `ai-studio/`
2. Build ToolRail component with grouped tools
3. Implement 3-column layout shell
4. Add CSS variables for new design system

### Sprint 2: Core Experience
5. Migrate AI query functionality
6. Build enhanced ResponseCard
7. Add ContextPanel with citations
8. Implement ActionBar component

### Sprint 3: Tool Views
9. Rebuild QuizView with interactions
10. Create FlashcardDeck with swipe
11. Add MindMapCanvas (D3.js)
12. Implement FlowchartRenderer (Mermaid)

### Sprint 4: Polish & Intelligence
13. Add focus mode overlay
14. Implement keyboard shortcuts
15. Build SmartSuggestions
16. Add study progress tracker
17. Responsive mobile layout

### Sprint 5: Integration
18. Update navigation (replace ai + tools with ai-studio)
19. Migrate history data
20. Add transition animations
21. Final testing & polish

---

## Estimated Timeline: 3-4 weeks

## Dependencies to Add:
- `framer-motion` - Animations
- `d3` or `react-flow` - Mind maps & concept graphs
- `mermaid` - Flowchart rendering
- `cmdk` or `@radix-ui/react-command` - Command palette
- `@use-gesture/react` - Touch gestures for flashcards
