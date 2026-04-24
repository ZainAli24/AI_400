# Color Schemes

## Base Palette (always available)

```python
BG     = '#0B0F1E'   # background — deep navy
RED    = '#FF4757'   # danger, error, reactive, slow
AMBER  = '#d29922'   # warning, delay, polling
GREEN  = '#2ECC71'   # success, proactive, efficient
BLUE   = '#4A9EFF'   # info, neutral, input/source
PURPLE = '#A855F7'   # AI, intelligent, scale-to-zero
ORANGE = '#FFA502'   # traffic, load, requests, energy
TEAL   = '#00CED1'   # branding (Zain Ali), highlight
WHITE  = '#FFFFFF'
LGRAY  = '#94A3B8'   # subtitles, labels
DGRAY  = '#1E2D40'   # bar backgrounds, tracks
```

---

## Concept → Color Mapping

| Concept | Primary | Secondary | Use |
|---------|---------|-----------|-----|
| Slow / Lagging / Reactive | `RED` | `AMBER` | HPA, polling, delay |
| Fast / Instant / Proactive | `GREEN` | `#56d364` | KEDA, instant, efficient |
| Traffic / Load / Requests | `ORANGE` | `#ffb347` | Incoming requests, load |
| AI / Intelligence / Smart | `PURPLE` | `#c084fc` | LLMs, embeddings, models |
| Data / Storage / DB | `BLUE` | `#388bfd` | Databases, queues, storage |
| Cost / Money / Zero | `PURPLE` | `#a371f7` | Scale-to-zero, savings |
| Error / Failure | `RED` | `#ff6b6b` | Errors, failures, timeouts |
| Success / Healthy | `GREEN` | `#2ea043` | Healthy state, success |
| Neutral / Step | `LGRAY` | `#8b949e` | Middle steps, connectors |

---

## Section Themes

### Comparison — Section A (warning/problematic side)
```python
SECTION_A_BG     = '#120a0a'   # dark red tint
SECTION_A_BORDER = '#f8514940' # red border (40% opacity)
SECTION_A_LABEL  = '#f85149'   # label text color
SECTION_A_ARROW  = AMBER       # arrow color
```

### Comparison — Section B (success/efficient side)
```python
SECTION_B_BG     = '#091510'   # dark green tint
SECTION_B_BORDER = '#2ea04360' # green border (60% opacity)
SECTION_B_LABEL  = '#56d364'   # label text color
SECTION_B_ARROW  = GREEN       # arrow color
```

### Single Flow (neutral)
```python
SECTION_BG     = '#0d1117'
SECTION_BORDER = '#30363d'
SECTION_LABEL  = BLUE
SECTION_ARROW  = BLUE
```

---

## Topic-Specific Schemes

### DevOps / Kubernetes / Cloud
- Section A (HPA/traditional): RED + AMBER
- Section B (KEDA/modern): GREEN + BLUE

### AI / Machine Learning
- Input/Data: BLUE
- Processing/Model: PURPLE
- Output/Result: GREEN
- Error/Hallucination: RED

### Databases
- SQL/Traditional: AMBER + BLUE
- NoSQL/Modern: GREEN + TEAL
- Cache: ORANGE
- Index: PURPLE

### Networking / APIs
- Client: BLUE
- Server: GREEN
- Load Balancer: ORANGE
- Cache/CDN: TEAL
- Error: RED

### Security / Auth
- Unauthenticated: RED
- Processing/Verification: AMBER
- Authenticated: GREEN
- Token/Key: PURPLE

### CI/CD Pipeline
- Source/Code: BLUE
- Build: AMBER
- Test: ORANGE
- Deploy: GREEN
- Rollback: RED

---

## Glow Intensity Guide

```python
# Strong glow — key/important node (controller, decision point)
glow=True    # in draw_box()

# No glow — supporting nodes (input, output)
glow=False

# Pulse ring — active processing node
pulse_ring(ax, cx, cy, color, t, speed=2.0)
```

---

## Background Panel Alpha

```python
# Subtle section tint (don't overpower content)
facecolor=RED,   alpha=0.04   # section A
facecolor=GREEN, alpha=0.04   # section B

# Danger flash (animated — when something goes wrong)
alpha = 0.04 + flash_intensity * 0.12   # max 0.16
```
