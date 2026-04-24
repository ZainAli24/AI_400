"""
GIF Flow Creator — Base Template
=================================
Copy this file, rename it, and customize the sections marked with
# ── CUSTOMIZE ── comments. Everything else is reusable boilerplate.

Usage:
    python <your-script>.py
Output:
    E:/AI_400/<topic>-flow.gif
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from PIL import Image
import io, os

# ════════════════════════════════════════════════════════════════
# ── CUSTOMIZE: Colors
# ════════════════════════════════════════════════════════════════
BG      = '#0B0F1E'
RED     = '#FF4757'
AMBER   = '#d29922'
GREEN   = '#2ECC71'
BLUE    = '#4A9EFF'
PURPLE  = '#A855F7'
ORANGE  = '#FFA502'
TEAL    = '#00CED1'
WHITE   = '#FFFFFF'
LGRAY   = '#94A3B8'
DGRAY   = '#1E2D40'

# ════════════════════════════════════════════════════════════════
# ── CUSTOMIZE: GIF settings
# ════════════════════════════════════════════════════════════════
OUTPUT        = "E:/AI_400/topic-flow.gif"   # ← change topic name
FIG_W, FIG_H  = 16, 9
DPI           = 120
N_FRAMES      = 120                          # 120 = ~6s at 20fps
FRAME_DUR_MS  = 50                           # 50ms = 20fps

# ════════════════════════════════════════════════════════════════
# ── CUSTOMIZE: Content
# ════════════════════════════════════════════════════════════════
TITLE    = "Your Title Here"
SUBTITLE_A = "Section A — Label"         # red/warning side
SUBTITLE_B = "Section B — Label"         # green/success side

# Nodes: (center_x, label, sublabel, color)
# Use 3–5 nodes per section. x values: spread between 1.5 and 13.5
SEC_A_NODES = [
    (1.6,  "Node 1",  "sub description",  BLUE),
    (5.0,  "Node 2",  "sub description",  AMBER),
    (9.0,  "Node 3",  "sub description",  RED),
    (13.0, "Node 4",  "sub description",  GREEN),
]
SEC_B_NODES = [
    (1.6,  "Node 1",  "sub description",  BLUE),
    (5.0,  "Node 2",  "sub description",  GREEN),
    (9.0,  "Node 3",  "sub description",  GREEN),
    (13.0, "Node 4",  "sub description",  PURPLE),
]

# Arrow labels between nodes (len = nodes - 1)
SEC_A_ARROW_LABELS = ["step label", "step label", "step label"]
SEC_B_ARROW_LABELS = ["step label", "step label", "step label"]

# Notice bars
NOTICE_A = "Key insight about Section A — what makes it different / limited"
NOTICE_B = "Key insight about Section B — what makes it better / special"

# Comparison cards
CARD_A_TITLE  = "Use Section A when"
CARD_B_TITLE  = "Use Section B when"
CARD_A_POINTS = ["Scenario 1", "Scenario 2", "Scenario 3"]
CARD_B_POINTS = ["Scenario 1", "Scenario 2", "Scenario 3"]

# Tags
TAGS = "#Tag1  #Tag2  #Tag3  #Tag4  #Tag5"

# ════════════════════════════════════════════════════════════════
# HELPERS — do not need to change these
# ════════════════════════════════════════════════════════════════

def draw_box(ax, cx, cy, w, h, color, label, sublabel='', glow=False, zorder=3):
    """Draw a rounded, glowing box with label and optional sublabel."""
    if glow:
        for r in [1.8, 1.3]:
            halo = FancyBboxPatch(
                (cx - w/2 - 0.05*r, cy - h/2 - 0.05*r),
                w + 0.10*r, h + 0.10*r,
                boxstyle="round,pad=0.04", facecolor='none',
                edgecolor=color, linewidth=2.5*r, alpha=0.07, zorder=zorder-1)
            ax.add_patch(halo)
    fill = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.04", facecolor=color,
        edgecolor='none', alpha=0.13, zorder=zorder)
    ax.add_patch(fill)
    border = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.04", facecolor='none',
        edgecolor=color, linewidth=2.0, alpha=0.9, zorder=zorder+1)
    ax.add_patch(border)
    y_lbl = cy + (0.15 if sublabel else 0)
    ax.text(cx, y_lbl, label, ha='center', va='center',
            fontsize=10, fontweight='bold', color=WHITE, zorder=zorder+2,
            multialignment='center')
    if sublabel:
        ax.text(cx, cy - 0.28, sublabel, ha='center', va='center',
                fontsize=7.5, color=color, alpha=0.9, zorder=zorder+2)


def draw_arrow(ax, x1, x2, y, color, label='', fast=False, alpha=0.6):
    """Draw animated dashed arrow between two x positions."""
    # static line (arrow body drawn in make_frame via dash animation)
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
        arrowprops=dict(arrowstyle='-|>', color=color, lw=1.5,
                        alpha=alpha*0.7, mutation_scale=12))
    if label:
        lx = (x1 + x2) / 2
        ax.text(lx, y + 0.35, label, ha='center', va='center',
                fontsize=8.5, color=color, fontweight='bold', zorder=5)


def draw_dash_anim(ax, x1, x2, y, color, t, fast=False, offset=0.0):
    """Draw an animated dashed line at time t."""
    speed   = 0.35 if fast else 1.5
    seg_len = 10 if fast else 18
    gap_len = 12 if fast else 18
    period  = seg_len + gap_len
    shift   = ((t + offset) * period / speed) % period
    xx = np.arange(x1 * 100, x2 * 100, 1) / 100.0
    for x in xx:
        rel = ((x - x1) * 100 + shift) % period
        if rel < seg_len:
            ax.plot(x, y, '.', color=color, ms=2.5,
                    alpha=0.85, zorder=4, markeredgewidth=0)


def moving_dot(ax, x1, x2, y, color, t, speed=1.0, offset=0.0, ms=9):
    """Draw a moving dot from x1 to x2 at normalized time t."""
    pos = ((t * speed + offset) % 1.0)
    dx  = x1 + pos * (x2 - x1)
    ax.plot(dx, y, 'o', color=color, ms=ms, zorder=8,
            markeredgecolor=WHITE, markeredgewidth=0.8, alpha=0.95)
    # trail
    for i in range(1, 3):
        tpos = ((t * speed + offset - i * 0.04) % 1.0)
        tdx  = x1 + tpos * (x2 - x1)
        ax.plot(tdx, y, 'o', color=color,
                ms=ms - 2*i, alpha=0.2, zorder=7)


def pulse_ring(ax, cx, cy, color, t, speed=2.0):
    """Expanding ring pulse effect."""
    phase = (t * speed) % 1.0
    for scale in [1.0, 0.6]:
        p = (phase * scale) % 1.0
        r = 0.55 * p
        a = 0.25 * (1 - p)
        ring = plt.Circle((cx, cy), r, color=color,
                           fill=False, lw=2.0, alpha=a, zorder=2)
        ax.add_patch(ring)


def fill_bar(ax, cx, cy, w, h, color, t, speed=1.5, bg_color=DGRAY):
    """Animated fill bar (e.g. CPU usage)."""
    fill_w = w * abs(np.sin(t * np.pi * speed))
    bg = mpatches.Rectangle((cx - w/2, cy - h/2), w, h,
                              color=bg_color, alpha=0.8, zorder=5)
    bar = mpatches.Rectangle((cx - w/2, cy - h/2), fill_w, h,
                               color=color, alpha=0.9, zorder=6)
    ax.add_patch(bg)
    ax.add_patch(bar)


def section_label(ax, x, y, text, color, icon=''):
    """Section header badge."""
    ax.text(x, y, f"{icon} {text}",
            ha='left', va='center', fontsize=10.5,
            fontweight='bold', color=color, alpha=0.95, zorder=6)


def notice_bar(ax, x, y, w, h, color, icon, strong_text, body_text):
    """Bottom notice bar for a section."""
    bg = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                         facecolor=color, edgecolor=color,
                         linewidth=0.8, alpha=0.08, zorder=3)
    bd = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                         facecolor='none', edgecolor=color,
                         linewidth=0.8, alpha=0.3, zorder=3)
    ax.add_patch(bg)
    ax.add_patch(bd)
    ax.text(x + 0.3, y + h/2, icon, ha='left', va='center',
            fontsize=14, zorder=5)
    ax.text(x + 0.85, y + h/2 + 0.12, strong_text,
            ha='left', va='center', fontsize=9.5,
            fontweight='bold', color=color, zorder=5)
    ax.text(x + 0.85, y + h/2 - 0.18, body_text,
            ha='left', va='center', fontsize=8,
            color=LGRAY, zorder=5)


def step_badge(ax, cx, cy, color):
    """Numbered step circle above a node."""
    # Called externally — just draws the circle
    circle = plt.Circle((cx, cy), 0.22, color=color,
                         fill=False, lw=1.5, alpha=0.8, zorder=6)
    ax.add_patch(circle)


# ════════════════════════════════════════════════════════════════
# FRAME GENERATOR — customize animations inside here
# ════════════════════════════════════════════════════════════════

def make_frame(t):
    """Generate one frame. t in [0, 1)."""
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # ── Background panels
    # Section A (top, y: 4.6 to 8.5) — warning tint
    pa = FancyBboxPatch((0.2, 4.55), 15.6, 3.85, boxstyle="round,pad=0.05",
                         facecolor=RED, edgecolor=RED, linewidth=0, alpha=0.04, zorder=1)
    # Section B (bottom, y: 0.4 to 4.4) — success tint
    pb = FancyBboxPatch((0.2, 0.4), 15.6, 4.0, boxstyle="round,pad=0.05",
                         facecolor=GREEN, edgecolor=GREEN, linewidth=0, alpha=0.04, zorder=1)
    ax.add_patch(pa)
    ax.add_patch(pb)

    # ── Divider
    ax.plot([0.4, 15.6], [4.5, 4.5], color=LGRAY, lw=0.7, alpha=0.25)

    # ── Title
    ax.text(8.0, 8.65, TITLE,
            ha='center', va='center', fontsize=20, fontweight='bold',
            color=WHITE, zorder=6)
    ax.text(8.0, 8.32,
            f"{SUBTITLE_A}   vs   {SUBTITLE_B}",
            ha='center', va='center', fontsize=10.5, color=LGRAY, zorder=6)

    # ── Branding (ALWAYS)
    ax.text(15.75, 0.22, 'Zain Ali',
            ha='right', va='center', fontsize=11,
            color=TEAL, alpha=0.95, zorder=10,
            fontweight='bold', style='italic')
    ax.plot([14.3, 15.75], [0.32, 0.32], color=TEAL, lw=0.8, alpha=0.45, zorder=9)

    # ── Section A header
    section_label(ax, 0.5, 8.05, SUBTITLE_A, RED, icon='⚠')

    # ── Section B header
    section_label(ax, 0.5, 4.2, SUBTITLE_B, GREEN, icon='⚡')

    # ════════════════════════════════
    # SECTION A FLOW  (y center = 6.5)
    # ════════════════════════════════
    AY = 6.5   # vertical center for section A nodes
    BOX_W, BOX_H = 2.2, 1.0

    # Draw nodes
    for i, (nx, lbl, sub, col) in enumerate(SEC_A_NODES):
        draw_box(ax, nx, AY, BOX_W, BOX_H, col, lbl, sub,
                 glow=(col in [RED, AMBER]))

    # Draw arrows between nodes (SLOW for section A)
    gap = BOX_W / 2 + 0.08
    for i in range(len(SEC_A_NODES) - 1):
        x1 = SEC_A_NODES[i][0] + gap
        x2 = SEC_A_NODES[i+1][0] - gap
        albl = SEC_A_ARROW_LABELS[i] if i < len(SEC_A_ARROW_LABELS) else ''
        draw_dash_anim(ax, x1, x2, AY, AMBER, t, fast=False, offset=i*0.3)
        draw_arrow(ax, x1, x2, AY, AMBER, label=albl, fast=False)
        # Single slow dot
        moving_dot(ax, x1, x2, AY, RED, t, speed=0.5, offset=i*0.33)

    # ── CUSTOMIZE: Section A node animations
    # Example: fill bar on node[1] (CPU-like indicator)
    if len(SEC_A_NODES) >= 2:
        nx = SEC_A_NODES[1][0]
        fill_bar(ax, nx, AY - 0.45, 1.6, 0.18, RED, t, speed=1.2)
        pct = int(abs(np.sin(t * np.pi * 1.2)) * 75 + 20)
        ax.text(nx, AY - 0.72, f'{pct}%',
                ha='center', va='center', fontsize=7.5, color=AMBER, zorder=8)

    # ── Pulse ring on middle node (HPA/controller equivalent)
    mid_a = len(SEC_A_NODES) // 2
    pulse_ring(ax, SEC_A_NODES[mid_a][0], AY, AMBER, t, speed=1.5)

    # ── Notice bar Section A
    notice_bar(ax, 0.3, 4.62, 15.4, 0.62,
               RED, '⚠️', 'REACTIVE (Lagging)', NOTICE_A)

    # ════════════════════════════════
    # SECTION B FLOW  (y center = 2.5)
    # ════════════════════════════════
    BY = 2.5   # vertical center for section B nodes

    # Draw nodes
    for i, (nx, lbl, sub, col) in enumerate(SEC_B_NODES):
        draw_box(ax, nx, BY, BOX_W, BOX_H, col, lbl, sub,
                 glow=(col == GREEN))

    # Draw arrows (FAST for section B)
    for i in range(len(SEC_B_NODES) - 1):
        x1 = SEC_B_NODES[i][0] + gap
        x2 = SEC_B_NODES[i+1][0] - gap
        blbl = SEC_B_ARROW_LABELS[i] if i < len(SEC_B_ARROW_LABELS) else ''
        draw_dash_anim(ax, x1, x2, BY, GREEN, t, fast=True, offset=i*0.15)
        draw_arrow(ax, x1, x2, BY, GREEN, label=blbl, fast=True)
        # Three fast dots (offset for simultaneous feel)
        for off in [0.0, 0.28, 0.56]:
            moving_dot(ax, x1, x2, BY, GREEN, t, speed=1.4, offset=off, ms=7)

    # ── Pulse ring on KEDA/controller node
    mid_b = len(SEC_B_NODES) // 2
    pulse_ring(ax, SEC_B_NODES[mid_b][0], BY, GREEN, t, speed=2.5)

    # ── CUSTOMIZE: Section B node animations
    # Example: queue fill bars on first node
    if len(SEC_B_NODES) >= 1:
        nx = SEC_B_NODES[0][0]
        fill_bar(ax, nx, BY - 0.42, 1.6, 0.14, BLUE, t, speed=0.9)
        count = int(abs(np.sin(t * np.pi * 0.9)) * 480 + 20)
        ax.text(nx, BY - 0.68, f'{count} events',
                ha='center', va='center', fontsize=7.5, color=BLUE, zorder=8)

    # ── Notice bar Section B
    notice_bar(ax, 0.3, 0.45, 15.4, 0.62,
               GREEN, '✅', 'PROACTIVE (Instant)', NOTICE_B)

    # ════════════════════════════════
    # COMPARISON CARDS (very bottom strip — if space allows)
    # Adjust y positions if needed
    # ════════════════════════════════
    # Card A
    ca = FancyBboxPatch((0.3, 0.45), 7.4, 0.0,   # hidden, use notice bar instead
                         boxstyle="round,pad=0.04",
                         facecolor='none', edgecolor='none', alpha=0, zorder=1)
    ax.add_patch(ca)

    # ── Tags
    ax.text(0.5, 0.18, TAGS,
            ha='left', va='center', fontsize=8, color='#30363d',
            zorder=5, alpha=0.6)

    # Save frame
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=DPI,
                bbox_inches='tight', facecolor=BG, edgecolor='none')
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    plt.close(fig)
    return img


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print(f"Generating {N_FRAMES} frames...")
    frames = []
    for i in range(N_FRAMES):
        t = i / N_FRAMES
        frames.append(make_frame(t))
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{N_FRAMES} done")

    out = OUTPUT
    print(f"Saving GIF -> {out}")
    frames[0].save(
        out, save_all=True, append_images=frames[1:],
        duration=FRAME_DUR_MS, loop=0, optimize=False
    )
    size_mb = os.path.getsize(out) / 1024 / 1024
    print(f"Done! {len(frames)} frames | {frames[0].size} | {size_mb:.1f} MB")
    print(f"Saved: {out}")
