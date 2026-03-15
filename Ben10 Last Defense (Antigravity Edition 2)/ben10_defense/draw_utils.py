"""
draw_utils.py — Drawing helpers, geometry utilities, perspective scale.
Depends on: config (colors/layout), font_lang (Fk).
"""
import math
import pygame

from ben10_defense.config import WP, PATH_W, UI_H, GH
from ben10_defense.font_lang import Fk

# ── Text rendering ─────────────────────────────────────────
def dtxt(surf, text, fk, col, x, y, anch='center', shad=False):
    f = Fk()[fk]
    if shad:
        s = f.render(str(text), True, (0, 0, 0))
        r = s.get_rect(); setattr(r, anch, (x+2, y+2)); surf.blit(s, r)
    s = f.render(str(text), True, col)
    r = s.get_rect(); setattr(r, anch, (x, y)); surf.blit(s, r)

def dtxt_bg(surf, text, fk, col, x, y, pad=6, bg=(0, 0, 0, 160), anch='center', shadow=None):
    """Text with dark pill background for readability. Supports anch and shadow (args)."""
    f = Fk()[fk]; s = f.render(str(text), True, col); r = s.get_rect()
    setattr(r, anch, (x, y))
    bg_r = pygame.Rect(r.x-pad, r.y-pad//2, r.w+pad*2, r.h+pad)
    bg_s = pygame.Surface((bg_r.w, bg_r.h), pygame.SRCALPHA)
    pygame.draw.rect(bg_s, (bg[0], bg[1], bg[2], bg[3]), bg_s.get_rect(), border_radius=6)
    surf.blit(bg_s, (bg_r.x, bg_r.y)); surf.blit(s, r)

# ── Shape helpers ──────────────────────────────────────────
def rrect(surf, col, rect, rad=6, width=0):
    """Draw a rounded rectangle. Resilience: handles (surf, rect, col) if swapped."""
    # Heuristic to fix swapped arguments (surf, rect, col)
    if not isinstance(col, (tuple, list)) and isinstance(rect, (tuple, list)):
        col, rect = rect, col
    elif isinstance(col, (pygame.Rect, tuple, list)) and len(col) == 4 and \
         isinstance(rect, (tuple, list)) and (len(rect) == 3 or len(rect) == 4):
        # col is 4-item (rect-like), rect is 3/4-item (color-like)
        col, rect = rect, col

    try:
        pygame.draw.rect(surf, col, rect, width=width, border_radius=rad)
    except Exception:
        # Absolute fallback: try to force rect to be a tuple of ints
        if hasattr(rect, 'x'): r2 = (int(rect.x), int(rect.y), int(rect.w), int(rect.h))
        else: r2 = tuple(int(x) for x in rect)
        pygame.draw.rect(surf, col, r2, width=width, border_radius=rad)

def glow(surf, col, cx, cy, r, a=60):
    if r < 2: return
    s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
    pygame.draw.circle(s, (col[0], col[1], col[2], a), (r, r), r)
    surf.blit(s, (cx-r, cy-r))

def lerp_col(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

# ── Geometry ───────────────────────────────────────────────
def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx-ax, by-ay
    if dx == 0 and dy == 0:
        return math.hypot(px-ax, py-ay)
    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy) / (dx*dx + dy*dy)))
    return math.hypot(px-(ax+t*dx), py-(ay+t*dy))

def on_path(x, y, margin=26):
    """Return True if (x,y) is within margin pixels of the path."""
    for i in range(len(WP)-1):
        if seg_dist(x, y, *WP[i], *WP[i+1]) < PATH_W//2 + margin:
            return True
    return False

# ── Perspective & shadow ───────────────────────────────────
def ps(y):
    """Perspective scale — sprites slightly smaller near top of game area."""
    t = max(0.0, min(1.0, (y - UI_H) / GH))
    return 0.72 + 0.28*t

def shd(surf, x, y, rw, rh=None, alpha=48):
    if rh is None: rh = max(4, rw//3)
    s = pygame.Surface((rw*2+2, rh*2+2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, alpha), s.get_rect())
    surf.blit(s, (x-rw-1, y-rh-1))
