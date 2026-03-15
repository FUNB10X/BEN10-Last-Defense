"""
map_builder.py — Builds the static 2D map surface.
Depends on: config, font_lang (F), draw_utils (on_path).
"""
import math
import random
import pygame

from ben10_defense.config import (
    GW, GH, UI_H, WP, PATH_W,
    GRASS_A, GRASS_B, PATH_COL, PATH_EDG, PATH_DRK,
)
from ben10_defense.font_lang import F
from ben10_defense.draw_utils import on_path


def build_map():
    s = pygame.Surface((GW, GH))
    s.fill(GRASS_A)
    # Grid
    for gx in range(0, GW, 36): pygame.draw.line(s, GRASS_B, (gx, 0), (gx, GH))
    for gy in range(0, GH, 36): pygame.draw.line(s, GRASS_B, (0, gy), (GW, gy))
    # Random tufts (seeded for determinism)
    rng2 = random.Random(42)
    for _ in range(200):
        gx = rng2.randint(4, GW-4); gy = rng2.randint(4, GH-4)
        if not on_path(gx, gy+UI_H, 36):
            c2 = (rng2.randint(15,28), rng2.randint(82,100), rng2.randint(15,28))
            pygame.draw.circle(s, c2, (gx, gy), rng2.randint(2, 5))
    sh = [(x, y-UI_H) for x, y in WP]
    # Path dark edge
    for i in range(len(sh)-1):
        pygame.draw.line(s, PATH_DRK, sh[i], sh[i+1], PATH_W+12)
    for p in sh[1:-1]:
        pygame.draw.circle(s, PATH_DRK, p, PATH_W//2+6)
    # Path edge
    for i in range(len(sh)-1):
        pygame.draw.line(s, PATH_EDG, sh[i], sh[i+1], PATH_W+6)
    for p in sh[1:-1]:
        pygame.draw.circle(s, PATH_EDG, p, PATH_W//2+3)
    # Path fill
    for i in range(len(sh)-1):
        pygame.draw.line(s, PATH_COL, sh[i], sh[i+1], PATH_W)
    for p in sh[1:-1]:
        pygame.draw.circle(s, PATH_COL, p, PATH_W//2)
    # Dashed centre-line
    for i in range(len(sh)-1):
        ax, ay = sh[i]; bx, by = sh[i+1]
        ln = math.hypot(bx-ax, by-ay); n = max(1, int(ln/20))
        for j in range(0, n, 2):
            t1 = j/n; t2 = min(1, (j+0.6)/n)
            pygame.draw.line(s, (165,128,82),
                             (int(ax+(bx-ax)*t1), int(ay+(by-ay)*t1)),
                             (int(ax+(bx-ax)*t2), int(ay+(by-ay)*t2)), 2)
    # Corner decorations
    for p in sh[1:-1]:
        pygame.draw.circle(s, (170,132,85), p, 8)
        pygame.draw.circle(s, (130,95,55),  p, 8, 2)
    # Base target
    bx2, by2 = sh[-1]
    for r, c in [(28,(0,60,0)),(24,(0,145,38)),(18,(0,195,55)),(12,(0,225,70))]:
        pygame.draw.circle(s, c, (bx2, by2), r)
    lbl = F['xs'].render("BASE", True, (255,255,200))
    s.blit(lbl, lbl.get_rect(center=(bx2, by2)))
    return s


# Built once at import — reused every frame
MAP_SURF = build_map()
