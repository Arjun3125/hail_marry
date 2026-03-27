# AI Study Assistant - UX Redesign Plan

## Overview

This document outlines a comprehensive 10-phase UX redesign of the AI Study Assistant platform. The goal is to transform the current functional-but-cluttered interface into an immersive, intuitive, and aesthetically pleasing learning environment that reduces cognitive load while enhancing engagement.

---

## Phase 1: Current UI Analysis

### 1.1 Usability Friction Points

| Issue | Location | User Impact | Severity |
|-------|----------|-------------|----------|
| **Mode overload** | AI page - 8 mode buttons in grid | Users struggle to find the right tool quickly | High |
| **Hidden settings** | Collapsible settings panel | Important options (language, length) require 2+ clicks | Medium |
| **No visual feedback** | During AI processing | Users unsure if system is working | Medium |
| **Buried citations** | Bottom of response | Users miss source verification | Low |
| **Tool/page separation** | AI and Tools are separate pages | Context switching disrupts learning flow | High |

### 1.2 Cognitive Overload Issues

**Current State:**
- 8 AI modes displayed simultaneously in a 4-column grid
- Each mode has different color gradients, creating visual chaos
- Settings panel opens over content, blocking context
- History sidebar takes up space even when not needed
- No visual hierarchy between primary and secondary actions

**User Confusion Points:**
1. "Which mode should I use for flashcards?" (Quiz vs Study Tools confusion)
2. "Where are my previous conversations?" (History not immediately visible)
3. "How do I change the response language?" (Hidden in settings)
4. "Can I see the sources while reading the answer?" (Citations at bottom)

### 1.3 Navigation Inefficiencies

```
Current User Flow (Inefficient):
User wants to study a topic →
  Go to AI Assistant page →
  Ask about topic →
  Read response →
  Want to create flashcards →
  Navigate to Study Tools page →
  Re-enter topic →
  Generate flashcards

Problem: Context loss, duplicate input, 2-page navigation
```

### 1.4 Visual Hierarchy Issues

- **No clear primary action**: 8 mode buttons compete for attention
- **Inconsistent card styles**: Chat bubbles vs response cards vs settings panels
- **Color overload**: Each mode has different gradient (8 different color schemes)
- **Typography inconsistency**: Mixed font weights and sizes without system

### 1.5 Interaction Inefficiencies

- No keyboard shortcuts for power users
- No way to quickly switch between recent tools
- Drag-and-drop not supported for organizing content
- No quick actions from response (must navigate away)

---

## Phase 2: Information Architecture

### 2.1 Tool Grouping Strategy

**New Grouped Structure:**

```
┌─────────────────────────────────────────────────────────────┐
│  LEARNING HUB (Indigo theme)                                │
│  ├─ Q&A - Ask anything about materials                      │
│  ├─ Study Guide - Comprehensive topic summaries            │
│  └─ Socratic Tutor - Guided discovery learning             │
├─────────────────────────────────────────────────────────────┤
│  PRACTICE LAB (Emerald theme)                               │
│  ├─ Quiz - Multiple choice questions                        │
│  ├─ Flashcards - Spaced repetition cards                   │
│  └─ Exam Prep - Question variations (perturbation)         │
├─────────────────────────────────────────────────────────────┤
│  THINKING STUDIO (Amber theme)                              │
│  ├─ Debate - Challenge your arguments                        │
│  └─ Essay Review - Writing feedback                         │
├─────────────────────────────────────────────────────────────┤
│  VISUAL STUDIO (Cyan theme)                                 │
│  ├─ Mind Maps - Hierarchical concept maps                  │
│  ├─ Flowcharts - Process visualization                       │
│  └─ Concept Maps - Relationship networks                    │
├─────────────────────────────────────────────────────────────┤
│  CAREER CENTER (Pink theme)                                 │
│  └─ Career Simulation - Role-play professional scenarios   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Mental Model Alignment

**Student Learning Journey:**
1. **Discover** (Learning Hub) → Understand the topic
2. **Practice** (Practice Lab) → Test knowledge
3. **Deepen** (Thinking Studio) → Critical analysis
4. **Visualize** (Visual Studio) → Structure understanding
5. **Apply** (Career Center) → Real-world context

### 2.3 Visual Grouping Design

- Each group has consistent color coding
- Group headers in sidebar with accent dots
- Tools within group share visual theme
- Progressive disclosure: expand/collapse groups

---

## Phase 3: Layout Redesign

### 3.1 New 3-Column Layout

```
┌─────────────────┬──────────────────────────┬─────────────────┐
│                 │                          │                 │
│  TOOL RAIL      │    LEARNING WORKSPACE    │  CONTEXT PANEL  │
│  (Collapsible)  │                          │  (Collapsible)  │
│     256px       │        Flexible          │     320px       │
│                 │                          │                 │
│  ┌───────────┐ │  ┌────────────────────┐  │  ┌───────────┐  │
│  │ AI Studio │ │  │                    │  │  │ Sources   │  │
│  │   Logo    │ │  │   Response Card    │  │  │   Tab     │  │
│  └───────────┘ │  │                    │  │  └───────────┘  │
│                 │  ├────────────────────┤  │                 │
│  ─────────────  │  │                    │  │  ┌───────────┐  │
│                 │  │   Main Content     │  │  │  Notes    │  │
│  ● Learning     │  │   (Markdown/       │  │  │   Tab     │  │
│    ○ Q&A        │  │    Interactive)    │  │  └───────────┘  │
│    ○ Study Guide│  │                    │  │                 │
│    ○ Socratic   │  └────────────────────┘  │  ┌───────────┐  │
│                 │                          │  │   Hints     │  │
│  ─────────────  │  ┌────────────────────┐  │  │   Tab     │  │
│                 │  │  Action Bar         │  │  └───────────┘  │
│  ● Practice     │  │  [Quiz] [Flash]     │  │                 │
│    ○ Quiz       │  │  [Mind] [Debate]    │  │  ┌───────────┐  │
│    ○ Flashcards │  └────────────────────┘  │  │  Settings │  │
│    ○ Exam Prep  │                          │  │  Language │  │
│                 │  ┌────────────────────┐  │  │  Length   │  │
│  ─────────────  │  │  Input Field        │  │  │  Level    │  │
│                 │  │  [Ask anything...]  │  │  └───────────┘  │
│  ● Thinking     │  └────────────────────┘  │                 │
│    ○ Debate     │                          │                 │
│    ○ Essay      │                          │                 │
│                 │                          │                 │
│  ─────────────  │                          │                 │
│                 │                          │                 │
│  ● Visual       │                          │                 │
│    ○ Mind Map   │                          │                 │
│    ○ Flowchart  │                          │                 │
│    ○ Concept    │                          │                 │
│                 │                          │                 │
│  ─────────────  │                          │                 │
│                 │                          │                 │
│  ● Career       │                          │                 │
│    ○ Career Sim │                          │                 │
│                 │                          │                 │
└─────────────────┴──────────────────────────┴─────────────────┘
```

### 3.2 Component Specifications

**Tool Rail (Left Column):**
- Width: 256px (collapsed: 64px)
- Collapsible sections for each tool group
- Color-coded group headers with accent dots
- Current tool highlighted with group color
- Hover shows tool description

**Learning Workspace (Center):**
- Flexible width (fills available space)
- Tool header with icon and description
- Conversation/thread view for responses
- Action bar under each response
- Input area anchored at bottom

**Context Panel (Right Column):**
- Width: 320px (collapsed: 48px)
- Tabbed interface: Sources, Notes, Hints, History
- Settings section at bottom
- Collapsible to save space

### 3.3 Responsive Breakpoints

| Breakpoint | Layout | Tool Rail | Context Panel |
|------------|--------|-----------|---------------|
| Desktop (>1024px) | 3-column | 256px | 320px |
| Tablet (640-1024px) | 2-column | Collapsed 64px | 320px |
| Mobile (<640px) | 1-column | Bottom sheet | Drawer |

---

## Phase 4: Immersive Learning Experience

### 4.1 Animated Transitions

**Tool Switching Animation:**
```css
/* Slide + fade transition */
.tool-switch-enter {
  opacity: 0;
  transform: translateX(20px);
}
.tool-switch-enter-active {
  opacity: 1;
  transform: translateX(0);
  transition: all 300ms ease-out;
}
```

**Response Loading:**
- Typing indicator morphs into content
- Staggered fade-in for citations
- Smooth height expansion for long responses

**Card Flip (Flashcards):**
```css
.flashcard {
  transition: transform 500ms;
  transform-style: preserve-3d;
}
.flashcard.flipped {
  transform: rotateY(180deg);
}
```

### 4.2 Focus Mode

**Activation:**
- Keyboard: Press `F`
- Button: Click focus icon in header
- Auto-trigger: Scroll past 50% of content

**Focus Mode Features:**
- Full-screen overlay
- Hides all UI except content
- Dark/light theme optimized for reading
- Progress bar at bottom
- Keyboard shortcuts help (press `?`)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  [Exit Focus]              Focus Mode              [? Help] │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                                                     │    │
│  │            Content goes here...                     │    │
│  │            (distraction-free)                       │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│              Progress: 65%                                    │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Distraction-Free Reading View

- Reading time estimation display
- Font size controls (small/medium/large)
- Line height adjustment
- Paragraph spacing toggle
- Highlight/annotation tools

### 4.4 Interactive Diagrams

**Mind Map Interactions:**
- Click node to expand/collapse children
- Drag to pan canvas
- Zoom with mouse wheel
- Double-click to edit node
- Right-click for context menu

**Flowchart Interactions:**
- Step-through animation
- Click step to see details
- Progress tracking through flow
- Decision path highlighting

### 4.5 Progressive Reveal

**Implementation:**
```javascript
// Response content reveals word by word
const ProgressiveReveal = ({ text, speed = 50 }) => {
  const [visibleChars, setVisibleChars] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setVisibleChars(c => Math.min(c + 1, text.length));
    }, speed);
    return () => clearInterval(interval);
  }, [text]);
  
  return <span>{text.slice(0, visibleChars)}</span>;
};
```

**Use Cases:**
- Socratic tutor: Reveal hints progressively
- Quiz questions: Show one at a time
- Study guides: Section-by-section reveal

---

## Phase 5: Tool Workflow Improvements

### 5.1 Contextual Action Bar

**Location:** Under every AI response
**Purpose:** Continue learning without navigation

```
┌─────────────────────────────────────────────────────────────┐
│  AI Response Content...                                      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Continue learning:                                          │
│  [📝 Generate Quiz]  [🗂️ Make Flashcards]                   │
│  [🧠 Create Mind Map]  [⚔️ Start Debate]                     │
│  [📚 Save to Library]                                        │
└─────────────────────────────────────────────────────────────┘
```

**Smart Actions (context-aware):**
- After Q&A: Suggest quiz, flashcards, mind map
- After Study Guide: Suggest practice quiz
- After Debate: Suggest essay review
- After Essay Review: Suggest debate on feedback

### 5.2 Cross-Tool Data Flow

**Data Passing:**
```javascript
// Q&A → Flashcards
const handleCreateFlashcards = (response) => {
  const facts = extractKeyFacts(response.answer);
  navigateToTool('flashcards', { 
    topic: response.query,
    suggestedCards: facts 
  });
};

// Study Guide → Quiz
const handleGenerateQuiz = (response) => {
  const sections = parseSections(response.answer);
  navigateToTool('quiz', {
    topic: response.query,
    content: sections
  });
};
```

### 5.3 Save to Library Workflow

**One-Click Save:**
- Button in action bar
- Auto-categorize by tool type
- Add to recent/favorites
- Option to add notes/tags

---

## Phase 6: Visual Design System

### 6.1 Color Palette

**Primary Colors:**
```css
/* Indigo - Learning Hub */
--learning-primary: #6366f1;
--learning-secondary: #8b5cf6;
--learning-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);

/* Emerald - Practice Lab */
--practice-primary: #10b981;
--practice-secondary: #14b8a6;
--practice-gradient: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);

/* Amber - Thinking Studio */
--thinking-primary: #f59e0b;
--thinking-secondary: #f97316;
--thinking-gradient: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);

/* Cyan - Visual Studio */
--visual-primary: #06b6d4;
--visual-secondary: #3b82f6;
--visual-gradient: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);

/* Pink - Career Center */
--career-primary: #ec4899;
--career-secondary: #d946ef;
--career-gradient: linear-gradient(135deg, #ec4899 0%, #d946ef 100%);
```

**Neutral Scale:**
```css
--surface-50: #fafafa;
--surface-100: #f5f5f5;
--surface-200: #e5e5e5;
--surface-300: #d4d4d4;
--surface-400: #a3a3a3;
--surface-500: #737373;
--surface-600: #525252;
--surface-700: #404040;
--surface-800: #262626;
--surface-900: #171717;
```

**Semantic Colors:**
```css
--success: #22c55e;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;
```

### 6.2 Typography

**Font Stack:**
```css
--font-heading: 'Inter', system-ui, -apple-system, sans-serif;
--font-body: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

**Type Scale:**
| Level | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| H1 | 24px | 700 | 1.3 | Page titles |
| H2 | 20px | 600 | 1.4 | Section headers |
| H3 | 16px | 600 | 1.5 | Card titles |
| Body | 14px | 400 | 1.6 | Main content |
| Small | 12px | 400 | 1.5 | Secondary text |
| Tiny | 10px | 500 | 1.4 | Labels, badges |

### 6.3 Card Layouts

**Response Card:**
```
┌─────────────────────────────────────────────────┐
│ ┌────┬─────────────────────────────────────────┐│
│ │ AI │ AI Assistant          10:42 AM     [...]││
│ └────┴─────────────────────────────────────────┘│
│                                                 │
│ Content goes here...                           │
│                                                 │
│ ─────────────────────────────────────────────── │
│ Sources: [Doc1] [Doc2] [Doc3]                   │
│ ─────────────────────────────────────────────── │
│ [👍] [👎] [💾]          [Quiz] [Flash] [Mind]   │
└─────────────────────────────────────────────────┘
```

**Tool Card (in sidebar):**
```
┌─────────────────────────────────────┐
│ ┌────┬────────────────────────────┐ │
│ │ ◉  │ Tool Name              ▶   │ │
│ └────┴────────────────────────────┘ │
│ Description text here...            │
└─────────────────────────────────────┘
```

### 6.4 Spacing System

**Base Unit: 4px**

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 4px | Tight spacing, icon gaps |
| space-2 | 8px | Compact elements |
| space-3 | 12px | Default padding |
| space-4 | 16px | Card padding |
| space-5 | 20px | Section gaps |
| space-6 | 24px | Large sections |
| space-8 | 32px | Page margins |
| space-10 | 40px | Major divisions |

### 6.5 Shadow & Elevation

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* Glassmorphism */
--glass-bg: rgba(255, 255, 255, 0.8);
--glass-blur: blur(12px);
--glass-border: 1px solid rgba(255, 255, 255, 0.2);
```

---

## Phase 7: Smart Study Assistant

### 7.1 Study Progress Tracker

**Dashboard Widget:**
```
┌─────────────────────────────────────┐
│ 📊 Your Study Session               │
├─────────────────────────────────────┤
│                                     │
│  Time: 45m    Questions: 12    🔥 3  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  ████████████░░░░░░░░  65%          │
│                                     │
│  Topics covered:                    │
│  ✅ Photosynthesis                  │
│  ✅ Cell Structure                  │
│  🔄 Mitosis (in progress)           │
│                                     │
└─────────────────────────────────────┘
```

**Metrics Tracked:**
- Session duration
- Questions asked per topic
- Tools used
- Concepts mastered (via quiz scores)
- Streak counter
- Daily/weekly goals

### 7.2 Difficulty Adjustment

**Adaptive Algorithm:**
```javascript
const adjustDifficulty = (quizResults) => {
  const avgScore = calculateAverage(quizResults);
  
  if (avgScore > 85) return 'advanced';
  if (avgScore > 60) return 'standard';
  return 'simple';
};
```

**Auto-Adjustment Triggers:**
- 3 consecutive correct answers → increase difficulty
- 2 consecutive wrong answers → decrease difficulty
- User can manually override

### 7.3 Recommended Next Activity

**Smart Suggestions Engine:**

```
┌─────────────────────────────────────────────────────────────┐
│  💡 Suggested for you                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "You've studied Photosynthesis for 20 minutes.              │
│   Ready to test your knowledge with a quiz?"                │
│                                                             │
│  [Start Quiz] [Continue Reading] [Create Flashcards]       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Suggestion Logic:**
1. After reading → Suggest quiz
2. After quiz (score >80%) → Suggest next topic
3. After quiz (score <60%) → Suggest review
4. After flashcards → Suggest quiz
5. Long session → Suggest break

### 7.4 Learning Path Suggestions

**Curated Paths:**
```
"Biology Fundamentals"
1. Study Guide: Cell Biology →
2. Q&A: Cell structure questions →
3. Quiz: Cell biology test →
4. Flashcards: Key terms →
5. Mind Map: Connect concepts

Estimated time: 45 minutes
```

**Progress Indicators:**
- Checkmark for completed
- Spinner for in-progress
- Lock for prerequisites

---

## Phase 8: Interaction Design

### 8.1 Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Cmd/Ctrl + K` | Command palette | Global |
| `F` | Toggle focus mode | Global |
| `Esc` | Exit focus mode / close panels | Global |
| `Cmd/Ctrl + Enter` | Submit query | Input focused |
| `Cmd/Ctrl + L` | Toggle context panel | Global |
| `Cmd/Ctrl + B` | Toggle tool rail | Global |
| `Cmd/Ctrl + Shift + Delete` | Clear conversation | Global |
| `?` | Show keyboard help | Global |
| `1-5` | Quick tool group switch | Global |
| `↑ / ↓` | Navigate history | Chat context |
| `Space` | Page down | Reading mode |
| `F` (flashcards) | Flip card | Flashcard mode |
| `K` (flashcards) | Mark known | Flashcard mode |
| `U` (flashcards) | Mark unknown | Flashcard mode |

### 8.2 Command Palette

**Activation:** `Cmd/Ctrl + K`

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Search tools, actions, or history...                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Recent                                                     │
│  ▸ Q&A - Photosynthesis                                      │
│  ▸ Quiz - Cell Biology (score: 85%)                         │
│                                                             │
│  Tools                                                      │
│  Learning ▸ Q&A                                              │
│  Learning ▸ Study Guide                                      │
│  Practice ▸ Quiz                                             │
│  Practice ▸ Flashcards                                       │
│  ...                                                        │
│                                                             │
│  Actions                                                    │
│  ▸ Clear conversation                                        │
│  ▸ Toggle focus mode                                           │
│  ▸ Export chat history                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 Quick Tool Switching

**Method 1: Number Keys**
- `1` → Learning Hub
- `2` → Practice Lab
- `3` → Thinking Studio
- `4` → Visual Studio
- `5` → Career Center

**Method 2: Command Palette**
- Type tool name
- Recent tools prioritized

**Method 3: Sidebar Click**
- Direct navigation
- Visual group indicators

### 8.4 Drag & Drop

**Supported Actions:**
1. Drag citations to notes panel
2. Drag responses to library folders
3. Reorder flashcards in deck
4. Rearrange mind map nodes
5. Move items between folders

**Implementation:**
```typescript
interface DraggableItem {
  id: string;
  type: 'citation' | 'response' | 'flashcard' | 'node';
  data: unknown;
}

const handleDrop = (item: DraggableItem, target: DropZone) => {
  switch (item.type) {
    case 'citation':
      addToNotes(item.data);
      break;
    case 'response':
      saveToLibrary(item.data, target.folder);
      break;
    // ...
  }
};
```

### 8.5 AI Suggestions Panel

**Context-Aware Suggestions:**
```
┌─────────────────────────────────────────────────────────────┐
│  AI Suggestions                                              │
├─────────────────────────────────────────────────────────────┤
│  Based on your question about photosynthesis:                │
│                                                             │
│  🔍 "What is chlorophyll?"                                   │
│  🔍 "Explain the Calvin cycle"                             │
│  🔍 "How does light affect photosynthesis?"                 │
│                                                             │
│  [Ask one of these] [Dismiss]                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 9: Responsive Design

### 9.1 Breakpoint Strategy

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, bottom nav |
| Tablet | 640-1024px | 2-column, collapsible rail |
| Desktop | > 1024px | 3-column full layout |

### 9.2 Mobile Adaptations

**Tool Rail:**
- Collapses to bottom tab bar
- 5 icons (one per group)
- Long-press to see tools in group
- Swipe between groups

**Context Panel:**
- Becomes swipeable drawer
- Pull up from bottom
- Full-screen when opened

**Input Area:**
- Fixed at bottom
- Auto-resize textarea
- Send button always visible

**Focus Mode:**
- Essential for mobile
- Swipe gestures for navigation
- Larger touch targets

### 9.3 Tablet Optimizations

- Collapsed tool rail by default
- Context panel always visible
- Split-view for mind maps
- Touch-optimized controls

### 9.4 Dynamic Layout Adaptations

```typescript
const useResponsiveLayout = () => {
  const [layout, setLayout] = useState('desktop');
  
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width < 640) setLayout('mobile');
      else if (width < 1024) setLayout('tablet');
      else setLayout('desktop');
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return layout;
};
```

---

## Phase 10: Implementation

### 10.1 Component Structure

```
frontend/src/app/student/ai-studio/
├── page.tsx                    # Main page component
├── layout.tsx                  # Layout wrapper
├── ai-studio.css               # Layout-specific styles
├── REDESIGN_PLAN.md            # This document
├── components/
│   ├── ToolRail.tsx            # Left sidebar navigation
│   ├── ContextPanel.tsx         # Right sidebar panel
│   ├── LearningWorkspace.tsx    # Central chat area
│   ├── ActionBar.tsx            # Post-response actions
│   ├── ResponseCard.tsx         # Enhanced response display
│   ├── FocusMode.tsx            # Distraction-free overlay
│   ├── SmartSuggestions.tsx     # AI recommendations
│   ├── ProgressTracker.tsx      # Study session stats
│   └── ToolViews/
│       ├── QuizView.tsx         # Interactive quiz
│       ├── FlashcardDeck.tsx    # Swipeable cards
│       ├── MindMapCanvas.tsx    # SVG mind map
│       ├── FlowchartRenderer.tsx # Mermaid diagrams
│       └── ConceptGraph.tsx     # Network visualization
├── hooks/
│   ├── useKeyboardShortcuts.ts  # Keyboard shortcut system
│   ├── useFocusMode.ts          # Focus mode state
│   └── useStudySession.ts       # Session tracking
└── types/
    └── ai-studio.ts             # TypeScript definitions
```

### 10.2 Animation Implementation

**Library:** Framer Motion

```typescript
// Tool switching animation
const toolVariants = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 }
};

<AnimatePresence mode="wait">
  <motion.div
    key={activeTool}
    variants={toolVariants}
    initial="hidden"
    animate="visible"
    exit="exit"
    transition={{ duration: 0.3 }}
  >
    {/* Tool content */}
  </motion.div>
</AnimatePresence>
```

### 10.3 Dependencies

```json
{
  "dependencies": {
    "framer-motion": "^11.0.0",
    "d3": "^7.8.5",
    "mermaid": "^10.6.1",
    "cmdk": "^0.2.0",
    "@use-gesture/react": "^10.3.0"
  }
}
```

### 10.4 Implementation Timeline

| Sprint | Duration | Deliverables |
|--------|----------|--------------|
| Sprint 1 | Week 1 | Layout shell, ToolRail, ContextPanel |
| Sprint 2 | Week 1-2 | LearningWorkspace, ActionBar, FocusMode |
| Sprint 3 | Week 2-3 | ToolViews (Quiz, Flashcards, MindMap) |
| Sprint 4 | Week 3-4 | Smart features, keyboard shortcuts, polish |
| Sprint 5 | Week 4 | Testing, bug fixes, performance |

### 10.5 Success Metrics

**User Experience:**
- Time to complete task reduced by 30%
- User satisfaction score > 4.5/5
- Support tickets reduced by 40%

**Engagement:**
- Session duration increased by 25%
- Tool switching frequency increased (good sign)
- Return visit rate increased by 20%

**Performance:**
- First contentful paint < 1.5s
- Time to interactive < 3s
- Animation frame rate maintained at 60fps

---

## Appendix A: Design Principles

1. **Progressive Disclosure**: Show only what's needed, reveal more on demand
2. **Consistent Metaphors**: Same interaction patterns across tools
3. **Immediate Feedback**: Every action has visible result
4. **Forgiving**: Easy to undo, hard to lose work
5. **Accessible**: WCAG 2.1 AA compliance minimum

## Appendix B: Accessibility Checklist

- [ ] Keyboard navigation for all features
- [ ] Screen reader announcements for dynamic content
- [ ] Color contrast ratio ≥ 4.5:1 for text
- [ ] Focus indicators visible
- [ ] Reduced motion support
- [ ] Text resize up to 200% without breaking

## Appendix C: Testing Plan

**Unit Tests:**
- Component rendering
- Hook behavior
- Utility functions

**Integration Tests:**
- Tool switching
- Data flow between components
- Keyboard shortcuts

**E2E Tests:**
- Complete user flows
- Cross-browser compatibility
- Mobile responsiveness

**User Testing:**
- 5 students, 2 teachers
- Task-based evaluation
- A/B testing old vs new design

---

*Document Version: 1.0*
*Last Updated: March 27, 2026*
*Status: Ready for Implementation*
