# Animation Patterns — Code Snippets

Copy-paste these into `make_frame(t)` as needed.

---

## Moving Dot (single — slow/lagging)
```python
# One dot, slow — shows lagging/reactive behavior
moving_dot(ax, x1, x2, y=AY, color=RED, t=t, speed=0.5, offset=0.0, ms=9)
# Trail included automatically in moving_dot()
```

## Moving Dots (triple — fast/proactive)
```python
# Three dots offset — shows instant/parallel behavior
for off in [0.0, 0.28, 0.56]:
    moving_dot(ax, x1, x2, y=BY, color=GREEN, t=t, speed=1.4, offset=off, ms=7)
```

---

## Animated Dashes on Arrow

```python
# Slow (lagging): 1.5s cycle
draw_dash_anim(ax, x1, x2, y, AMBER, t, fast=False, offset=i*0.3)

# Fast (instant): 0.35s cycle
draw_dash_anim(ax, x1, x2, y, GREEN, t, fast=True, offset=i*0.15)
```

---

## Fill Bar (CPU / Queue / Load)

```python
# Animates width with sin wave — goes up and down
fill_bar(ax, cx=node_x, cy=AY-0.45, w=1.6, h=0.18,
         color=RED, t=t, speed=1.2)

# Show percentage label below bar
pct = int(abs(np.sin(t * np.pi * 1.2)) * 75 + 20)
ax.text(node_x, AY-0.72, f'CPU: {pct}%',
        ha='center', va='center', fontsize=7.5, color=AMBER, zorder=8)
```

## Queue Depth Counter
```python
count = int(abs(np.sin(t * np.pi * 0.9)) * 480 + 20)
ax.text(node_x, BY-0.65, f'{count} msgs',
        ha='center', va='center', fontsize=8, color=BLUE,
        fontweight='bold', zorder=8)
```

---

## Pulse Ring (controller reacting)

```python
# Slow pulse — HPA polling feel
pulse_ring(ax, cx=node_x, cy=AY, color=AMBER, t=t, speed=1.5)

# Fast pulse — KEDA instant react feel
pulse_ring(ax, cx=node_x, cy=BY, color=GREEN, t=t, speed=2.5)
```

---

## Clock Hand (15s delay indicator)

```python
# Draw clock face
clock_cx, clock_cy = arrow_mid_x, AY - 0.55
ax.add_patch(plt.Circle((clock_cx, clock_cy), 0.28,
             color=AMBER, fill=False, lw=1.5, alpha=0.8, zorder=5))

# Minute hand (fast)
angle = t * 2 * np.pi * 2   # 2 full rotations per cycle
hx = clock_cx + 0.18 * np.sin(angle)
hy = clock_cy + 0.18 * np.cos(angle)
ax.plot([clock_cx, hx], [clock_cy, hy],
        color=AMBER, lw=1.5, zorder=6, alpha=0.9)

# Label
ax.text(clock_cx, clock_cy - 0.45, '⏱ 15s POLL',
        ha='center', va='center', fontsize=8,
        color=AMBER, fontweight='bold', zorder=6)
```

---

## "INSTANT" Badge (on arrow)

```python
# Blinks to show instant reaction
alpha = 0.4 + 0.6 * abs(np.sin(t * np.pi * 3))
ax.text(arrow_mid_x, BY + 0.42, '⚡ INSTANT',
        ha='center', va='center', fontsize=8.5,
        fontweight='bold', color=GREEN, alpha=alpha,
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#0a1f0a',
                  edgecolor=GREEN, linewidth=0.8, alpha=0.7),
        zorder=6)
```

---

## "TOO LATE" Badge (on output node)

```python
# Appears when CPU is high — fades in/out
badge_alpha = max(0, abs(np.sin(t * np.pi * 1.0)) - 0.2)
ax.text(node_x + 1.2, AY + 0.65, 'TOO LATE ⚠',
        ha='center', va='center', fontsize=8,
        fontweight='bold', color=WHITE, alpha=badge_alpha,
        bbox=dict(boxstyle='round,pad=0.25', facecolor=RED,
                  edgecolor='none', alpha=badge_alpha * 0.9),
        zorder=8)
```

---

## Scale-to-Zero (pods disappear at night)

```python
# Show "3AM moon" icon that fades in when pods fade out
moon_alpha = abs(np.sin(t * np.pi * 0.7 + np.pi/2))
ax.text(node_x + 0.8, BY + 0.55, '🌙 3AM\n0 pods',
        ha='center', va='center', fontsize=8,
        color=PURPLE, alpha=moon_alpha, zorder=7,
        multialignment='center', fontweight='bold')

# Pods fade out
pod_alpha = 1 - moon_alpha * 0.85
# Apply alpha to pod drawing
```

---

## Event Pills (flashing event sources)

```python
# Kafka, SQS, HTTP etc — flash one by one
sources = ['Kafka', 'SQS', 'RabbitMQ', 'HTTP']
pill_x_start = node_x - 0.85
for idx, src in enumerate(sources):
    delay = idx * 0.25
    pill_alpha = 0.3 + 0.7 * abs(np.sin((t + delay) * np.pi * 2))
    ax.text(pill_x_start + idx * 0.52, BY + 0.52, src,
            ha='center', va='center', fontsize=7,
            fontweight='bold', color=GREEN, alpha=pill_alpha,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#0a1f0a',
                      edgecolor=GREEN, linewidth=0.6, alpha=0.7),
            zorder=6)
```

---

## Background Danger Flash (section A)

```python
# Section A background flashes dark-red when CPU spikes
cpu_level = abs(np.sin(t * np.pi * 1.2))
flash_alpha = max(0, cpu_level - 0.5) * 0.15
pa = FancyBboxPatch((0.2, 4.55), 15.6, 3.85,
                    boxstyle="round,pad=0.05",
                    facecolor=RED, edgecolor='none',
                    alpha=0.04 + flash_alpha, zorder=1)
ax.add_patch(pa)
```

---

## Numbered Step Badges

```python
steps = [1.6, 5.0, 9.0, 13.0]   # same as node x positions
for i, sx in enumerate(steps):
    ax.text(sx, AY + 0.75, str(i+1),
            ha='center', va='center', fontsize=9,
            fontweight='bold', color=RED, zorder=7,
            bbox=dict(boxstyle='circle,pad=0.3',
                      facecolor='#1a0808', edgecolor=RED,
                      linewidth=1.2, alpha=0.85))
```

---

## Animated Queue Bars (multi-row)

```python
bar_heights = [0.12, 0.12, 0.12]
bar_colors  = [0.0, 0.35, 0.7]   # staggered offsets
for bi, (bh, off) in enumerate(zip(bar_heights, bar_colors)):
    by_pos = node_y - 0.25 + bi * (bh + 0.04)
    fill_w = 1.5 * abs(np.sin((t + off) * np.pi * 0.9))
    # background
    ax.add_patch(mpatches.Rectangle(
        (node_x - 0.75, by_pos), 1.5, bh, color=DGRAY, alpha=0.8, zorder=5))
    # fill
    ax.add_patch(mpatches.Rectangle(
        (node_x - 0.75, by_pos), fill_w, bh,
        color=BLUE, alpha=0.85, zorder=6))
```
