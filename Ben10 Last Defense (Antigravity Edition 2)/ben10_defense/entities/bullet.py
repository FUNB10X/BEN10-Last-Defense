"""
bullet.py — Bullet class with four bullet-type draw styles.
Depends on: draw_utils (glow), sound (sfx).
"""
import math
import pygame

from ben10_defense.draw_utils import glow
from ben10_defense.sound import sfx


class Bullet:
    def __init__(self, x, y, target, dmg, col, spd, btype, parts, floats):
        self.x, self.y = float(x), float(y)
        self.target = target
        self.dmg = dmg; self.col = col; self.spd = spd; self.btype = btype
        self.alive = True; self.trail = []
        self.parts = parts; self.floats = floats
        self.tick = 0

    def update(self):
        if not self.target.alive:
            self.alive = False; return
        dx = self.target.x - self.x; dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.spd + 3:
            self.target.hurt(self.dmg, self.parts, self.floats)
            if self.target.kind == 'boss': sfx('boss_hit')
            self.alive = False; return
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 8: self.trail.pop(0)
        self.x += dx/dist * self.spd; self.y += dy/dist * self.spd
        self.tick = (self.tick + 1) % 60

    def draw(self, surf):
        ix, iy = int(self.x), int(self.y)
        t = self.tick

        if self.btype == 'fire':
            for i, (tx, ty) in enumerate(self.trail):
                a = (i+1) / max(1, len(self.trail))
                pygame.draw.circle(surf, (int(255*a), int(100*a), 0), (tx, ty), max(1, int(4*a)))
            glow(surf, (255,100,0), ix, iy, 14, 80)
            pygame.draw.circle(surf, (255,145,20), (ix,iy), 6)
            pygame.draw.circle(surf, (255,228,60), (ix,iy), 3)
            fa = t*0.4; fx = ix+int(math.cos(fa)*4); fy = iy+int(math.sin(fa)*4)
            pygame.draw.circle(surf, (255,240,80), (fx,fy), 2)

        elif self.btype == 'fist':
            for i, (tx, ty) in enumerate(self.trail):
                a = (i+1) / max(1, len(self.trail))
                pygame.draw.circle(surf, (int(220*a), int(15*a), int(15*a)), (tx, ty), max(1, int(4*a)))
            glow(surf, (255,40,40), ix, iy, 13, 75)
            pygame.draw.circle(surf, (220,20,20), (ix,iy), 6)
            pygame.draw.circle(surf, (255,80,80), (ix,iy), 6, 2)
            pygame.draw.circle(surf, (255,150,150), (ix,iy), 3)

        elif self.btype == 'bolt':
            for i, (tx, ty) in enumerate(self.trail):
                a = (i+1) / max(1, len(self.trail))
                pygame.draw.circle(surf, (int(50*a), int(170*a), int(255*a)), (tx, ty), max(1, int(3*a)))
            glow(surf, (100,200,255), ix, iy, 11, 82)
            pygame.draw.circle(surf, (160,228,255), (ix,iy), 5)
            pygame.draw.circle(surf, (220,245,255), (ix,iy), 2)

        elif self.btype == 'crystal':
            for i, (tx, ty) in enumerate(self.trail):
                a = (i+1) / max(1, len(self.trail))
                pygame.draw.circle(surf, (int(110*a), int(220*a), int(255*a)), (tx, ty), max(1, int(3*a)))
            glow(surf, (160,240,255), ix, iy, 12, 70)
            pts = [(ix, iy-7), (ix+5, iy), (ix, iy+5), (ix-5, iy)]
            pygame.draw.polygon(surf, (110,220,255), pts)
            pygame.draw.polygon(surf, (215,248,255), pts)
            pygame.draw.polygon(surf, (200,248,255), pts, 1)
