"""
lang_btn.py — draw_lang_btn() — TH/EN language toggle buttons in the HUD.
Depends on: config, draw_utils, font_lang.
"""
import pygame

from ben10_defense.config import SW, UI_H
from ben10_defense.draw_utils import rrect
from ben10_defense.font_lang import Fk, LANG


def draw_lang_btn(surf, mx, my):
    """Draw language buttons, return (th_rect, en_rect)."""
    bw = 82; bh = 24; gap = 5
    right_edge = SW - 8
    btn_y = (UI_H - bh) // 2
    en_r = pygame.Rect(right_edge - bw,          btn_y, bw, bh)
    th_r = pygame.Rect(right_edge - bw*2 - gap,  btn_y, bw, bh)

    lbl_s = Fk()['xs'].render('ภาษา :', True, (140,155,195))
    surf.blit(lbl_s, (th_r.x - lbl_s.get_width() - 6,
                      btn_y + (bh - lbl_s.get_height())//2))

    for r2, lang_code, lbl_txt in [
        (th_r, 'th', 'TH/ไทย'),
        (en_r, 'en', 'EN/อังกฤษ'),
    ]:
        active = LANG[0] == lang_code
        hov    = r2.collidepoint(mx, my)
        if active:
            bg = (0,130,38); border = (0,200,55)
        elif hov:
            bg = (30,48,95); border = (65,105,195)
        else:
            bg = (16,24,48); border = (38,60,125)
        rrect(surf, bg, r2, 6)
        pygame.draw.rect(surf, border, r2, 2, border_radius=6)
        tc = (255,255,255) if active else (155,170,210) if hov else (115,132,175)
        ls = Fk()['xs'].render(lbl_txt, True, tc)
        surf.blit(ls, (r2.centerx - ls.get_width()//2,
                       r2.centery - ls.get_height()//2))
        if active:
            pygame.draw.line(surf, (0,220,55),
                             (r2.x+4, r2.bottom-3), (r2.right-4, r2.bottom-3), 2)

    return th_r, en_r
