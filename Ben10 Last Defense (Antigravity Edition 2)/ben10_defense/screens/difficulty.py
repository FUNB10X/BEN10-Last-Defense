"""
difficulty.py — choose_difficulty() screen: animated 3-card difficulty selector.
Depends on: config, data, draw_utils, font_lang, sound, ui/lang_btn.
"""
import sys
import math
import random
import pygame

from ben10_defense.config import screen, clock, SW, SH, FPS
from ben10_defense.data import DIFFICULTIES
from ben10_defense.draw_utils import dtxt, rrect, glow, lerp_col
from ben10_defense.font_lang import LANG, tr
from ben10_defense.sound import sfx, play_music


def choose_difficulty():
    play_music('menu_bgm', 0.42)
    card_w = 270; card_h = 360; gap = 28
    total_w = 3*card_w + 2*gap; start_x = (SW-total_w)//2
    rects = [pygame.Rect(start_x+i*(card_w+gap), (SH-card_h)//2, card_w, card_h) for i in range(3)]
    keys  = ['easy', 'normal', 'hard']
    t = 0
    star_s = [(random.randint(0,SW), random.randint(0,SH), random.randint(1,3)) for _ in range(120)]

    def info():
        return {
            'easy':   [tr("10 Waves"),tr("Fewer enemies"),tr("Low HP & slow"),tr("Generous income"),tr("Boss on Wave 10")],
            'normal': [tr("20 Waves"),tr("Standard count"),tr("Normal HP/speed"),tr("Normal income"),tr("Boss on Wave 20")],
            'hard':   [tr("30 Waves"),tr("Many enemies"),tr("High HP & fast"),tr("Scarce money"),tr("Boss at Wave 15 & 30")],
        }

    while True:
        clock.tick(FPS); t += 1; mx, my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: return 'easy'
                if ev.key == pygame.K_2: return 'normal'
                if ev.key == pygame.K_3: return 'hard'
                if ev.key == pygame.K_ESCAPE: return 'normal'
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(ev.pos): sfx('click',0.35); return keys[i]

        for y in range(SH):
            pygame.draw.line(screen, lerp_col((5,5,18),(8,18,38),y/SH), (0,y), (SW,y))
        for sx, sy, sr in star_s:
            br = 130+int(math.sin(t*0.04+sx*0.01)*80)
            pygame.draw.circle(screen, (br,br,br), (sx,sy), sr)
        dtxt(screen, tr("SELECT DIFFICULTY"), 'xl', (200,215,245), SW//2, 55, shad=True)
        dtxt(screen, tr("Press 1 / 2 / 3  or  click"), 's', (90,100,130), SW//2, SH-28)

        card_info = info()
        for i, (r, key) in enumerate(zip(rects, keys)):
            d = DIFFICULTIES[key]; hov = r.collidepoint(mx, my)
            sc2 = 1.0+0.06*math.sin(t*0.12+i*1.2) if hov else 1.0
            rw = int(r.w*sc2); rh = int(r.h*sc2)
            rr = pygame.Rect(r.centerx-rw//2, r.centery-rh//2, rw, rh)
            glow(screen, d['col'], rr.centerx, rr.centery, rw//2+16, 22 if hov else 10)
            rrect(screen, (18,26,44) if hov else (14,20,36), rr, 12)
            pygame.draw.rect(screen, d['col'], rr, 2 if not hov else 3, border_radius=12)
            dtxt(screen, f"[{i+1}]", 'xs', (120,135,165), rr.x+12, rr.y+12, 'topleft')
            dtxt(screen, d['label'], 'xl', d['col'], rr.centerx, rr.y+44, shad=True)
            dtxt(screen, tr(d['sub']), 'm', (180,190,215), rr.centerx, rr.y+88)
            for j, line in enumerate(card_info[key]):
                dtxt(screen, "· "+line, 's',
                     (200,215,235) if hov else (145,155,175), rr.centerx, rr.y+120+j*32)
            dtxt(screen, tr("Start:")+f" ${d['money']}", 'm', (255,210,50), rr.centerx, rr.bottom-36)
            dtxt(screen, tr("Base HP:")+f" {d['bhp']}", 'xs', (100,220,120), rr.centerx, rr.bottom-18)
        pygame.display.flip()
