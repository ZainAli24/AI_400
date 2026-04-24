---
name: gif-flow-creator
description: |
  Creates professional animated .gif files that visually explain any technical concept,
  flow process, or comparison — using Python matplotlib + Pillow (no browser needed).
  This skill should be used whenever the user asks to create an animated GIF, wants to
  visually explain a concept, flow, or comparison for a LinkedIn post or any content,
  regardless of topic (AI, DevOps, Cloud, Databases, Networking, System Design, etc.).
  Automatically detects whether content needs a single-flow or comparison layout.
---

# Animated GIF Flow Creator

Turns any topic/content/post into a professional animated .gif with moving dots,
pulsing effects, fill bars, and clear visual storytelling.

**Requirements** (standard, usually already installed):
```bash
pip install matplotlib pillow
```

---

## Step 1 — Analyze Content

Read user's content/post carefully and determine:

### A) Layout Type

| Type | When to use | Example |
|------|-------------|---------|
| **Comparison** | Two concepts being contrasted | HPA vs KEDA, SQL vs NoSQL, REST vs GraphQL |
| **Single Flow** | One process/pipeline being explained | How Kafka works, CI/CD pipeline, RAG flow |
| **Multi-step** | Sequential stages with outcomes | Model training pipeline, Auth flow |

### B) Extract Nodes (per flow/section)

For each section extract **3–5 nodes**:
- `label` — short title (1–2 words)
- `sublabel` — one-line description
- `color_mood` — see Color Schemes below
- `animation` — what animates inside this node

### C) Identify Key Contrast (for Comparison type)

What makes the two sides VISUALLY OPPOSITE?
- Speed difference? → slow vs fast arrows
- Reactive vs proactive? → delayed vs instant animations
- Cost difference? → show cost indicator
- Always-on vs zero? → show scale-to-zero

---

## Step 2 — Design Decisions

### Color Schemes

| Mood | Primary | Use when |
|------|---------|----------|
| Danger / Warning / Slow | `#f85149` red + `#d29922` amber | Lagging, reactive, problematic |
| Success / Fast / Efficient | `#2ea043` green + `#56d364` light-green | Proactive, instant, good |
| Neutral / Info | `#58a6ff` blue + `#388bfd` | Informational, neutral steps |
| Premium / Smart | `#a855f7` purple + `#c084fc` | AI, intelligent, advanced |
| Energy / Highlight | `#ff7b00` orange | Traffic, load, requests |

Full palette always available in `references/color-schemes.md`.

### Arrow Speed Convention

| Concept | Speed | Animation duration |
|---------|-------|--------------------|
| Slow / lagging / delayed | Slow dots (1 dot) | `1.5s` dash cycle |
| Normal flow | Medium dots (1–2) | `0.8s` dash cycle |
| Fast / instant / proactive | Fast dots (3 dots, offset) | `0.3s` dash cycle |

### Section Background

- Comparison Section A (warning): dark red tint `#120a0a`, border red
- Comparison Section B (success): dark green tint `#091510`, border green
- Single flow: neutral dark `#0d1117`

---

## Step 3 — Write the Python Script

**Always use** `references/base-template.py` as starting point.

Customize these parts:

```python
# ── 1. Output path
OUTPUT = "E:/AI_400/<topic-slug>-flow.gif"

# ── 2. Title & subtitle
TITLE    = "Your Main Title Here"
SUBTITLE = "Section A Label  vs  Section B Label"   # or single description

# ── 3. Node definitions per section
# Each node: (center_x, label, sublabel, color)
section_a_nodes = [
    (1.6,  "Node 1", "description", RED),
    (4.8,  "Node 2", "description", AMBER),
    (8.0,  "Node 3", "description", GREEN),
]

# ── 4. Animation per node (customize inside make_frame)
# - Fill bar: abs(sin(t * pi * speed))
# - Moving dot: index path by t * speed % 1
# - Pulse ring: plt.Circle with shrinking alpha
# - Fade in/out node: alpha driven by sin wave

# ── 5. Arrow labels & speeds
# section_a → slow arrows (1.5s), section_b → fast (0.35s)

# ── 6. Notice bar text per section
NOTICE_A = "Key insight about Section A behavior"
NOTICE_B = "Key insight about Section B behavior"

# ── 7. Comparison cards (bottom)
CARD_A_POINTS = ["Point 1", "Point 2", "Point 3"]
CARD_B_POINTS = ["Point 1", "Point 2", "Point 3"]
```

See `references/animation-patterns.md` for all animation code snippets.

---

## Step 4 — Run Script

```bash
python E:/AI_400/<script-name>.py
```

Expected output:
```
Generating 120 frames...
  [120/120] done
Assembling GIF -> E:/AI_400/<topic>-flow.gif
Done! 120 frames | (1400x900) px | ~5 MB
```

---

## Step 5 — Deliver

Report to user:
- GIF file path
- What each animation represents conceptually
- Frame count, size, loop duration

---

## Branding Rules (ALWAYS)

- **"Zain Ali"** — bottom-right corner, every GIF, no exceptions
- Font: italic, `#58a6ff` blue, with thin separator line above
- Style: same as ByteByteGo branding on their diagrams

---

## Quick Decision Tree

```
User gives content/post
        ↓
Two concepts contrasted? ──YES──→ Comparison layout (2 sections)
        ↓NO
One process explained?   ──YES──→ Single-flow layout (1 section, 4-5 steps)
        ↓NO
Multiple stages?         ──YES──→ Multi-step layout (vertical or horizontal)
```

---

## Reference Files

| File | Load when |
|------|-----------|
| `references/base-template.py` | Always — starting point for every GIF script |
| `references/animation-patterns.md` | Need specific animation code snippet |
| `references/color-schemes.md` | Need full color palette details |
| `references/layout-examples.md` | Need layout code for single-flow or multi-step |
