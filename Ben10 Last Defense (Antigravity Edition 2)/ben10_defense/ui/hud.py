"""
hud.py — draw_hud() — top status bar with HP, money, wave, enemy count, boss bar.
Depends on: config, data (DIFFICULTIES, CURRENT_DIFF), draw_utils, font_lang.
"""
import pygame

from ben10_defense.config import (
    SW, UI_H, GW, HUD_BG, HUD_LINE, WHITE, GOLD, OMNI_G, HP_G, HP_O, HP_R,
)
from ben10_defense.data import DIFFICULTIES, CURRENT_DIFF
from ben10_defense.draw_utils import rrect, dtxt, dtxt_bg, glow
from ben10_defense.font_lang import tr


def draw_hud(surf, hp, max_hp, money, wave, total_waves, eleft,
             boss_on_field=None, ben_count=0):
    rrect(surf, HUD_BG, (0, 0, SW, UI_H), 0)
    pygame.draw.line(surf, HUD_LINE, (0, UI_H-1), (SW, UI_H-1))

    # Earth HP bar
    ratio = max(0.0, hp / max_hp)
    hc = HP_G if ratio > .5 else HP_O if ratio > .25 else HP_R
    dtxt(surf, tr("EARTH HP"), 'xs', (140,148,175), 14, 11, 'topleft')
    rrect(surf, (28,6,6),             (14, 26, 148, 20), 5)
    rrect(surf, hc,                   (14, 26, int(148*ratio), 20), 5)
    pygame.draw.rect(surf, (100,100,120), (14, 26, 148, 20), 1, border_radius=5)
    dtxt(surf, str(hp), 'xs', WHITE, 90, 36)

    pygame.draw.line(surf, HUD_LINE, (175, 6), (175, UI_H-6))
    dtxt(surf, tr("MONEY"), 'xs', (140,148,175), 188, 11, 'topleft')
    dtxt(surf, "$"+str(money), 'ml', GOLD, 265, 36)

    pygame.draw.line(surf, HUD_LINE, (325, 6), (325, UI_H-6))
    dtxt(surf, tr("WAVE"), 'xs', (140,148,175), 338, 11, 'topleft')
    dtxt(surf, f"{wave} / {total_waves}", 'ml', (100,190,255), 398, 36)

    pygame.draw.line(surf, HUD_LINE, (468, 6), (468, UI_H-6))
    dtxt(surf, tr("ENEMIES"), 'xs', (140,148,175), 480, 11, 'topleft')
    dtxt(surf, str(eleft), 'ml', (220,80,80), 540, 36)

    # Ben ATK boost indicator
    if ben_count > 0:
        pygame.draw.line(surf, HUD_LINE, (590, 6), (590, UI_H-6))
        mult = 2 ** min(ben_count, 3)
        dtxt(surf, tr("ATK BOOST"), 'xs', (120,220,140), 610, 11, 'topleft')
        dtxt(surf, f"×{mult}", 'ml', OMNI_G, 638, 36)

    # Boss HP bar (floating above HUD)
    if boss_on_field:
        br = boss_on_field.hp / boss_on_field.mhp
        bw2 = 280; bx3 = (GW-bw2)//2; by3 = UI_H-20
        glow(surf, (200,0,0), bx3+bw2//2, by3+8, bw2//2+10, 22)
        rrect(surf, (60,0,0),   (bx3-2, by3-2, bw2+4, 18), 4)
        rrect(surf, (220,20,20),(bx3, by3, int(bw2*br), 14), 3)
        pygame.draw.rect(surf, (180,0,0), (bx3, by3, bw2, 14), 1, border_radius=3)
        dtxt_bg(surf, f"VILGAX  {boss_on_field.hp}/{boss_on_field.mhp}",
                'xs', (255,80,80), bx3+bw2//2, by3+7)

    # Omnitrix badge (right of HUD)
    pygame.draw.circle(surf, (0,120,30),  (SW-50, UI_H//2), 22)
    pygame.draw.circle(surf, (0,200,50),  (SW-50, UI_H//2), 18)
    pygame.draw.circle(surf, (0,30,8),    (SW-50, UI_H//2), 10)
    diff_lbl = tr(DIFFICULTIES[CURRENT_DIFF[0]]['label'])
    dtxt(surf, diff_lbl, 'xs', DIFFICULTIES[CURRENT_DIFF[0]]['col'], SW-105, UI_H//2)
