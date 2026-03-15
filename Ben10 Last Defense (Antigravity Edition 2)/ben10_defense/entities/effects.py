"""
effects.py — Particle, FloatText, Shake, Announce visual effects.
Depends on: config (colors/sizes), draw_utils (dtxt_bg, glow), font_lang (F).
"""
import math
import random
import pygame

from ben10_defense.config import GOLD
from ben10_defense.draw_utils import dtxt_bg, glow
from ben10_defense.font_lang import F


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'col', 'life', 'ml', 'r', 'grav')

    def __init__(self, x, y, col, smin=1.5, smax=5.5, grav=0.12):
        self.x = float(x); self.y = float(y); self.col = col
        a = random.uniform(0, math.tau); sp = random.uniform(smin, smax)
        self.vx = math.cos(a)*sp; self.vy = math.sin(a)*sp
        self.grav = grav; self.life = random.randint(18, 40)
        self.ml = self.life; self.r = random.randint(2, 5)

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += self.grav; self.life -= 1

    def draw(self, surf):
        a = self.life / self.ml
        c = tuple(min(255, int(v*a)) for v in self.col)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), max(1, int(self.r*a)))


class FloatText:
    def __init__(self, x, y, text, col):
        self.x = float(x); self.y = float(y)
        self.text = text; self.col = col
        self.life = 60; self.ml = 60

    def update(self):
        self.y -= 0.85; self.life -= 1

    def draw(self, surf):
        a = self.life / self.ml
        c = tuple(int(v*a) for v in self.col)
        dtxt_bg(surf, self.text, 's', c, int(self.x), int(self.y),
                pad=4, bg=(0, 0, 0, int(100*a)))


class Shake:
    def __init__(self): self.dur = 0; self.mag = 0

    def trigger(self, mag=6, dur=8):
        self.mag = max(self.mag, mag); self.dur = max(self.dur, dur)

    def get(self):
        if self.dur <= 0: return 0, 0
        self.dur -= 1; m = self.mag * (self.dur / 8.0)
        return random.uniform(-m, m), random.uniform(-m, m)


class Announce:
    def __init__(self): self.text = ''; self.life = 0; self.col = GOLD

    def show(self, t, c=None):
        self.text = t; self.life = 130; self.col = c or GOLD

    def update(self):
        self.life = max(0, self.life - 1)

    def draw(self, surf):
        if self.life <= 0: return
        fi = min(1.0, self.life / 22.0)
        fo = min(1.0, (130 - self.life) / 18.0) if self.life > 108 else 1.0
        a = fi * fo
        sc = 1.0 + 0.055*math.sin(self.life * 0.18)
        s = F['xl'].render(self.text, True, tuple(int(v*a) for v in self.col))
        sw2 = int(s.get_width()*sc); sh2 = int(s.get_height()*sc)
        s2 = pygame.transform.scale(s, (sw2, sh2))
        from ben10_defense.config import GW, SH
        r2 = s2.get_rect(center=(GW//2, SH//2 - 24))
        bg_s = pygame.Surface((r2.w+24, r2.h+10), pygame.SRCALPHA)
        pygame.draw.rect(bg_s, (0, 0, 0, int(160*a)), bg_s.get_rect(), border_radius=8)
        surf.blit(bg_s, (r2.x-12, r2.y-5)); surf.blit(s2, r2)
