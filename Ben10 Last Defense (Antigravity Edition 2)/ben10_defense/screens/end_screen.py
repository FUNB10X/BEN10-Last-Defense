"""
end_screen.py — end_screen(), boss_intro() — win/loss screen and boss cutscene.
Depends on: config, draw_utils, font_lang, sound, entities/effects.
"""
import sys
import math
import random
import pygame

from ben10_defense.config import screen, clock, SW, SH, FPS, GOLD
from ben10_defense.draw_utils import dtxt, dtxt_bg, glow, lerp_col
from ben10_defense.font_lang import F, tr
from ben10_defense.sound import sfx, play_music, stop_music
from ben10_defense.entities.effects import Particle


def boss_intro():
    """Short dramatic cutscene when a boss wave starts."""
    sfx('boss_warn')
    play_music('boss_bgm', 0.45)
    
    # Intense glitchy intro
    for frame in range(180):
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN): return
        
        # Shake effect during cutscene
        off_x = random.randint(-4, 4) if frame < 150 else random.randint(-8, 8)
        off_y = random.randint(-4, 4) if frame < 150 else random.randint(-8, 8)
        
        # Red pulsing background with periodic "glitch" flashes
        flash = int(abs(math.sin(frame*0.22))*180)
        if random.random() < 0.05: # Glitch flash
            screen.fill((200, 200, 200))
        else:
            screen.fill((flash//3, 0, 0))
            
        # Draw central glowing orb
        glow(screen, (255,50,0), SW//2 + off_x, SH//2 + off_y, 220, int(60+40*abs(math.sin(frame*.15))))
        glow(screen, (220,0,0), SW//2 + off_x, SH//2 + off_y, 320, 30)
        
        # Text with intense scale and flickering
        sc2 = 1.1 + 0.12 * math.sin(frame * 0.45)
        if random.random() < 0.1: sc2 *= 1.1 # Periodic zoom glitch
        
        # "⚠ VILGAX ⚠" text
        s = F['xxl'].render(tr('⚠ VILGAX ⚠'), True, (255, 30, 30))
        s2 = pygame.transform.scale(s, (int(s.get_width()*sc2), int(s.get_height()*sc2)))
        screen.blit(s2, s2.get_rect(center=(SW//2 + off_x, SH//2 - 60 + off_y)))
        
        # Subtext
        sub_col = (255, 255, 255) if (frame // 4) % 2 == 0 else (255, 50, 50)
        s3 = F['l'].render(tr('PLANETARY  THREAT  DETECTED'), True, sub_col)
        screen.blit(s3, s3.get_rect(center=(SW//2 + off_x, SH//2 + 40 + off_y)))
        
        # Countdown
        cd = max(0, int((180-frame)/45))
        if cd > 0:
            dtxt_bg(screen, f"INITIATING COMBAT: {cd}", 'm', (255,180,50), SW//2, SH//2+120)
            
        pygame.display.flip()


def end_screen(won):
    """Win or lose end screen with animated overlay, then return to caller."""
    t = 0; parts = []
    if won:
        title = tr("VILGAX DEFEATED!"); tc = (0,230,60)
        subs  = [tr("Vilgax's army retreats into deep space."), "",
                 tr("Earth breathes again.  For now."), "",
                 tr("A mysterious signal pulses from the cosmos..."), "",
                 tr("Ben looks up.  This isn't over.")]
        sfx('win', 0.45); play_music('victory_bgm', 0.45)
        for _ in range(25):
            parts.append(Particle(random.randint(0,SW), random.randint(SH//4, 3*SH//4),
                                  (0,200,50), smin=.4, smax=2.5, grav=0))
    else:
        title = tr("EARTH HAS FALLEN"); tc = (220,20,20)
        subs  = [tr("Vilgax conquers the planet."), "",
                 tr("The Omnitrix goes dark."), "",
                 tr("All hope... is lost.")]
        sfx('lose', 0.45); play_music('gameover_bgm', 0.42)

    while True:
        clock.tick(FPS); t += 1
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                stop_music(); return
        base = (3,18,6) if won else (18,3,3)
        for y in range(SH):
            pygame.draw.line(screen, lerp_col(base,(8,8,18),y/SH), (0,y), (SW,y))
        if t%5 == 0 and won:
            parts.append(Particle(random.randint(100,SW-100), -10, tc, smin=.4, smax=2.5, grav=.04))
        for p in parts[:]:
            p.update(); p.draw(screen)
            if p.life <= 0: parts.remove(p)
        glow(screen, tc, SW//2, SH//2-80, 220, 25)
        dtxt(screen, title, 'xxl', tc, SW//2, SH//2-80, shad=True)
        cy = SH//2-14
        for line in subs:
            if line:
                a = min(1.0, max(0.0, (t-30)/80.0))
                dtxt(screen, line, 'm', tuple(int(c*a) for c in (165,170,195)), SW//2, cy)
            cy += 30
        dtxt_bg(screen, tr("[ Click or press any key  →  menu ]"), 's', (180,190,215), SW//2, SH-40)
        pygame.display.flip()
