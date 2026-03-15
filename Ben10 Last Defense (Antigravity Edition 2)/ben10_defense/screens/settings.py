"""
settings.py — Audio volume sliders and language toggle screen.
"""
import sys
import pygame
from ben10_defense.config import screen, clock, SW, SH, FPS, BG, GOLD, WHITE
from ben10_defense.font_lang import tr, LANG
from ben10_defense.sound import sfx, update_music_volume
import ben10_defense.sound as sound_mod
from ben10_defense.draw_utils import dtxt, dtxt_bg, rrect, glow

def draw_slider(surf, x, y, w, h, val, label, hov):
    """Draws a horizontal slider. val is 0.0 to 1.0."""
    pygame.draw.rect(surf, (40, 50, 60), (x, y, w, h), border_radius=h//2)
    fill_w = int(w * val)
    if fill_w > 0:
        col = (100, 200, 255) if hov else (80, 160, 200)
        pygame.draw.rect(surf, col, (x, y, fill_w, h), border_radius=h//2)
    
    # Knob
    kx = x + fill_w
    pygame.draw.circle(surf, WHITE if hov else (220, 220, 220), (kx, y + h//2), h)
    
    # Label & Value
    dtxt_bg(surf, label, 'm', WHITE, x, y - 25)
    dtxt_bg(surf, f"{int(val * 100)}%", 'm', WHITE, x + w + 30, y + h//2, anch='midleft')

def settings():
    # Initial states
    bgm_val = sound_mod.MASTER_BGM
    sfx_val = sound_mod.MASTER_SFX
    
    dragging = None  # 'bgm' or 'sfx'
    
    # Layout config
    sl_w = 400
    sl_h = 16
    cx = SW // 2 - sl_w // 2
    
    # Rects for interactions
    bgm_r = pygame.Rect(cx - 20, 250 - 20, sl_w + 40, sl_h + 40)
    sfx_r = pygame.Rect(cx - 20, 350 - 20, sl_w + 40, sl_h + 40)
    
    btn_w, btn_h = 160, 50
    lang_th_r = pygame.Rect(SW//2 - 170, 480, btn_w, btn_h)
    lang_en_r = pygame.Rect(SW//2 + 10, 480, btn_w, btn_h)
    
    back_w, back_h = 240, 60
    back_r = pygame.Rect(SW//2 - back_w//2, SH - 120, back_w, back_h)
    
    # Particles for background
    import random
    class Star:
        def __init__(self):
            self.x = random.randint(0, SW)
            self.y = random.randint(0, SH)
            self.s = random.uniform(0.5, 2.0)
            self.a = random.randint(50, 200)
    stars = [Star() for _ in range(50)]

    while True:
        mx, my = pygame.mouse.get_pos()
        clock.tick(FPS)
        
        # Interactions
        hov_bgm = bgm_r.collidepoint(mx, my) or dragging == 'bgm'
        hov_sfx = sfx_r.collidepoint(mx, my) or dragging == 'sfx'
        hov_th  = lang_th_r.collidepoint(mx, my)
        hov_en  = lang_en_r.collidepoint(mx, my)
        hov_back = back_r.collidepoint(mx, my)
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                sfx('click', 0.35)
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if hov_bgm: dragging = 'bgm'
                elif hov_sfx: dragging = 'sfx'
                elif hov_th and LANG[0] != 'th':
                    LANG[0] = 'th'; sfx('click', 0.35)
                elif hov_en and LANG[0] != 'en':
                    LANG[0] = 'en'; sfx('click', 0.35)
                elif hov_back:
                    sfx('click', 0.35)
                    return
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if dragging == 'sfx':
                    sfx('click', 0.35) # Test sound on release
                dragging = None
                
        # Handle dragging
        if dragging:
            val = max(0.0, min(1.0, (mx - cx) / sl_w))
            if dragging == 'bgm':
                bgm_val = val
                sound_mod.MASTER_BGM = val
                update_music_volume(0.42)
            else:
                sfx_val = val
                sound_mod.MASTER_SFX = val
        
        # Draw
        screen.fill(BG)
        for s in stars:
            s.x -= s.s
            if s.x < 0: s.x = SW; s.y = random.randint(0, SH)
            pygame.draw.circle(screen, (255,255,255,s.a), (int(s.x), int(s.y)), 1)
            
        # Title
        title_txt = "ตั้งค่าระบบ" if LANG[0] == 'th' else "SETTINGS"
        glow(screen, (50, 150, 255), SW//2, 100, 320, 50)
        dtxt(screen, title_txt, 'xl', WHITE, SW//2, 100, shad=True)
        
        # Sliders
        draw_slider(screen, cx, 250, sl_w, sl_h, bgm_val, "เพลงพื้นหลัง" if LANG[0]=='th' else "Music Volume", hov_bgm)
        draw_slider(screen, cx, 350, sl_w, sl_h, sfx_val, "เอฟเฟกต์เสียง" if LANG[0]=='th' else "SFX Volume", hov_sfx)
        
        # Language Buttons
        lang_title = "ภาษา" if LANG[0] == 'th' else "Language"
        dtxt_bg(screen, lang_title, 'm', WHITE, SW//2, 440)
        
        th_col = (50, 210, 85) if LANG[0] == 'th' else ((80,84,95) if not hov_th else (110,115,130))
        rrect(screen, th_col, lang_th_r, 8)
        if hov_th or LANG[0] == 'th':
            pygame.draw.rect(screen, WHITE, lang_th_r, 2, border_radius=8)
        dtxt(screen, "ภาษาไทย", 'm', WHITE, lang_th_r.centerx, lang_th_r.centery, shad=True)
        
        en_col = (50, 210, 85) if LANG[0] == 'en' else ((80,84,95) if not hov_en else (110,115,130))
        rrect(screen, en_col, lang_en_r, 8)
        if hov_en or LANG[0] == 'en':
            pygame.draw.rect(screen, WHITE, lang_en_r, 2, border_radius=8)
        dtxt(screen, "English", 'm', WHITE, lang_en_r.centerx, lang_en_r.centery, shad=True)
        
        # Back Button
        if hov_back:
            glow(screen, (255, 230, 100), back_r.centerx, back_r.centery, 130, 25)
        bc = (230, 190, 40) if hov_back else (150, 150, 30)
        rrect(screen, bc, back_r, 12)
        pygame.draw.rect(screen, WHITE if hov_back else (200,200,200), back_r, 2, 12)
        b_txt = "กลับสู่เมนูหลัก" if LANG[0] == 'th' else "Back to Menu"
        # Changed text color to WHITE and used dtxt with shad=True for readability
        dtxt(screen, b_txt, 'ml', WHITE, back_r.centerx, back_r.centery, shad=True)
        
        pygame.display.flip()
