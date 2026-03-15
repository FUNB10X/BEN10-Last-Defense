"""
enemy.py — Enemy class with 5 enemy-type sprite-draw methods.
Depends on: config, data (BASE_ENEMIES, DIFFICULTIES, WP),
            draw_utils (rrect, glow, shd, dtxt_bg, ps),
            entities/effects (Particle, FloatText).
"""
import math
import random
import pygame

from ben10_defense.config import GOLD, HP_G, HP_O, HP_R, WP
from ben10_defense.data import BASE_ENEMIES, DIFFICULTIES, get_wave_spd_mult
from ben10_defense.draw_utils import rrect, glow, shd, dtxt_bg, ps
from ben10_defense.entities.effects import Particle, FloatText


class Enemy:
    def __init__(self, kind, diff_key='normal', wave_num=1):
        d = BASE_ENEMIES[kind]; dk = DIFFICULTIES[diff_key]
        self.kind = kind
        # specific boss HP requested by user
        if kind == 'boss':
            if diff_key == 'easy':   self.hp = 1500
            elif diff_key == 'normal': self.hp = 2000
            elif diff_key == 'hard':
                 self.hp = 3000 # Hard W15 and W30
            else: self.hp = int(d['hp'] * dk['hp'])
        else:
            self.hp = int(d['hp'] * dk['hp'])

        self.mhp = self.hp
        
        # Wave-based speed scaling
        is_boss = (kind == 'boss')
        wave_spd_mult = get_wave_spd_mult(diff_key, wave_num, is_boss)
        self.spd  = d['spd'] * wave_spd_mult
        
        self.dmg = d['dmg']
        self.base_rew = d['rew']; self.rew_mult = dk['rew']; self.col = d['col']
        self.x, self.y = float(WP[0][0]), float(WP[0][1])
        self.wp = 1; self.alive = True; self.reached = False
        self.angle = 0.0; self.tick = random.randint(0, 59)
        self.hit_flash = 0
        self._napalm_slow = 0   # frames of slow from Heatblast
        self._stun        = 0   # frames of stun from Four Arms
        self._xlr8_slow   = 0   # frames of slow from XLR8 field

    @property
    def rew(self):
        return max(1, int(self.base_rew * self.rew_mult))

    def update(self):
        if self.wp >= len(WP): self.reached = True; return
        actual_spd = self.spd
        if self._stun > 0:
            actual_spd = 0; self._stun -= 1
        else:
            if self._xlr8_slow > 0:
                actual_spd *= 0.5; self._xlr8_slow -= 1
            elif self._napalm_slow > 0:
                actual_spd *= 0.7; self._napalm_slow -= 1
        if self.kind == 'boss' and self.hp / self.mhp < 0.4:
            actual_spd *= 1.5
        tx, ty = WP[self.wp]; dx, dy = tx-self.x, ty-self.y; dist = math.hypot(dx, dy)
        if dist > 0: self.angle = math.atan2(dy, dx)
        if dist <= actual_spd + 0.5:
            self.x, self.y = float(tx), float(ty); self.wp += 1
        else:
            self.x += dx/dist * actual_spd; self.y += dy/dist * actual_spd
        self.tick = (self.tick+1) % 60
        if self.hit_flash > 0: self.hit_flash -= 1

    def hurt(self, dmg, parts, floats):
        self.hp -= dmg; self.hit_flash = 5
        for _ in range(4): parts.append(Particle(self.x, self.y, self.col, 1, 4.5))
        if self.hp <= 0:
            self.alive = False
            burst = 14 + (20 if self.kind == 'boss' else 0)
            spd_lo = 1.5 if self.kind != 'boss' else 2.5
            spd_hi = 6   if self.kind != 'boss' else 10
            for _ in range(burst):
                parts.append(Particle(self.x, self.y, self.col, spd_lo, spd_hi))
            floats.append(FloatText(self.x, self.y-24, "+$"+str(self.rew), GOLD))

    # ── Master draw dispatcher ─────────────────────────────
    def draw(self, surf):
        ix, iy = int(self.x), int(self.y); t = self.tick; sc = ps(iy)
        ca = math.cos(self.angle); sa = math.sin(self.angle)
        flash_alpha = min(180, self.hit_flash*40) if self.hit_flash > 0 else 0

        if   self.kind == 'grunt': self._draw_grunt(surf, ix, iy, t, sc, ca, sa, flash_alpha)
        elif self.kind == 'drone': self._draw_drone(surf, ix, iy, t, sc, ca, sa, flash_alpha)
        elif self.kind == 'tank':  self._draw_tank (surf, ix, iy, t, sc, ca, sa, flash_alpha)
        elif self.kind == 'elite': self._draw_elite(surf, ix, iy, t, sc, ca, sa, flash_alpha)
        elif self.kind == 'boss':  self._draw_boss (surf, ix, iy, t, sc, ca, sa, flash_alpha)

        # HP bar
        sz_ref = (14 if self.kind == 'grunt' else 16 if self.kind == 'drone'
                  else 22 if self.kind == 'tank' else 20 if self.kind == 'elite' else 44)
        bw2 = max(int(sz_ref*2*sc)+6, 34); bh2 = 5
        bx3 = ix - bw2//2; by3 = iy - int(sz_ref*sc) - 32
        rrect(surf, (40,0,0), (bx3, by3, bw2, bh2), 2)
        ratio = max(0.0, self.hp / self.mhp)
        hc = HP_G if ratio > .5 else HP_O if ratio > .22 else HP_R
        if ratio > 0: rrect(surf, hc, (bx3, by3, int(bw2*ratio), bh2), 2)
        pygame.draw.rect(surf, (110,110,110), (bx3, by3, bw2, bh2), 1)

    # ── Grunt ──────────────────────────────────────────────
    def _draw_grunt(self, surf, ix, iy, t, sc, ca, sa, flash_alpha):
        bw = int(14*sc); bh = int(18*sc); hr = int(9*sc); foot = iy+int(6*sc)
        shd(surf, ix, foot+2, int(14*sc), int(5*sc))
        for side in (-1, 1):
            lx = ix+side*int(5*sc)
            pygame.draw.line(surf, (120,20,20), (lx, foot-int(8*sc)), (lx, foot), max(2, int(4*sc)))
            pygame.draw.ellipse(surf, (80,10,10), (lx-int(4*sc), foot-int(3*sc), int(8*sc), int(4*sc)))
        body = pygame.Rect(ix-bw//2, foot-bh-int(8*sc), bw, bh)
        pygame.draw.rect(surf, (110,18,18), body, border_radius=int(5*sc))
        pygame.draw.rect(surf, self.col, pygame.Rect(body.x+1, body.y+1, body.w-2, body.h-2), border_radius=int(4*sc))
        pygame.draw.line(surf, (220,80,80), (ix, body.y+int(4*sc)), (ix, body.bottom-int(4*sc)), max(1, int(3*sc)))
        for side in (-1, 1):
            ax2 = ix+side*int(bw*.8); ay2 = foot-bh//2
            pygame.draw.line(surf, (155,28,28), (ix+side*bw//2, foot-bh+int(4*sc)), (ax2, ay2), max(2, int(4*sc)))
            pygame.draw.circle(surf, (200,50,50), (ax2, ay2), max(2, int(4*sc)))
        hy = foot-bh-int(8*sc)-hr
        pygame.draw.circle(surf, (88,10,10), (ix, hy), hr+1)
        pygame.draw.circle(surf, self.col,   (ix, hy), hr)
        vr = pygame.Rect(ix-hr+2, hy-int(3*sc), hr*2-4, int(5*sc))
        pygame.draw.rect(surf, (255,215,0), vr, border_radius=2)

    # ── Drone ──────────────────────────────────────────────
    def _draw_drone(self, surf, ix, iy, t, sc, ca, sa, flash_alpha):
        bob = int(math.sin(t*0.15)*3*sc); by2 = iy-int(8*sc)+bob
        disc_rw = int(20*sc); disc_rh = int(7*sc)
        shd(surf, ix, iy+int(4*sc), int(18*sc), int(6*sc), 38)
        pygame.draw.ellipse(surf, (15,55,120), (ix-disc_rw, by2+int(3*sc), disc_rw*2, disc_rh*2))
        pygame.draw.ellipse(surf, (20,78,165), (ix-disc_rw, by2, disc_rw*2, disc_rh))
        pygame.draw.ellipse(surf, self.col,    (ix-disc_rw+2, by2+1, disc_rw*2-4, disc_rh-2))
        dr2 = int(10*sc); dh2 = int(9*sc)
        pygame.draw.ellipse(surf, (15,62,150),  (ix-dr2, by2-dh2+2, dr2*2, dh2))
        pygame.draw.ellipse(surf, (50,138,218), (ix-dr2+1, by2-dh2+3, dr2*2-2, dh2-2))
        pygame.draw.circle(surf, (180,222,255), (ix, by2-int(3*sc)), max(2, int(5*sc)))
        if (t//10) % 2 == 0:
            pygame.draw.circle(surf, (255,45,45), (ix, by2+int(9*sc)), max(2, int(3*sc)))
            glow(surf, (255,45,45), ix, by2+int(9*sc), int(6*sc), 52)

    # ── Tank ───────────────────────────────────────────────
    def _draw_tank(self, surf, ix, iy, t, sc, ca, sa, flash_alpha):
        w = int(26*sc); h = int(20*sc); foot = iy+int(8*sc)
        shd(surf, ix, foot+2, int(24*sc), int(8*sc))
        for side in (-1, 1):
            tx2 = ix+side*int(w*.52)
            tr = pygame.Rect(tx2-int(6*sc), foot-h+2, int(12*sc), h)
            pygame.draw.rect(surf, (30,32,35), tr, border_radius=int(4*sc))
            pygame.draw.rect(surf, (55,58,62), tr, 1, border_radius=int(4*sc))
            for k in range(4):
                sy2 = tr.y+k*(h//4)
                pygame.draw.line(surf, (40,42,46), (tr.x, sy2), (tr.right, sy2), 1)
        hull = pygame.Rect(ix-int(w*.38), foot-h+int(4*sc), int(w*.76), h-int(4*sc))
        pygame.draw.rect(surf, (48,52,56), hull, border_radius=int(4*sc))
        pygame.draw.rect(surf, self.col, pygame.Rect(hull.x+1, hull.y+1, hull.w-2, hull.h-2), border_radius=int(3*sc))
        turr = pygame.Rect(ix-int(9*sc), hull.y-int(10*sc), int(18*sc), int(12*sc))
        pygame.draw.rect(surf, (42,45,50), turr, border_radius=int(4*sc))
        pygame.draw.circle(surf, (60,63,68),
                           (turr.centerx+int(ca*int(10*sc)), turr.centery+int(sa*int(5*sc))),
                           max(2, int(4*sc)))
        vp = pygame.Rect(ix-int(5*sc), turr.y+int(3*sc), int(10*sc), int(5*sc))
        pygame.draw.rect(surf, (0,175,215), vp, border_radius=2)

    # ── Elite ──────────────────────────────────────────────
    def _draw_elite(self, surf, ix, iy, t, sc, ca, sa, flash_alpha):
        bh = int(28*sc); bw = int(16*sc); foot = iy+int(6*sc)
        shd(surf, ix, foot+2, int(16*sc), int(5*sc))
        glow(surf, self.col, ix, foot-bh//2, int(20*sc), int(32+8*math.sin(t*0.2)))
        for side in (-1, 1):
            lx = ix+side*int(5*sc); la = math.radians(t*4*side)
            pygame.draw.line(surf, (100,10,128), (lx, foot-int(10*sc)),
                             (lx+int(math.sin(la)*4*sc), foot), max(2, int(4*sc)))
        body = pygame.Rect(ix-bw//2, foot-bh, bw, bh)
        pygame.draw.rect(surf, (45,5,60), body, border_radius=int(5*sc))
        pygame.draw.rect(surf, self.col, pygame.Rect(body.x+1, body.y+1, body.w-2, body.h-2), border_radius=int(4*sc))
        for k in range(3):
            ey2 = body.y+int((k+1)*bh/4)
            pygame.draw.line(surf, (228,138,252), (body.x+2, ey2), (body.right-2, ey2), max(1, int(2*sc)))
        for side in (-1, 1):
            sx = ix+side*int(bw*.6); sy2 = body.y+int(4*sc)
            pts = [(sx, sy2-int(12*sc)), (sx+side*int(8*sc), sy2+int(4*sc)), (sx, sy2+int(2*sc))]
            pygame.draw.polygon(surf, (165,40,210), pts)
        hy = body.y-int(10*sc)
        hpts = [(ix, hy-int(8*sc)), (ix+int(8*sc), hy+int(5*sc)), (ix-int(8*sc), hy+int(5*sc))]
        pygame.draw.polygon(surf, (60,0,80), hpts)
        pygame.draw.polygon(surf, (165,40,210), hpts)
        for side in (-1, 1):
            ex2 = ix+side*int(3*sc); ey2 = hy
            glow(surf, (228,98,252), ex2, ey2, int(5*sc), 78)
            pygame.draw.circle(surf, (238,148,252), (ex2, ey2), max(2, int(3*sc)))

    # ── Boss (Vilgax) ──────────────────────────────────────
    def _draw_boss(self, surf, ix, iy, t, sc, ca, sa, flash_alpha):
        bob = int(math.sin(t*0.10)*5); bh = int(58*sc); bw = int(38*sc)
        foot = iy+int(14*sc)+bob
        glow(surf, (180,0,0), ix, foot-bh//2, int(55*sc), int(25+8*math.sin(t*0.13)))
        shd(surf, ix, foot+2, int(36*sc), int(12*sc), 58)
        for k in range(4):
            la = math.radians(200+k*45+math.sin(t*0.12+k)*15)
            lx = ix+int(math.cos(la)*int(20*sc)); ly = foot-int(10*sc)+int(math.sin(la)*int(8*sc))
            pygame.draw.line(surf, (80,0,0), (ix, foot-int(10*sc)), (lx, ly), max(3, int(7*sc)))
            pygame.draw.circle(surf, (120,10,10), (lx, ly), max(2, int(5*sc)))
        body = pygame.Rect(ix-bw//2, foot-bh, bw, bh)
        pygame.draw.rect(surf, (70,0,0), body, border_radius=int(8*sc))
        pygame.draw.rect(surf, self.col, pygame.Rect(body.x+2, body.y+2, body.w-4, body.h-4), border_radius=int(6*sc))
        pygame.draw.rect(surf, (238,52,52), pygame.Rect(body.x+5, body.y+5, body.w-10, body.h-10), border_radius=int(4*sc))
        core_y = body.y+bh//2-int(4*sc)
        glow(surf, (255,50,0), ix, core_y, int(14*sc), 72)
        pygame.draw.circle(surf, (255,78,0),  (ix, core_y), max(4, int(8*sc)))
        pygame.draw.circle(surf, (255,198,50), (ix, core_y), max(2, int(4*sc)))
        for k, ang_d in enumerate([130, 50, 140, 40]):
            ar = math.radians(ang_d+k*2)
            ax2 = ix+int(math.cos(ar)*int(32*sc)); ay2 = body.y+int(10*sc)+int(math.sin(ar)*int(14*sc))
            pygame.draw.line(surf, (100,0,0), (ix, body.y+int(14*sc)), (ax2, ay2), max(4, int(8*sc)))
            pygame.draw.circle(surf, (200,20,20), (ax2, ay2), max(3, int(6*sc)))
            glow(surf, (218,28,28), ax2, ay2, int(8*sc), 48)
        hy = body.y-int(16*sc)
        pygame.draw.ellipse(surf, (80,0,0),  (ix-int(16*sc), hy-int(10*sc), int(32*sc), int(24*sc)))
        pygame.draw.ellipse(surf, (120,0,0), (ix-int(14*sc), hy-int(8*sc),  int(28*sc), int(20*sc)))
        pygame.draw.ellipse(surf, (158,8,8), (ix-int(12*sc), hy-int(4*sc),  int(24*sc), int(16*sc)))
        for side in (-1, 1):
            ex2 = ix+side*int(6*sc); ey2 = hy
            glow(surf, (255,78,0), ex2, ey2, int(8*sc), 88)
            pygame.draw.ellipse(surf, (255,98,0),  (ex2-int(5*sc), ey2-int(4*sc), int(10*sc), int(7*sc)))
            pygame.draw.ellipse(surf, (255,218,78), (ex2-int(3*sc), ey2-int(2*sc), int(6*sc), int(4*sc)))
            pygame.draw.ellipse(surf, (0,0,0),      (ex2-int(2*sc), ey2-int(1*sc), int(4*sc), int(3*sc)))
        dtxt_bg(surf, "VILGAX", 'xs', (255,78,78), ix, hy-int(18*sc))
        # Hit flash
        if flash_alpha > 0:
            flash_s = pygame.Surface((bw+10, bh+30), pygame.SRCALPHA)
            pygame.draw.rect(flash_s, (255,80,80,flash_alpha), (0,0,bw+10,bh+30), border_radius=8)
            surf.blit(flash_s, (ix-bw//2-5, foot-bh-5))
