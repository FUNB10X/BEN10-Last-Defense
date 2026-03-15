"""
tower.py — Tower class with upgrade system and 6 alien sprite draw methods.
Depends on: config, data (TOWERS, WP), draw_utils, font_lang,
            entities/effects (Particle, FloatText), entities/bullet (Bullet), sound (sfx).
"""
import math
import random
import pygame

from ben10_defense.config import GOLD, OMNI_G, WHITE
from ben10_defense.data import TOWERS
from ben10_defense.config import WP
from ben10_defense.draw_utils import rrect, glow, shd, dtxt_bg, ps
from ben10_defense.font_lang import F, Fk, LANG, tr
from ben10_defense.entities.effects import Particle, FloatText
from ben10_defense.entities.bullet import Bullet
from ben10_defense.sound import sfx
import os as _os

_IDIN_PHOTO = None
def _get_idin_photo():
    global _IDIN_PHOTO
    if _IDIN_PHOTO is None:
        try:
            path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'assets', 'idin_photo.png')
            if _os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                _IDIN_PHOTO = img
        except Exception:
            _IDIN_PHOTO = False
    return _IDIN_PHOTO if _IDIN_PHOTO is not False else None


class Tower:
    # ── Upgrade cost table (cost to go FROM level TO level+1) ──
    UPGRADE_COSTS = {
        'heatblast':   [60,  90,  130, 180],
        'fourarms':    [120, 160, 220, 300],
        'xlr8':        [180, 240, 320, 420],
        'diamondhead': [240, 320, 420, 560],
        'grandpa':     [180, 240, 0,   0  ],
        'ben10':       [360, 0,   0,   0  ],
        'idin':        [500, 750, 1000, 1500],
    }
    # ── Upgrade descriptions per level ──
    UPGRADE_DESC = {
        'heatblast':  ['','DMG↑ Rate↑','Napalm: ชะลอศัตรู','DMG↑↑ Range↑','Inferno: เผาทุกตัวในรัศมี'],
        'fourarms':   ['','DMG↑↑','Shockwave: สตันชั่วคราว','DMG↑↑ Range↑','Earthquake: สแปลชทุกตัว'],
        'xlr8':       ['','Rate↑↑','Slow Field: ศัตรูช้าลง','Rate↑↑ DMG↑','Bullet Storm: ยิง 3 เป้าพร้อมกัน'],
        'diamondhead':['','DMG↑ Range↑','Crystal Pierce: ทะลุศัตรู','DMG↑↑ Range↑↑','Crystal Storm: ยิงรอบทิศ'],
        'grandpa':    ['','Income↑ +75/10s','','',''],
        'ben10':      ['','ATK x3 แทน x2','','',''],
        'idin':       ['','Income↑ +300/8s','Income↑ +450/8s','Income↑ +700/8s','Income↑ +1200/8s'],
    }

    def __init__(self, kind, x, y):
        d = TOWERS[kind]
        self.kind = kind; self.x, self.y = float(x), float(y)
        self.base_rng = d['rng']; self.base_dmg = d['dmg']; self.base_rate = d['rate']
        self.rng = d['rng']; self.dmg = d['dmg']; self.rate = d['rate']; self.bspd = d['bspd']
        self.col = d['col']; self.bc = d['bc']; self.btype = d['btype']
        self.timer = random.randint(0, max(1, d['rate']))
        self.angle = 0.0; self.tick = 0; self.firing = 0
        self.income_timer = 0.0; self.income_pending = 0
        self.level = 1
        self.total_invested = d['cost']
        self.special_tick = 0
        self.slow_targets = set()
        self.aoe_cooldown = 0
        self.income_amt      = d.get('income_amt', 0)
        self.income_interval = d.get('income_interval', 1.0)

    def upgrade(self):
        if self.level >= 5: return False
        cost = self.UPGRADE_COSTS[self.kind][self.level-1]
        if cost <= 0: return False
        self.level += 1
        self.total_invested += cost
        lv = self.level
        if self.kind == 'heatblast':
            self.dmg  = int(self.base_dmg  * (1 + 0.35*(lv-1)))
            self.rate = max(10, int(self.base_rate * (1 - 0.12*(lv-1))))
            if lv >= 4: self.rng = int(self.base_rng * 1.15)
        elif self.kind == 'fourarms':
            self.dmg = int(self.base_dmg * (1 + 0.45*(lv-1)))
            if lv >= 4: self.rng = int(self.base_rng * 1.20)
        elif self.kind == 'xlr8':
            self.rate = max(8, int(self.base_rate * (1 - 0.18*(lv-1))))
            if lv >= 4: self.dmg = int(self.base_dmg * 1.4)
        elif self.kind == 'diamondhead':
            self.dmg = int(self.base_dmg  * (1 + 0.35*(lv-1)))
            self.rng = int(self.base_rng * (1 + 0.12*(lv-1)))
        elif self.kind == 'grandpa':
            if lv >= 2: self.income_amt = 75
        elif self.kind == 'idin':
             self.income_amt = [200, 300, 450, 700, 1200][lv-1]
        # ben10 upgrade handled in game loop
        return True

    def sell_value(self):
        return max(1, self.total_invested // 2)

    def get_target(self, enemies):
        best = None; bp = -1
        for e in enemies:
            if not e.alive: continue
            if math.hypot(e.x-self.x, e.y-self.y) > self.rng: continue
            idx = min(e.wp, len(WP)-1)
            prog = e.wp*10000 - math.hypot(e.x-WP[idx][0], e.y-WP[idx][1])
            if prog > bp: bp = prog; best = e
        return best

    def update(self, enemies, bullets, parts, floats, dt, dmg_mult=1):
        self.tick  = (self.tick+1) % 60; self.timer += 1
        if self.firing > 0: self.firing -= 1
        d = TOWERS[self.kind]

        # Passive income towers (grandpa / ben10)
        if d['income']:
            self.income_timer += dt
            if self.income_timer >= self.income_interval:
                self.income_timer -= self.income_interval
                amt = self.income_amt
                self.income_pending += amt
                floats.append(FloatText(self.x, self.y-38, "+$"+str(amt), GOLD))
                sfx('cash')
            return

        # Combat towers
        self.special_tick = (self.special_tick+1) % 360
        if self.aoe_cooldown > 0: self.aoe_cooldown -= 1

        # XLR8 Lv3+ slow-field aura
        if self.kind == 'xlr8' and self.level >= 3:
            for ae in enemies:
                if ae.alive and math.hypot(ae.x-self.x, ae.y-self.y) <= self.rng:
                    ae._xlr8_slow = 10

        tgt = self.get_target(enemies)
        if tgt:
            self.angle = math.atan2(tgt.y-self.y, tgt.x-self.x)
            if self.timer >= self.rate:
                self.timer = 0; self.firing = 8
                actual_dmg = int(self.dmg * dmg_mult)
                spawn_x = self.x + math.cos(self.angle)*20
                spawn_y = self.y + math.sin(self.angle)*12
                # Lv5 Crystal Storm
                if self.kind == 'diamondhead' and self.level >= 5:
                    for _ in range(0, 360, 45):
                        tgt2 = self.get_target(enemies)
                        if tgt2:
                            bullets.append(Bullet(self.x, self.y, tgt2, actual_dmg, self.bc, self.bspd, self.btype, parts, floats))
                # Lv5 Bullet Storm (XLR8)
                elif self.kind == 'xlr8' and self.level >= 5:
                    targets3 = [e for e in enemies if e.alive and math.hypot(e.x-self.x, e.y-self.y) <= self.rng]
                    for tgt3 in targets3[:3]:
                        bullets.append(Bullet(spawn_x, spawn_y, tgt3, actual_dmg, self.bc, self.bspd, self.btype, parts, floats))
                else:
                    bullets.append(Bullet(spawn_x, spawn_y, tgt, actual_dmg, self.bc, self.bspd, self.btype, parts, floats))
                # Lv3+ Napalm slow
                if self.kind == 'heatblast' and self.level >= 3:
                    tgt._napalm_slow = 90
                # Lv3+ Shockwave stun
                if self.kind == 'fourarms' and self.level >= 3 and self.aoe_cooldown <= 0:
                    tgt._stun = 30; self.aoe_cooldown = 120
                # Lv5 Earthquake AoE
                if self.kind == 'fourarms' and self.level >= 5 and self.aoe_cooldown <= 0:
                    for ae in enemies:
                        if ae.alive and math.hypot(ae.x-self.x, ae.y-self.y) <= self.rng:
                            ae.hurt(actual_dmg//3, parts, floats)
                    self.aoe_cooldown = 180
                # Lv5 Inferno AoE burn
                if self.kind == 'heatblast' and self.level >= 5 and self.aoe_cooldown <= 0:
                    for ae in enemies:
                        if ae.alive and math.hypot(ae.x-self.x, ae.y-self.y) <= self.rng:
                            ae.hurt(actual_dmg//4, parts, floats)
                            ae._napalm_slow = 60
                    self.aoe_cooldown = 200

    # ── Master draw method ─────────────────────────────────
    def draw(self, surf, hov=False):
        ix, iy = int(self.x), int(self.y); t = self.tick; sc = ps(iy)
        ca = math.cos(self.angle); sa = math.sin(self.angle)

        if hov:
            rs = pygame.Surface((self.rng*2+4, self.rng*2+4), pygame.SRCALPHA); r2 = self.rng+2
            pygame.draw.circle(rs, (255,255,120,14), (r2, r2), self.rng)
            pygame.draw.circle(rs, (255,255,120,60), (r2, r2), self.rng, 1)
            surf.blit(rs, (ix-r2, iy-r2))

        foot = iy + int(10*sc)
        # Platform disc
        shd(surf, ix, foot+3, int(22*sc), int(7*sc), 50)
        pygame.draw.ellipse(surf, (18,26,40), (ix-int(22*sc), foot+2, int(44*sc), int(9*sc)))
        pygame.draw.ellipse(surf, (32,48,68), (ix-int(21*sc), foot,   int(42*sc), int(8*sc)))
        pygame.draw.ellipse(surf, (44,60,82), (ix-int(20*sc), foot-2, int(40*sc), int(7*sc)))

        if self.firing > 0: glow(surf, self.col, ix, iy, int(28*sc), 85)

        if   self.kind == 'heatblast':   self._draw_heatblast(surf, ix, iy, t, sc, ca, sa, foot)
        elif self.kind == 'fourarms':    self._draw_fourarms (surf, ix, iy, t, sc, ca, sa, foot)
        elif self.kind == 'xlr8':        self._draw_xlr8     (surf, ix, iy, t, sc, ca, sa, foot)
        elif self.kind == 'diamondhead': self._draw_diamondhead(surf, ix, iy, t, sc, ca, sa, foot)
        elif self.kind == 'grandpa':     self._draw_grandpa  (surf, ix, iy, t, sc, ca, sa, foot)
        elif self.kind == 'ben10':       self._draw_ben10    (surf, ix, iy, t, sc, ca, sa, foot)
        elif self.kind == 'idin':        self._draw_idin     (surf, ix, iy, t, sc, ca, sa, foot)

        # Move name badges higher (from 54*sc to 70*sc)
        dtxt_bg(surf, tr(TOWERS[self.kind]['name']), 'xs', (220,228,248), ix, iy-int(70*sc), pad=4, bg=(0,0,0,140))
        # Level badge (adjust to match new name position)
        if self.level > 1:
            lv_col = [(255,200,50),(100,220,100),(100,180,255),(255,120,20),(220,50,220)][self.level-1]
            lv_s = F['xs'].render(f'Lv{self.level}', True, lv_col)
            bg_lv = pygame.Surface((lv_s.get_width()+6, lv_s.get_height()+4), pygame.SRCALPHA)
            pygame.draw.rect(bg_lv, (0,0,0,160), bg_lv.get_rect(), border_radius=4)
            surf.blit(bg_lv, (ix-lv_s.get_width()//2-3, iy-int(54*sc)-lv_s.get_height()//2-2))
            surf.blit(lv_s,  (ix-lv_s.get_width()//2,   iy-int(54*sc)-lv_s.get_height()//2))
        if self.firing > 2 and self.kind == 'heatblast' and self.level >= 3:
            glow(surf, (255,140,0), ix, iy, int(32*sc), 30)

    # ── Heatblast ──────────────────────────────────────────
    def _draw_heatblast(self, surf, ix, iy, t, sc, ca, sa, foot):
        bh = int(30*sc); bw = int(20*sc); body_y = foot-bh
        glow(surf, (215,58,0), ix, body_y+bh//2, int(26*sc), 40)
        for side in (-1, 1):
            lx = ix+side*int(6*sc)
            pygame.draw.line(surf, (55,35,20), (lx, foot-int(10*sc)), (lx, foot), max(3, int(5*sc)))
            pygame.draw.ellipse(surf, (65,42,24), (lx-int(4*sc), foot-int(2*sc), int(8*sc), int(4*sc)))
        pygame.draw.ellipse(surf, (52,35,24), (ix-bw//2-2, body_y, bw+4, bh+4))
        pygame.draw.ellipse(surf, (70,50,32), (ix-bw//2, body_y, bw, bh))
        pygame.draw.ellipse(surf, (90,64,42), (ix-bw//2+2, body_y+2, bw-4, bh-4))
        for k in range(6):
            ang_k = math.radians(k*60+t*2)
            x1 = ix+int(math.cos(ang_k)*int(3*sc)); y1 = body_y+bh//2+int(math.sin(ang_k)*int(3*sc))
            x2 = ix+int(math.cos(ang_k)*int(bw*.52)); y2 = body_y+bh//2+int(math.sin(ang_k)*int(bh*.42))
            pygame.draw.line(surf, (255, 82+int(math.sin(t*.18+k)*38), 0), (x1,y1), (x2,y2), max(1, int(2*sc)))
        eye_y = body_y+int(9*sc)
        for side in (-1, 1):
            ex2 = ix+side*int(5*sc)
            pygame.draw.ellipse(surf, (255,108,0), (ex2-int(4*sc), eye_y-int(2*sc), int(8*sc), int(4*sc)))
            pygame.draw.ellipse(surf, (255,228,78),(ex2-int(2*sc), eye_y-int(1*sc), int(4*sc), int(2*sc)))
        for k in range(4):
            fa = math.radians(k*90+t*6); fx = ix+int(math.cos(fa)*int(7*sc))
            fy = body_y-int(2*sc)+int(math.sin(fa)*2)
            fh = int((10+int(math.sin(t*.28+k)*3))*sc)
            pygame.draw.polygon(surf, (255,75,0),   [(fx-int(3*sc),fy),(fx+int(3*sc),fy),(fx,fy-fh)])
            pygame.draw.polygon(surf, (255,188,38), [(fx-int(2*sc),fy-int(2*sc)),(fx+int(2*sc),fy-int(2*sc)),(fx,fy-fh+int(4*sc))])
        for side in (-1, 1):
            if self.firing > 0 and ((side > 0 and ca >= 0) or (side < 0 and ca < 0)):
                ar = self.angle
            else:
                ar = math.radians(90+side*30)
            ax2 = ix+int(math.cos(ar)*int(bw*.58+8)); ay2 = body_y+bh//3+int(math.sin(ar)*int(12*sc))
            pygame.draw.line(surf, (68,45,28), (ix+side*bw//3, body_y+bh//3), (ax2, ay2), max(3, int(6*sc)))
            pygame.draw.circle(surf, (80,52,32), (ax2, ay2), max(3, int(6*sc)))
            if self.firing > 0 and ((side > 0 and ca >= 0) or (side < 0 and ca < 0)):
                glow(surf, (255,112,20), ax2, ay2, int(15*sc), 90)
                pygame.draw.circle(surf, (255,155,30), (ax2, ay2), max(3, int(7*sc)))

    # ── Four Arms ──────────────────────────────────────────
    def _draw_fourarms(self, surf, ix, iy, t, sc, ca, sa, foot):
        bh = int(32*sc); bw = int(28*sc); body_y = foot-bh
        for side in (-1, 1):
            lx = ix+side*int(7*sc)
            pygame.draw.line(surf, (108,6,6), (lx, foot-int(12*sc)), (lx, foot), max(4, int(8*sc)))
            pygame.draw.ellipse(surf, (78,4,4), (lx-int(5*sc), foot-int(2*sc), int(10*sc), int(5*sc)))
        body = pygame.Rect(ix-bw//2, body_y, bw, bh)
        pygame.draw.rect(surf, (98,4,4), body, border_radius=int(6*sc))
        pygame.draw.rect(surf, self.col, pygame.Rect(body.x+2, body.y+2, body.w-4, body.h-4), border_radius=int(5*sc))
        mx2 = body.centerx; my2 = body.centery
        for pts2 in [[(mx2-bw//3,body.y),(mx2+bw//3,body.bottom),(mx2-int(2*sc),body.centery)],
                      [(mx2+bw//3,body.y),(mx2-bw//3,body.bottom),(mx2+int(2*sc),body.centery)]]:
            pygame.draw.polygon(surf, (14,4,4), pts2)
        for j, (ang_d, arm_y_off) in enumerate([(135,2),(45,2),(152,10),(28,10)]):
            is_atk = self.firing > 0 and (j in (2,3)) and ((j==3 and ca>=0) or (j==2 and ca<0))
            if is_atk:
                ar = self.angle; arm_len = int(30*sc)
            else:
                ar = math.radians(ang_d); arm_len = int(bw*(.76 if j < 2 else .65))
            base_x = ix+int(math.cos(math.radians(ang_d))*bw//4)
            base_y = body_y+(arm_y_off if j < 2 else bh*2//3)
            ax2 = base_x+int(math.cos(ar)*arm_len); ay2 = base_y+int(math.sin(ar)*arm_len*0.55)
            pygame.draw.line(surf, (158,14,14), (base_x, base_y), (ax2, ay2), max(4, int((7 if j < 2 else 6)*sc)))
            pygame.draw.circle(surf, (108,4,4), (ax2, ay2), max(4, int((7 if j < 2 else 6)*sc)))
            pygame.draw.circle(surf, (195,26,26),(ax2, ay2), max(3, int((5 if j < 2 else 4)*sc)))
            if is_atk:
                glow(surf, (255,58,58), ax2, ay2, int(16*sc), 88)
                pygame.draw.circle(surf, (255,98,98), (ax2, ay2), max(3, int(8*sc)))
        hy = body_y-int(12*sc)
        pygame.draw.circle(surf, (86,4,4),  (ix, hy), max(6, int(12*sc))+1)
        pygame.draw.circle(surf, self.col,   (ix, hy), max(6, int(12*sc)))
        for k in range(4):
            ex2 = ix+(k-1)*int(5*sc)-int(2*sc); ey2 = hy-int(2*sc)
            pygame.draw.circle(surf, (252,238,218), (ex2, ey2), max(2, int(3*sc)))
            pygame.draw.circle(surf, (0,0,0),        (ex2, ey2), max(1, int(2*sc)))

    # ── XLR8 ──────────────────────────────────────────────
    def _draw_xlr8(self, surf, ix, iy, t, sc, ca, sa, foot):
        bh = int(24*sc); bw = int(16*sc)
        lean_x = int(ca*3*sc); lean_y = int(sa*2*sc); body_y = foot-bh
        for k in range(4):
            tr_a = self.angle+math.pi+math.radians((k-1.5)*14)
            tlen = int((10+k*8)*sc)
            tx2 = ix+int(math.cos(tr_a)*tlen)+lean_x; ty2 = iy+int(math.sin(tr_a)*tlen*0.62)+lean_y
            if (t//6+k) % 2 == 0:
                pygame.draw.line(surf, (52,162,255), (ix+lean_x, iy+lean_y), (tx2, ty2), max(1, int(2*sc)))
        for side in (-1, 1):
            lx = ix+side*int(5*sc)+lean_x
            pygame.draw.line(surf, (5,14,40),  (lx, foot-int(12*sc)+lean_y), (lx+side*int(4*sc), foot+lean_y), max(2, int(5*sc)))
            pygame.draw.ellipse(surf, (8,20,52), (lx+side*int(1*sc)-int(5*sc), foot-int(2*sc)+lean_y, int(10*sc), int(5*sc)))
        body = pygame.Rect(ix-bw//2+lean_x, body_y+lean_y, bw, bh)
        pygame.draw.rect(surf, (5,12,30),  body, border_radius=int(6*sc))
        pygame.draw.rect(surf, (10,20,55), pygame.Rect(body.x+1,body.y+1,body.w-2,body.h-2), border_radius=int(5*sc))
        pygame.draw.rect(surf, self.col,   pygame.Rect(body.x+2,body.y+2,body.w-4,body.h-4), border_radius=int(4*sc))
        bp = [(body.centerx+int(3*sc),body.y+int(2*sc)),(body.centerx-int(1*sc),body.centery-int(1*sc)),
              (body.centerx+int(3*sc),body.centery-int(1*sc)),(body.centerx-int(2*sc),body.bottom-int(2*sc))]
        pygame.draw.polygon(surf, (255,228,58), bp)
        hy = body_y+lean_y-int(13*sc)
        pygame.draw.circle(surf, (5,12,30), (ix+lean_x, hy), max(5, int(11*sc)))
        vr = pygame.Rect(ix-int(9*sc)+lean_x, hy-int(4*sc), int(18*sc), int(7*sc))
        pygame.draw.rect(surf, (0,70,150),  vr, border_radius=2)
        pygame.draw.rect(surf, (38,158,255),vr, border_radius=2)
        tail_a = self.angle+math.pi
        t1x = ix+int(math.cos(tail_a)*int(8*sc))+lean_x; t1y = iy+int(math.sin(tail_a)*int(5*sc))+lean_y
        t2x = ix+int(math.cos(tail_a)*int(20*sc))+lean_x; t2y = iy+int(math.sin(tail_a)*int(9*sc))+lean_y
        pygame.draw.line(surf, (8,18,50),  (ix+lean_x, iy+lean_y), (t1x, t1y), max(3, int(6*sc)))
        pygame.draw.line(surf, (20,50,108),(t1x, t1y), (t2x, t2y), max(2, int(4*sc)))
        if self.firing > 0:
            fwd_x = ix+int(ca*int(16*sc))+lean_x; fwd_y = iy+int(sa*int(8*sc))+lean_y
            glow(surf, (118,218,255), fwd_x, fwd_y, int(18*sc), 88)
            pygame.draw.circle(surf, (178,235,255), (fwd_x, fwd_y), max(3, int(7*sc)))

    # ── Diamondhead ────────────────────────────────────────
    def _draw_diamondhead(self, surf, ix, iy, t, sc, ca, sa, foot):
        bh = int(34*sc); bw = int(18*sc); body_y = foot-bh
        bc = (30,160,140); bhi = (80,220,200); bdk = (15,90,80)
        for side in (-1, 1):
            lx = ix+side*int(5*sc)
            pygame.draw.line(surf, bdk, (lx, foot-int(12*sc)), (lx, foot), max(3, int(6*sc)))
            pygame.draw.ellipse(surf, (20,105,90), (lx-int(4*sc), foot-int(2*sc), int(8*sc), int(5*sc)))
        pts  = [(ix+int(bw//2*math.cos(math.radians(k*60-90))),
                 body_y+bh//2+int(bh//2*math.sin(math.radians(k*60-90))*.85)) for k in range(6)]
        pygame.draw.polygon(surf, bdk, pts)
        pts2 = [(ix+int((bw//2-2)*math.cos(math.radians(k*60-90))),
                 body_y+bh//2+int((bh//2-2)*math.sin(math.radians(k*60-90))*.85)) for k in range(6)]
        pygame.draw.polygon(surf, bc, pts2)
        facet = [(ix,body_y+int(4*sc)),(ix+bw//2-int(2*sc),body_y+bh//2),
                 (ix,body_y+bh-int(4*sc)),(ix-bw//2+int(2*sc),body_y+bh//2)]
        pygame.draw.polygon(surf, bhi, facet); pygame.draw.polygon(surf, (158,238,226), facet, 1)
        for side in (-1, 1):
            sp_x = ix+side*(bw//2+int(4*sc)); sp_y = body_y+int(6*sc)
            spts = [(sp_x,sp_y-int(16*sc)),(sp_x+side*int(8*sc),sp_y+int(4*sc)),(sp_x-side*int(3*sc),sp_y+int(6*sc))]
            pygame.draw.polygon(surf, bc, spts); pygame.draw.polygon(surf, (158,238,226), spts, 1)
            glow(surf, (100,218,198), sp_x, sp_y-int(5*sc), int(8*sc), 32)
        hy = body_y-int(14*sc)
        hpts  = [(ix,hy-int(14*sc)),(ix+int(11*sc),hy),(ix+int(7*sc),hy+int(10*sc)),(ix-int(7*sc),hy+int(10*sc)),(ix-int(11*sc),hy)]
        hpts2 = [(ix,hy-int(12*sc)),(ix+int(9*sc),hy),(ix+int(6*sc),hy+int(9*sc)), (ix-int(6*sc),hy+int(9*sc)), (ix-int(9*sc),hy)]
        pygame.draw.polygon(surf, bdk, hpts)
        pygame.draw.polygon(surf, bc,  hpts2); pygame.draw.polygon(surf, (148,236,222), hpts2, 1)
        pygame.draw.line(surf, bhi, (ix,hy-int(12*sc)), (ix+int(9*sc),hy), 1)
        pygame.draw.line(surf, bhi, (ix,hy-int(12*sc)), (ix-int(9*sc),hy), 1)
        glow(surf, (118,228,208), ix, hy, int(10*sc), 36)
        for side in (-1, 1):
            pygame.draw.circle(surf, (0,0,0),     (ix+side*int(4*sc), hy+int(2*sc)), max(2, int(3*sc)))
            pygame.draw.circle(surf, (98,238,218),(ix+side*int(4*sc), hy+int(2*sc)), max(1, int(2*sc)))
        arm_side = 1 if ca >= 0 else -1
        arm_base_x = ix+arm_side*int(bw*.44); arm_base_y = body_y+int(8*sc)
        if self.firing > 0:
            clamped_ca = ca; clamped_sa = max(-0.3, min(0.3, sa))
            ax2 = arm_base_x+int(clamped_ca*int(24*sc)); ay2 = arm_base_y+int(clamped_sa*int(14*sc))
        else:
            ax2 = arm_base_x+arm_side*int(16*sc); ay2 = arm_base_y-int(2*sc)
        pygame.draw.line(surf, bdk, (arm_base_x, arm_base_y), (ax2, ay2), max(3, int(7*sc)))
        pygame.draw.line(surf, bc,  (arm_base_x, arm_base_y), (ax2, ay2), max(2, int(5*sc)))
        fpts = [(ax2,ay2-int(7*sc)),(ax2+int(5*sc),ay2),(ax2,ay2+int(5*sc)),(ax2-int(5*sc),ay2)]
        pygame.draw.polygon(surf, bdk, fpts); pygame.draw.polygon(surf, bhi, fpts)
        pygame.draw.polygon(surf, (198,248,238), fpts, 1)
        if self.firing > 0:
            glow(surf, (158,242,232), ax2, ay2, int(16*sc), 88)

    # ── Grandpa Max ────────────────────────────────────────
    def _draw_grandpa(self, surf, ix, iy, t, sc, ca, sa, foot):
        rv_x = ix-int(38*sc); rv_y = iy-int(22*sc)
        rv_w = int(68*sc); rv_h = int(26*sc)
        rv_body = pygame.Rect(rv_x, rv_y, rv_w, rv_h)
        pygame.draw.rect(surf, (210,202,185), rv_body, border_radius=int(3*sc))
        pygame.draw.rect(surf, (195,188,170), rv_body, 1, border_radius=int(3*sc))
        for rx2, ry2, rr2 in [(rv_x+int(8*sc),rv_y+int(18*sc),int(4*sc)),
                               (rv_x+int(20*sc),rv_y+int(20*sc),int(3*sc)),
                               (rv_x+int(38*sc),rv_y+int(19*sc),int(5*sc)),
                               (rv_x+int(55*sc),rv_y+int(17*sc),int(4*sc))]:
            pygame.draw.circle(surf, (148,72,38), (rx2, ry2), max(2, rr2))
        stripe_y = rv_y+int(rv_h*0.38)
        pygame.draw.rect(surf, (60,90,150),   (rv_x+int(1*sc), stripe_y, rv_w-int(2*sc), max(2,int(3*sc))))
        pygame.draw.rect(surf, (200,120,30),  (rv_x+int(1*sc), stripe_y+max(2,int(3*sc)), rv_w-int(2*sc), max(1,int(2*sc))))
        win_h = int(8*sc); win_y = rv_y+int(5*sc)
        for wx in [rv_x+int(12*sc), rv_x+int(26*sc), rv_x+int(40*sc)]:
            win_w = int(9*sc)
            pygame.draw.rect(surf, (40,48,60), (wx,win_y,win_w,win_h), border_radius=1)
            pygame.draw.rect(surf, (55,68,85), (wx,win_y,win_w,win_h), 1, border_radius=1)
        wsh_x = rv_x+int(57*sc)
        pygame.draw.rect(surf, (48,60,78), (wsh_x,rv_y+int(4*sc),int(9*sc),int(12*sc)), border_radius=1)
        pygame.draw.rect(surf, (160,152,138), (rv_x+int(5*sc),rv_y-int(3*sc),rv_w-int(10*sc),max(2,int(3*sc))), border_radius=1)
        pygame.draw.arc(surf, (130,122,108),
                        pygame.Rect(rv_x+int(8*sc),rv_y-int(8*sc),int(10*sc),int(8*sc)),
                        math.radians(0), math.radians(180), max(1,int(2*sc)))
        wheel_y = rv_y+rv_h-int(2*sc)
        for wx in [rv_x+int(10*sc), rv_x+int(20*sc), rv_x+int(44*sc), rv_x+int(54*sc)]:
            wr = max(4, int(6*sc))
            pygame.draw.circle(surf, (30,30,32),  (wx, wheel_y), wr)
            pygame.draw.circle(surf, (60,60,64),  (wx, wheel_y), wr, max(1,int(2*sc)))
            pygame.draw.circle(surf, (80,80,85),  (wx, wheel_y), max(2,wr//2))
        # Body
        bh = int(36*sc); bw = int(26*sc); body_y = foot-bh
        shd(surf, ix, foot+2, int(18*sc), int(6*sc))
        for side in (-1, 1):
            lx = ix+side*int(7*sc); lw = max(4,int(10*sc)); lh = int(16*sc)
            pygame.draw.rect(surf, (48,62,112),  (lx-lw//2,foot-lh,lw,lh), border_radius=int(3*sc))
            pygame.draw.rect(surf, (60,78,138),  (lx-lw//2+1,foot-lh+1,lw-2,lh-2), border_radius=int(2*sc))
        for side in (-1, 1):
            lx = ix+side*int(7*sc); bw2 = max(6,int(12*sc)); bh2 = max(4,int(6*sc))
            pygame.draw.rect(surf, (90,58,28),  (lx-bw2//2,foot-bh2,bw2+side*int(2*sc),bh2), border_radius=int(3*sc))
            pygame.draw.rect(surf, (108,72,36), (lx-bw2//2+1,foot-bh2+1,bw2+side*int(2*sc)-2,bh2-2), border_radius=int(2*sc))
            pygame.draw.ellipse(surf, (60,38,15),(lx-bw2//2,foot-int(3*sc),bw2+side*int(2*sc),int(4*sc)))
        belt_y = foot-int(16*sc)
        pygame.draw.rect(surf, (25,20,15), (ix-bw//2,belt_y,bw,max(2,int(3*sc))), border_radius=1)
        pygame.draw.rect(surf, (160,140,50),(ix-int(3*sc),belt_y,int(6*sc),max(2,int(3*sc))))
        shirt_y = belt_y-int(18*sc)
        shirt_rect = pygame.Rect(ix-bw//2, shirt_y, bw, int(19*sc))
        pygame.draw.rect(surf, (178,38,38), shirt_rect, border_radius=int(4*sc))
        pygame.draw.rect(surf, (195,48,48), pygame.Rect(shirt_rect.x+1,shirt_rect.y+1,shirt_rect.w-2,shirt_rect.h-2), border_radius=int(3*sc))
        pygame.draw.rect(surf, (230,228,222),(ix-int(3*sc),shirt_y,int(6*sc),int(8*sc)), border_radius=2)
        pygame.draw.polygon(surf, (145,28,28),[(ix-int(4*sc),shirt_y),(ix+int(4*sc),shirt_y),(ix,shirt_y+int(7*sc))])
        for fx2, fy2 in [(ix-int(8*sc),shirt_y+int(5*sc)),(ix+int(7*sc),shirt_y+int(6*sc)),
                         (ix-int(5*sc),shirt_y+int(13*sc)),(ix+int(8*sc),shirt_y+int(13*sc)),(ix,shirt_y+int(10*sc))]:
            r_fl = max(3, int(4*sc))
            pygame.draw.circle(surf, (148,28,28), (int(fx2),int(fy2)), r_fl)
            for petal in range(4):
                pa2 = math.radians(petal*90)
                px3 = int(fx2)+int(math.cos(pa2)*r_fl*0.9); py3 = int(fy2)+int(math.sin(pa2)*r_fl*0.9)
                pygame.draw.circle(surf, (148,28,28), (px3,py3), max(2,int(3*sc)))
        for side in (-1, 1):
            arm_a = math.radians(88+side*22)
            arm_base_x = ix+side*int(bw*0.46); arm_base_y = shirt_y+int(4*sc)
            ax2 = arm_base_x+int(math.cos(arm_a)*int(20*sc)); ay2 = arm_base_y+int(math.sin(arm_a)*int(16*sc))
            pygame.draw.line(surf, (178,38,38),(arm_base_x,arm_base_y),(ax2,ay2),max(5,int(9*sc)))
            fa_x = ax2; fa_y = ay2
            fa_x2 = fa_x+int(math.cos(arm_a)*int(8*sc)); fa_y2 = fa_y+int(math.sin(arm_a)*int(8*sc))
            pygame.draw.line(surf, (215,168,125),(fa_x,fa_y),(fa_x2,fa_y2),max(4,int(7*sc)))
            pygame.draw.circle(surf, (205,158,118),(fa_x2,fa_y2),max(3,int(5*sc)))
        hy = shirt_y-int(14*sc); head_r = max(8,int(13*sc))
        pygame.draw.rect(surf, (215,168,125),(ix-int(4*sc),shirt_y-int(5*sc),int(8*sc),int(6*sc)))
        pygame.draw.circle(surf, (195,150,108),(ix,hy),head_r+1)
        pygame.draw.circle(surf, (215,168,125),(ix,hy),head_r)
        pygame.draw.line(surf, (170,128,90),(ix-int(7*sc),hy-int(5*sc)),(ix+int(7*sc),hy-int(5*sc)),max(1,int(2*sc)))
        for k in range(5):
            hx3 = ix-int(8*sc)+k*int(4*sc)
            pygame.draw.rect(surf, (165,162,158),(hx3,hy-head_r-int(3*sc),max(2,int(3*sc)),int(5*sc)))
        pygame.draw.rect(surf, (155,152,148),(ix-int(9*sc),hy-head_r,int(18*sc),int(3*sc)))
        for side in (-1, 1):
            ex2 = ix+side*int(5*sc); ey2 = hy-int(3*sc)
            pygame.draw.ellipse(surf, (60,45,28),(ex2-int(3*sc),ey2-int(2*sc),int(6*sc),int(3*sc)))
            pygame.draw.ellipse(surf, (20,14,8), (ex2-int(2*sc),ey2-int(1*sc),int(4*sc),int(2*sc)))
            pygame.draw.line(surf, (28,22,12),(ex2-int(4*sc),ey2-int(4*sc)),(ex2+int(4*sc),ey2-int(3*sc)),max(1,int(2*sc)))
        pygame.draw.circle(surf, (195,148,105),(ix+int(2*sc),hy+int(2*sc)),max(2,int(3*sc)))
        pygame.draw.arc(surf, (148,100,72),
                        pygame.Rect(ix-int(4*sc),hy+int(5*sc),int(9*sc),int(5*sc)),
                        math.radians(190), math.radians(345), max(1,int(2*sc)))
        pygame.draw.circle(surf, (200,155,115),(ix-head_r+int(1*sc),hy),max(2,int(4*sc)))
        from ben10_defense.data import TOWERS as _T
        if self.income_timer > (_T['grandpa']['income_interval'] * 0.85):
            glow(surf, GOLD, ix, iy-int(20*sc), int(18*sc), 55)

    # ── Ben 10 ─────────────────────────────────────────────
    def _draw_ben10(self, surf, ix, iy, t, sc, ca, sa, foot):
        bh = int(28*sc); bw = int(16*sc); body_y = foot-bh
        shd(surf, ix, foot+2, int(14*sc), int(5*sc))
        for side in (-1, 1):
            lx = ix+side*int(4*sc)
            pygame.draw.line(surf, (40,40,55),  (lx, foot-int(10*sc)), (lx, foot), max(2,int(5*sc)))
            pygame.draw.ellipse(surf, (30,30,42),(lx-int(4*sc),foot-int(3*sc),int(8*sc),int(4*sc)))
        body = pygame.Rect(ix-bw//2, body_y, bw, bh)
        pygame.draw.rect(surf, (0,100,22), body, border_radius=int(5*sc))
        pygame.draw.rect(surf, self.col, pygame.Rect(body.x+1,body.y+1,body.w-2,body.h-2), border_radius=int(4*sc))
        pygame.draw.rect(surf, (0,0,0),  (ix-bw//2+1, body_y+int(bh*.55), bw-2, int(bh*.4)), border_radius=int(2*sc))
        pygame.draw.rect(surf, (15,15,20),(ix-int(2*sc), body_y, int(4*sc), bh-1), border_radius=2)
        for side in (-1, 1):
            arm_a = math.radians(90+side*30)
            ax2 = ix+int(math.cos(arm_a)*int(bw*.72)); ay2 = body_y+bh//3+int(math.sin(arm_a)*int(10*sc))
            pygame.draw.line(surf, (0,120,28),(ix+side*bw//4,body_y+bh//4),(ax2,ay2),max(2,int(5*sc)))
            pygame.draw.circle(surf, (0,90,20),(ax2,ay2),max(2,int(5*sc)))
        omni_x = ix-int(bw*.72); omni_y = body_y+bh//3+int(8*sc)
        glow(surf, OMNI_G, omni_x, omni_y, int(7*sc), 55)
        pygame.draw.circle(surf, (0,50,12),  (omni_x,omni_y), max(3,int(5*sc)))
        pygame.draw.circle(surf, OMNI_G,     (omni_x,omni_y), max(2,int(4*sc)))
        pygame.draw.circle(surf, (0,10,2),   (omni_x,omni_y), max(1,int(2*sc)))
        hy = body_y-int(12*sc)
        pygame.draw.circle(surf, (30,28,20), (ix,hy), max(6,int(10*sc))+1)
        pygame.draw.circle(surf, (200,155,100),(ix,hy), max(6,int(10*sc)))
        for side in (-1, 1):
            pygame.draw.circle(surf, (60,48,28),(ix+side*int(3*sc),hy-int(2*sc)),max(1,int(2*sc)))
        pygame.draw.ellipse(surf, (38,28,15),(ix-int(10*sc),hy-int(12*sc),int(20*sc),int(10*sc)))
        pulse = int(math.sin(t*0.15)*4)
        glow(surf, OMNI_G, ix, iy, int((28+pulse)*sc), 28)

    # ── Idin Tower (Custom Support) ──────────────────────────
    def _draw_idin(self, surf, ix, iy, t, sc, ca, sa, foot):
        bh = int(32*sc); bw = int(22*sc); body_y = foot-bh
        shd(surf, ix, foot+2, int(18*sc), int(6*sc))

        # Photo background
        photo = _get_idin_photo()
        if photo:
            ph_sc = int(80*sc); pulse = int(math.sin(t*0.08)*3)
            ph_img = pygame.transform.scale(photo, (ph_sc, ph_sc))
            # Holographic/Glow effect
            ph_surf = pygame.Surface((ph_sc+8, ph_sc+8), pygame.SRCALPHA)
            pygame.draw.rect(ph_surf, (100,200,255,100), ph_surf.get_rect(), border_radius=int(6*sc))
            ph_surf.blit(ph_img, (4, 4))
            # Perspective tilt/sway
            surf.blit(ph_surf, (ix-ph_sc//2-4, body_y-ph_sc-int(8*sc)+pulse), special_flags=pygame.BLEND_ADD)
            glow(surf, (80,180,255), ix, body_y-ph_sc//2-int(12*sc), int(40*sc), 25)

        # Legs
        for side in (-1, 1):
            lx = ix+side*int(6*sc)
            pygame.draw.line(surf, (20,30,50), (lx, foot-int(12*sc)), (lx, foot), max(3, int(6*sc)))
            pygame.draw.ellipse(surf, (10,15,30), (lx-int(5*sc), foot-int(3*sc), int(10*sc), int(5*sc)))
        
        # Body (Dark blue ribbed sweater)
        body_rect = pygame.Rect(ix-bw//2, body_y, bw, bh)
        pygame.draw.rect(surf, (25,40,75), body_rect, border_radius=int(5*sc))
        # Ribbed effect (vertical lines)
        for rx in range(body_rect.left+2, body_rect.right-2, max(2, int(4*sc))):
            pygame.draw.line(surf, (35,55,100), (rx, body_y+2), (rx, body_y+bh-2))
        
        # White crossbody strap
        strap_pts = [(ix-bw//2, body_y+int(8*sc)), (ix+bw//2, body_y+bh-int(8*sc))]
        pygame.draw.line(surf, (240,240,245), strap_pts[0], strap_pts[1], max(2, int(5*sc)))
        
        # Silver chain necklace
        neck_y = body_y+int(5*sc)
        pygame.draw.arc(surf, (190,195,210), (ix-int(6*sc), neck_y-int(3*sc), int(12*sc), int(8*sc)), math.pi, 2*math.pi, max(1, int(2*sc)))
        
        # Arms
        for side in (-1, 1):
            arm_a = math.radians(90+side*25 + math.sin(t*0.1)*5)
            ax2 = ix+side*int(bw*0.55); ay2 = body_y+int(8*sc)
            fx2 = ax2+int(math.cos(arm_a)*int(18*sc)); fy2 = ay2+int(math.sin(arm_a)*int(14*sc))
            pygame.draw.line(surf, (25,40,75), (ax2, ay2), (fx2, fy2), max(4, int(8*sc)))
            pygame.draw.circle(surf, (215,168,125), (fx2, fy2), max(3, int(5*sc)))
            
        # Head
        hy = body_y-int(14*sc); head_r = max(8, int(12*sc))
        pygame.draw.circle(surf, (215,168,125), (ix, hy), head_r)
        
        # Hair (Short black, styled upwards)
        hair_pts = [(ix-head_r-1, hy), (ix-head_r, hy-int(6*sc)), (ix-int(4*sc), hy-head_r-int(6*sc)), 
                    (ix, hy-head_r-int(8*sc)), (ix+int(4*sc), hy-head_r-int(6*sc)), 
                    (ix+head_r, hy-int(4*sc)), (ix+head_r+1, hy)]
        pygame.draw.polygon(surf, (20,18,15), hair_pts)
        
        # Eyes
        for side in (-1, 1):
            ex2 = ix+side*int(4*sc); ey2 = hy-int(2*sc)
            pygame.draw.circle(surf, (30,25,20), (ex2, ey2), max(1, int(2*sc)))
            
        # Float glow if income logic
        from ben10_defense.data import TOWERS as _T
        if self.income_timer > (_T['idin']['income_interval'] * 0.85):
            glow(surf, GOLD, ix, iy-int(20*sc), int(22*sc), 65)
