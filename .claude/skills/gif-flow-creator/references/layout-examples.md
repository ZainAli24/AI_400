# Layout Examples

## Layout 1 — Comparison (2 sections, most common)

Use when: Two concepts being contrasted (A vs B).

```
┌─────────────────────────────────────────────────────────────┐
│  [chip]        Main Title                                   │
│           Subtitle A  vs  Subtitle B                        │
├──────────────────── SECTION A (y: 4.6–8.5) ────────────────┤
│  ⚠ Section A Label                                          │
│  [Step1]─slow─►[Step2]─slow─►[Step3]─slow─►[Step4]         │
│  ⚠️  REACTIVE notice bar                                    │
├──────────────────── SECTION B (y: 0.4–4.4) ────────────────┤
│  ⚡ Section B Label                                          │
│  [Step1]═fast═►[Step2]═fast═►[Step3]═fast═►[Step4]         │
│  ✅  PROACTIVE notice bar                                    │
├─────────────────────────────────────────────────────────────┤
│  [Card A: Use when...]    [Card B: Use when...]             │
│  Tags                                        Zain Ali       │
└─────────────────────────────────────────────────────────────┘

Y centers:  Section A nodes = 6.5,  Section B nodes = 2.5
```

**Vertical zones (ylim 0–9):**
```
8.8–9.0  : title
8.3–8.6  : subtitle
8.0–8.2  : section A label
7.8–8.0  : (section A header space)
5.8–7.2  : section A nodes (cy=6.5, box h=1.0)
4.62–5.24: section A notice bar
4.5      : divider line
4.2–4.4  : section B label
1.8–3.2  : section B nodes (cy=2.5, box h=1.0)
0.45–1.07: section B notice bar
0.18     : tags + branding
```

---

## Layout 2 — Single Flow (1 section, 4–5 steps)

Use when: One process/pipeline being explained step by step.

```
┌─────────────────────────────────────────────────────────────┐
│  [chip]        Main Title                                   │
│           How [Topic] Works                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① [Step1] ──► ② [Step2] ──► ③ [Step3] ──► ④ [Step4]      │
│                                                             │
│  Key insight notice bar                                     │
├─────────────────────────────────────────────────────────────┤
│  [Detail box 1]          [Detail box 2]                     │
│  Tags                                        Zain Ali       │
└─────────────────────────────────────────────────────────────┘

Y center for nodes: 5.0  (mid of canvas)
```

**Code setup for single flow:**
```python
# No section panels, single flow at y=5.0
FLOW_Y = 5.0
NODES = [
    (1.5,  "Step 1", "description", BLUE),
    (4.8,  "Step 2", "description", ORANGE),
    (8.1,  "Step 3", "description", PURPLE),
    (11.4, "Step 4", "description", GREEN),
    (14.5, "Step 5", "description", TEAL),
]
ARROW_LABELS = ["label", "label", "label", "label"]

# Single flow uses BLUE arrows at medium speed
for i in range(len(NODES) - 1):
    x1 = NODES[i][0] + BOX_W/2 + 0.1
    x2 = NODES[i+1][0] - BOX_W/2 - 0.1
    draw_dash_anim(ax, x1, x2, FLOW_Y, BLUE, t, fast=False, offset=i*0.25)
    draw_arrow(ax, x1, x2, FLOW_Y, BLUE, label=ARROW_LABELS[i])
    moving_dot(ax, x1, x2, FLOW_Y, BLUE, t, speed=0.8, offset=i*0.25)
```

---

## Layout 3 — Multi-Step Vertical (pipeline stages)

Use when: Sequential stages with sub-steps (e.g. ML training pipeline).

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Stage 1  │ ──► │ Stage 2  │ ──► │ Stage 3  │ ──► │ Stage 4  │
│ substep  │     │ substep  │     │ substep  │     │ substep  │
│ substep  │     │ substep  │     │ substep  │     │ substep  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

Use single-flow layout code but make boxes taller (BOX_H=1.8) and add sub-items inside.

---

## Node X Position Guide

### 3 nodes across 16-unit canvas:
```python
xs = [2.5, 8.0, 13.5]
```

### 4 nodes:
```python
xs = [1.8, 5.8, 9.8, 13.8]
```

### 5 nodes:
```python
xs = [1.5, 4.5, 7.5, 10.5, 13.5]    # tight
xs = [1.2, 4.0, 7.0, 10.0, 13.5]    # with room
```

---

## Box Size Guide

| Content | Width | Height |
|---------|-------|--------|
| Simple label + sublabel | 2.0 | 0.9 |
| Label + sublabel + pill | 2.2 | 1.1 |
| Label + bar + value | 2.2 | 1.2 |
| Label + multiple items | 2.4 | 1.4 |

Arrow gap from box edge: `BOX_W / 2 + 0.08`

---

## Notice Bar Positions

```python
# Section A notice (just above divider)
notice_bar(ax, x=0.3, y=4.62, w=15.4, h=0.62, ...)

# Section B notice (above tags)
notice_bar(ax, x=0.3, y=0.45, w=15.4, h=0.62, ...)

# Single flow notice (below flow)
notice_bar(ax, x=0.3, y=3.2,  w=15.4, h=0.62, ...)
```

---

## Comparison Cards (optional, replaces notice bars)

Use when you want "Use X when" cards at the bottom:

```python
# Left card (Section A)
ca_bg = FancyBboxPatch((0.3, 0.42), 7.5, 1.8, ...)
ax.add_patch(ca_bg)
ax.text(0.9, 2.1, 'Use A when', fontsize=11, color=RED, fontweight='bold')
for i, pt in enumerate(CARD_A_POINTS):
    ax.text(1.0, 1.85 - i*0.35, f'• {pt}', fontsize=9, color=LGRAY)

# Right card (Section B)
cb_bg = FancyBboxPatch((8.2, 0.42), 7.5, 1.8, ...)
ax.add_patch(cb_bg)
ax.text(8.8, 2.1, 'Use B when', fontsize=11, color=GREEN, fontweight='bold')
for i, pt in enumerate(CARD_B_POINTS):
    ax.text(8.9, 1.85 - i*0.35, f'• {pt}', fontsize=9, color=LGRAY)
```
