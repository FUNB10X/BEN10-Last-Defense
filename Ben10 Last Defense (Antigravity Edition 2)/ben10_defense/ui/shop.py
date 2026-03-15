"""
shop.py — draw_shop(), draw_tower_panel() — side-panel shop and tower info popup.
Depends on: config, data (TOWERS, DIFFICULTIES, CURRENT_DIFF, T_KEYS_P1/2),
            draw_utils, font_lang.
"""
import pygame

from ben10_defense.config import (
    SW, SH, UI_H, GW, GH, SHOP_X, SHOP_W, SHOP_BG, SHOP_LN, WHITE, GOLD, OMNI_G,
)
from ben10_defense.data import TOWERS, DIFFICULTIES, CURRENT_DIFF, T_KEYS_P1, T_KEYS_P2
from ben10_defense.draw_utils import rrect, dtxt, dtxt_bg
from ben10_defense.font_lang import Fk, LANG, tr
from ben10_defense.entities.tower import Tower

SLOT_H = 134
SPAD   = 12


def draw_tower_panel(surf, tower, money, mx, my, moving=False):
    """Draw popup info/upgrade/sell panel next to clicked tower.
    Returns (upgrade_r, move_r, sell_r, close_r, upgrade_cost).
    """
    PANEL_W = 210; PANEL_H = 220
    px = int(tower.x) + 32; py = int(tower.y) - PANEL_H//2
    if px + PANEL_W > GW: px = int(tower.x) - PANEL_W - 32
    py = max(UI_H+4, min(SH - PANEL_H - 4, py))

    bg_s = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.rect(bg_s, (10,16,36,220), bg_s.get_rect(), border_radius=10)
    pygame.draw.rect(bg_s, (50,80,160,200), bg_s.get_rect(), 2, border_radius=10)
    surf.blit(bg_s, (px, py))

    d = TOWERS[tower.kind]; tc = tower.col
    dtxt_bg(surf, tr(d['name']), 'ml', tc, px+PANEL_W//2, py+18)
    lv_col = [(255,255,255),(255,200,50),(100,220,100),(100,180,255),(255,120,20),(220,50,220)][tower.level]
    dtxt(surf, f"Lv.{tower.level}/5", 's', lv_col, px+PANEL_W//2, py+38)

    # Stat bars
    bar_y = py+54; bw = PANEL_W-28
    for lbl, val, maxv, col2 in [
        (('DMG','ดาเมจ'), tower.dmg, 60, (255,80,80)),
        (('RNG','รัศมี'), tower.rng, 220, (80,180,255)),
        (('RATE','ยิง'), 60//max(1,tower.rate)*10, 30, (80,220,80)),
    ]:
        label = lbl[1] if LANG[0] == 'th' else lbl[0]
        dtxt(surf, label, 'xs', (140,155,185), px+14, bar_y, 'topleft')
        fill_w = int(min(1.0, val/maxv) * bw)
        rrect(surf, (25,32,52), (px+14, bar_y+14, bw, 5), 2)
        rrect(surf, col2,       (px+14, bar_y+14, fill_w, 5), 2)
        bar_y += 26

    # Ability hint
    desc_list = Tower.UPGRADE_DESC.get(tower.kind, [])
    if tower.level >= 1 and tower.level-1 < len(desc_list):
        spec = desc_list[tower.level-1]
        if spec:
            dtxt_bg(surf, spec, 'xs', (200,210,240), px+PANEL_W//2, bar_y+4, pad=4, bg=(0,0,0,140))
    bar_y += 20

    # Button row
    BTN_W = 62; BTN_H = 28; BT_Y = py+PANEL_H-38
    upgrade_cost = (Tower.UPGRADE_COSTS.get(tower.kind, [])[tower.level-1]
                    if tower.level < 5 else 0)
    sell_val = tower.sell_value()

    # Upgrade
    up_r  = pygame.Rect(px+6, BT_Y, BTN_W, BTN_H)
    can_up = tower.level < 5 and upgrade_cost > 0 and money >= upgrade_cost
    up_col = (0,120,35) if can_up else (35,40,55)
    up_bdr = (0,200,50) if can_up else (50,58,80)
    rrect(surf, up_col, up_r, 6); pygame.draw.rect(surf, up_bdr, up_r, 1, border_radius=6)
    if tower.level >= 5:
        dtxt(surf, 'MAX', 'xs', (180,140,50), up_r.centerx, up_r.centery)
    elif upgrade_cost <= 0:
        dtxt(surf, 'MAX', 'xs', (140,140,140), up_r.centerx, up_r.centery)
    else:
        upg_lbl = 'อัพ' if LANG[0] == 'th' else 'UPG'
        dtxt(surf, upg_lbl, 'xs', WHITE if can_up else (100,108,120), up_r.centerx, up_r.y+7)
        dtxt(surf, f"${upgrade_cost}", 'xs', GOLD if can_up else (90,80,40), up_r.centerx, up_r.y+18)

    # Move
    mv_r  = pygame.Rect(px+6+BTN_W+4, BT_Y, BTN_W, BTN_H)
    mv_col = (0,80,160) if not moving else (0,140,200)
    mv_bdr = (50,140,255) if not moving else (80,200,255)
    rrect(surf, mv_col, mv_r, 6); pygame.draw.rect(surf, mv_bdr, mv_r, 1, border_radius=6)
    mv_lbl = 'ย้าย' if LANG[0] == 'th' else 'MOVE'
    dtxt(surf, mv_lbl, 'xs', WHITE, mv_r.centerx, mv_r.centery)

    # Sell
    sl_r  = pygame.Rect(px+6+BTN_W*2+8, BT_Y, BTN_W, BTN_H)
    rrect(surf, (120,20,20), sl_r, 6); pygame.draw.rect(surf, (200,40,40), sl_r, 1, border_radius=6)
    sl_lbl = 'ขาย' if LANG[0] == 'th' else 'SELL'
    dtxt(surf, sl_lbl, 'xs', WHITE, sl_r.centerx, sl_r.y+7)
    dtxt(surf, f"+${sell_val}", 'xs', (255,200,50), sl_r.centerx, sl_r.y+18)

    # Close X
    close_r = pygame.Rect(px+PANEL_W-20, py+4, 16, 16)
    rrect(surf, (60,20,20), close_r, 4)
    dtxt(surf, 'x', 'xs', (220,80,80), close_r.centerx, close_r.centery)

    return up_r, mv_r, sl_r, close_r, upgrade_cost


def draw_shop(surf, money, selected, mx, my, page, towers_placed):
    """Draw the right-side shop panel. Returns (p1_rect, p2_rect) page buttons."""
    rrect(surf, SHOP_BG, (SHOP_X, UI_H, SHOP_W, GH), 0)
    pygame.draw.line(surf, SHOP_LN, (SHOP_X, UI_H), (SHOP_X, SH))
    dtxt(surf, tr("SHOP"), 'l', OMNI_G, SHOP_X+SHOP_W//2, UI_H+22, shad=True)
    pygame.draw.line(surf, SHOP_LN, (SHOP_X+12, UI_H+44), (SW-12, UI_H+44))

    keys = T_KEYS_P1 if page == 0 else T_KEYS_P2
    for i, key in enumerate(keys):
        d = TOWERS[key]; sy = UI_H+56+i*SLOT_H
        sr = pygame.Rect(SHOP_X+SPAD, sy, SHOP_W-SPAD*2, SLOT_H-8)
        cnt    = sum(1 for t in towers_placed if t.kind == key)
        at_max = cnt >= d.get('max_count', 99)
        can    = money >= d['cost'] and not at_max
        sel    = selected == key; hov = sr.collidepoint(mx, my)
        bg  = (20,50,100) if sel else (22,32,54) if (hov and can) else (18,20,32) if not can else (16,24,44)
        bc2 = OMNI_G if sel else (60,90,160) if (hov and can) else (40,42,60) if not can else (40,65,120)
        rrect(surf, bg, sr, 8); pygame.draw.rect(surf, bc2, sr, 1, border_radius=8)
        # Icon
        sw_r = pygame.Rect(sr.x+8, sr.y+8, 38, 38)
        rrect(surf, (8,12,24), sw_r, 6)
        pygame.draw.circle(surf, d['col'], (sw_r.centerx, sw_r.centery), 14)
        nc = WHITE if can else (100,100,120)
        # Name (clip to slot width)
        _nm_s = Fk()['m'].render(tr(d['name']), True, nc)
        _max_w = sr.w - 60
        if _nm_s.get_width() > _max_w:
            _nm_s = pygame.transform.scale(_nm_s, (_max_w, _nm_s.get_height()))
        surf.blit(_nm_s, (sr.x+54, sr.y+14))
        _ds_s = Fk()['xs'].render(tr(d['desc']), True, (140,148,170))
        if _ds_s.get_width() > _max_w:
            _ds_s = pygame.transform.scale(_ds_s, (_max_w, _ds_s.get_height()))
        surf.blit(_ds_s, (sr.x+54, sr.y+34))
        bar_y = sr.y+56
        if d['income']:
            dtxt(surf, f"Earn: ${d['income_amt']} / {int(d['income_interval'])}s",
                 's', GOLD, sr.x+54, bar_y+4, 'topleft')
            if key == 'ben10':
                dtxt(surf, f"ATK ×{2**(min(3,cnt+1))} when placed",
                     'xs', (120,220,140), sr.x+54, bar_y+20, 'topleft')
                dtxt(surf, f"Placed: {cnt}/3",
                     'xs', (160,170,190), sr.x+54, bar_y+36, 'topleft')
        else:
            for j, (lbl, val, mx2) in enumerate([('DMG',d['dmg'],45),('RNG',d['rng'],210),('RATE',60//d['rate']*10,6)]):
                # Increased horizontal spacing from 58 to 61
                bx3 = sr.x+52+j*61
                dtxt(surf, lbl, 'xs', (120,130,155), bx3, bar_y, 'topleft')
                # Slightly narrow bar (46 -> 42) to ensure space between columns
                bw = 42; fill = int(min(1.0, val/mx2)*bw)
                # Dropped bars down from 14 to 19 to respect spacing
                rrect(surf, (30,35,55), (bx3, bar_y+19, bw, 5), 2)
                rrect(surf, d['col'],   (bx3, bar_y+19, fill, 5), 2)
        cost_s = Fk()['ml'].render("$"+str(d['cost']), True, GOLD if can else (90,80,40))
        surf.blit(cost_s, cost_s.get_rect(bottomright=(sr.right-8, sr.bottom-8)))
        if at_max:   dtxt(surf, tr("MAX"), 'xs', (220,80,80), sr.centerx, sr.bottom-14)
        elif sel:    dtxt(surf, tr("CLICK MAP TO PLACE"), 'xs', OMNI_G, sr.centerx, sr.bottom-14)

    # Page toggle buttons
    by3 = UI_H+56+len(keys)*SLOT_H
    pygame.draw.line(surf, SHOP_LN, (SHOP_X+12, by3), (SW-12, by3))
    p1_r = pygame.Rect(SHOP_X+12,         by3+8, SHOP_W//2-18, 28)
    p2_r = pygame.Rect(SHOP_X+SHOP_W//2+4, by3+8, SHOP_W//2-16, 28)
    for pr, lbl, pg in [(p1_r, tr("Aliens"), 0), (p2_r, tr("Support"), 1)]:
        col2 = OMNI_G if page == pg else (50,70,110)
        rrect(surf, col2, pr, 6)
        dtxt(surf, lbl, 'xs', WHITE, pr.centerx, pr.centery)

    diff_col = DIFFICULTIES[CURRENT_DIFF[0]]['col']
    dtxt(surf, DIFFICULTIES[CURRENT_DIFF[0]]['label'], 'xs', diff_col, SHOP_X+SHOP_W//2, by3+46)
    dtxt(surf, tr("Hover: range · ESC: cancel"), 'xs', (60,68,95), SHOP_X+SHOP_W//2, by3+62)
    return p1_r, p2_r
