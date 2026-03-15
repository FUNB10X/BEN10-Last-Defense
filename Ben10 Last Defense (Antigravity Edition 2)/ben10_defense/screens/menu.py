"""
menu.py — menu() screen: animated starfield + BEN 10 title + PLAY/QUIT buttons.
Depends on: config, draw_utils, font_lang, sound, ui/lang_btn.
"""
import sys
import math
import random
import pygame

from ben10_defense.config import screen, clock, SW, SH, FPS, WHITE, ADMIN_UNLOCKED
from ben10_defense.draw_utils import dtxt, rrect, glow, lerp_col
from ben10_defense.font_lang import LANG, tr
from ben10_defense.sound import sfx, play_music
from ben10_defense.screens.settings import settings


def menu():
    play_music('menu_bgm', 0.42)
    stars   = [(random.randint(0,SW), random.randint(0,SH), random.uniform(.2,1.4), random.randint(1,3))
               for _ in range(220)]
    meteors = []; met_t = 0; t = 0
    play_r  = pygame.Rect(SW//2-95, SH//2+68,  190, 52)
    sett_r  = pygame.Rect(SW//2-95, SH//2+128, 190, 48)
    quit_r  = pygame.Rect(SW//2-95, SH//2+184, 190, 44)

    # Admin access state
    admin_clicks     = 0
    admin_input_open = False
    admin_input_text = ""
    ring_y = SH//2+34
    omni_r = pygame.Rect(SW//2-30, ring_y-30, 60, 60)

    while True:
        clock.tick(FPS); t += 1; mx, my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if admin_input_open: admin_input_open = False
                    else: pygame.quit(); sys.exit()
                # Admin password input
                if admin_input_open:
                    if ev.key == pygame.K_BACKSPACE:
                        admin_input_text = admin_input_text[:-1]
                    elif ev.key == pygame.K_RETURN:
                        if admin_input_text == "67":
                            ADMIN_UNLOCKED[0] = True; sfx('win')
                        admin_input_open = False; admin_input_text = ""
                        continue
                    else:
                        if ev.unicode and len(admin_input_text) < 10:
                            admin_input_text += ev.unicode
                    continue

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if admin_input_open: continue
                if play_r.collidepoint(ev.pos): sfx('click', 0.35); return
                if sett_r.collidepoint(ev.pos): sfx('click', 0.35); settings(); play_music('menu_bgm', 0.42); continue
                if quit_r.collidepoint(ev.pos): sfx('click', 0.35); pygame.quit(); sys.exit()
                if omni_r.collidepoint(ev.pos):
                    sfx('click', 0.2)
                    admin_clicks += 1
                    if admin_clicks >= 5:
                        admin_input_open = True; admin_clicks = 0

        # Background gradient
        for y in range(SH):
            pygame.draw.line(screen, lerp_col((5,5,18),(8,18,38),y/SH), (0,y), (SW,y))
        # Meteors
        met_t += 1
        if met_t > 75:
            met_t = 0
            meteors.append({'x':float(random.randint(50,SW-50)), 'y':float(random.randint(0,SH//3)),
                            'vx':random.uniform(2,5), 'vy':random.uniform(1,3), 'life':60, 'ml':60})
        for m in meteors[:]:
            m['x'] += m['vx']; m['y'] += m['vy']; m['life'] -= 1
            if m['life'] <= 0: meteors.remove(m); continue
            a = m['life']/m['ml']
            pygame.draw.line(screen, tuple(int(200*a) for _ in range(3)),
                             (int(m['x']),int(m['y'])),
                             (int(m['x']-m['vx']*6),int(m['y']-m['vy']*6)), 2)
        # Stars
        for sx, sy, sp, sr in stars:
            tw = 0.5+0.5*math.sin(t*sp*0.08+sx); br = int(tw*210+30)
            pygame.draw.circle(screen, (br,br,br), (int(sx),int(sy)), sr)
        # Title
        glow(screen, (0,200,50), SW//2, SH//2-148, 65, 18)
        wb = int(math.sin(t*0.055)*4)
        dtxt(screen, "BEN 10",      'ttl', (0,210,55),   SW//2, SH//2-148+wb, shad=True)
        dtxt(screen, "Last Defense",'xl',  (255,200,50),  SW//2, SH//2-78+wb,  shad=True)
        dtxt(screen, tr("Tower Defense  |  6 Towers  |  3 Difficulties"),
             's', (120,140,180), SW//2, SH//2-14)
        # Omnitrix ring
        ring_y = SH//2+34
        for i in range(12):
            a2 = math.radians(i*30+t*1.5)
            cx2 = SW//2+int(math.cos(a2)*28); cy2 = ring_y+int(math.sin(a2)*28)
            br  = 180+int(math.sin(t*0.1+i)*50)
            pygame.draw.circle(screen, (0,br,40), (cx2,cy2), 3)
        pygame.draw.circle(screen, (0,120,30), (SW//2,ring_y), 24)
        pygame.draw.circle(screen, (0,210,50), (SW//2,ring_y), 19)
        pygame.draw.circle(screen, (0,30,8),   (SW//2,ring_y), 10)
        # Buttons
        for rect, lbl in [(play_r, tr(" PLAY")), (sett_r, tr("SETTINGS")), (quit_r, tr("QUIT"))]:
            hov = rect.collidepoint(mx, my)
            if hov:
                glow(screen, (0,255,100), rect.centerx, rect.centery, 110, 30)
            rrect(screen, (0,165,58) if hov else (0,90,22), rect, 10)
            pygame.draw.rect(screen, (0,255,75) if hov else (0,165,42), rect, 2, border_radius=10)
            dtxt(screen, lbl, 'l' if rect != sett_r else 'ml', WHITE, rect.centerx, rect.centery, shad=True)
        
        # Admin Prompt Overlay
        if admin_input_open:
            over = pygame.Surface((SW,SH), pygame.SRCALPHA); over.fill((0,0,0,180))
            screen.blit(over, (0,0))
            pm_r = pygame.Rect(SW//2-150, SH//2-60, 300, 100)
            rrect(screen, (30,30,45), pm_r, 12)
            pygame.draw.rect(screen, (0,200,255), pm_r, 2, 12)
            dtxt(screen, "ENTER CODE", 's', (0,200,255), SW//2, SH//2-35)
            t_r = pygame.Rect(SW//2-80, SH//2-10, 160, 40)
            pygame.draw.rect(screen, (20,20,30), t_r, 0, 6)
            pygame.draw.rect(screen, (100,100,120), t_r, 1, 6)
            dtxt(screen, admin_input_text + ("|" if (pygame.time.get_ticks()//500)%2 else ""), 'm', WHITE, SW//2, SH//2+10)

        dtxt(screen, tr("Click to place towers  |  ESC: deselect  |  Hover tower: range"),
             'xs', (65,75,95), SW//2, SH-22)
        dtxt(screen, 'V.3.4 (FINAL)', 'xs', (0,150,50), SW-50, SH-22)
        pygame.display.flip()
