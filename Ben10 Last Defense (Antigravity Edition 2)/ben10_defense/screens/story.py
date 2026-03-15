"""
story.py — story() screen: scrolling backstory text before game starts.
Depends on: config, draw_utils, font_lang, sound, ui/lang_btn.
"""
import sys
import math
import random
import pygame

from ben10_defense.config import screen, clock, SW, SH, FPS, UI_H
from ben10_defense.draw_utils import glow, lerp_col
from ben10_defense.font_lang import LANG, Fk, tr
from ben10_defense.sound import play_music


def story():
    play_music('menu_bgm', 0.42)
    tick   = 0
    star_s = [(random.randint(0,SW), random.randint(0,SH), random.randint(1,3))
              for _ in range(160)]

    while True:
        clock.tick(FPS); tick += 1
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN): return

        # Lines rebuilt each frame so live language-switch works
        LINES = [
            (tr("SEASON 4 : FINAL WAR"),                           'xl',  (0,220,55)),
            ("",                                                    'xs',  (0,0,0)),
            (tr("Alien armies are invading Earth."),                'ml',  (200,210,235)),
            (tr("Cities are burning.  Defenses have fallen."),      'ml',  (200,210,235)),
            ("",                                                    'xs',  (0,0,0)),
            (tr("Ben Tennyson activates the Omnitrix..."),          'm',   (180,190,215)),
            (tr("...and stands between humanity and extinction."),  'm',   (180,190,215)),
            ("",                                                    'xs',  (0,0,0)),
            (tr("The mastermind of this invasion:"),                'ml',  (220,100,100)),
            ("",                                                    'xs',  (0,0,0)),
            (tr("V I L G A X"),                                     'xxl', (230,20,20)),
            ("",                                                    'xs',  (0,0,0)),
            (tr("[ Click or press any key ]"),                      'm',   (100,200,255)),
        ]

        for y in range(SH):
            pygame.draw.line(screen, lerp_col((4,4,14),(6,14,28),y/SH), (0,y), (SW,y))
        for sx, sy, sr in star_s:
            br = 140+int(math.sin(tick*0.04+sx*0.01)*80)
            pygame.draw.circle(screen, (br,br,br), (sx,sy), sr)

        fdict = Fk(); GAP = 10
        total_h = sum(fdict[l[1]].get_height()+GAP for l in LINES)
        cy = max(UI_H+10, (SH-total_h)//2)
        mx2, my2 = pygame.mouse.get_pos()

        for text, fk2, col in LINES:
            if text:
                if fk2 == 'xxl':
                    glow(screen, (180,0,0), SW//2, cy+fdict[fk2].get_height()//2, 160, 22)
                sc2 = 1.0+0.025*math.sin(tick*0.07) if fk2 == 'xxl' else 1.0
                s = fdict[fk2].render(text, True, col)
                if sc2 != 1.0:
                    s = pygame.transform.scale(s, (int(s.get_width()*sc2), int(s.get_height()*sc2)))
                screen.blit(s, s.get_rect(centerx=SW//2, top=cy))
            cy += fdict[fk2].get_height()+GAP

        pygame.display.flip()
