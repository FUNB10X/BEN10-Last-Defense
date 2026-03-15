"""
game.py — The main game loop: wave management, entity updates, rendering.
Depends on all other modules — the top of the dependency chain.
"""
import sys
import math
import random
import pygame

from ben10_defense.config import (
    screen, clock, WP, SW, SH, FPS, UI_H, GW, GH, SHOP_X, SHOP_W,
    BG, GOLD, OMNI_G, WHITE, ADMIN_UNLOCKED, INFINITE_MONEY
)
from ben10_defense.data import (
    TOWERS, DIFFICULTIES, CURRENT_DIFF, T_KEYS_P1, T_KEYS_P2,
    get_wave_spawn_interval
)
from ben10_defense.font_lang import LANG, tr
from ben10_defense.sound import sfx, play_music, stop_music
from ben10_defense.draw_utils import dtxt, dtxt_bg, glow, on_path, rrect
from ben10_defense.maps.map_builder import MAP_SURF
from ben10_defense.entities.effects import Particle, FloatText, Shake, Announce
from ben10_defense.entities.enemy import Enemy
from ben10_defense.entities.tower import Tower
from ben10_defense.entities.bullet import Bullet
from ben10_defense.ui.hud import draw_hud
from ben10_defense.ui.shop import draw_shop, draw_tower_panel, SLOT_H, SPAD
from ben10_defense.screens.end_screen import boss_intro


def game():
    diff_key    = CURRENT_DIFF[0]; diff = DIFFICULTIES[diff_key]
    waves       = diff['waves']; total_waves = diff['total']; boss_waves = diff['boss_waves']
    towers      = []; enemies = []; bullets = []; parts = []; floats = []
    shake       = Shake(); ann = Announce()
    money       = diff['money']; base_hp = diff['bhp']; max_hp = base_hp
    won = False; dead = False; selected = None; shop_page = 0
    wave_num = 0; wave_idx = -1; in_wave = False
    spawn_q = []; spawn_t = 0.0; btw_t = 0.0
    prep_time = 10.0; in_prep_phase = True
    boss_ref  = [None]
    sel_tower  = None
    move_mode  = False
    panel_rects = {}
    
    # Admin State
    admin_open        = ADMIN_UNLOCKED[0]
    infinite_money    = INFINITE_MONEY[0]
    admin_wave_target = 1
    admin_collapsed   = False

    def begin_wave():
        nonlocal in_wave, wave_num, wave_idx, spawn_q, spawn_t, in_prep_phase
        wave_idx += 1; wave_num = wave_idx+1; in_wave = True; in_prep_phase = False
        spawn_q = list(waves[wave_idx]); spawn_t = 0.0
        if wave_num in boss_waves:
            play_music('boss_bgm', 0.5) 
            boss_intro() # Trigger cutscene immediately
        else:
            msg = f"รอบที่ {wave_num}" if LANG[0]=='th' else f"WAVE  {wave_num}"
            ann.show(msg, GOLD); sfx('wave')
            if wave_num == 1: play_music('bgm', 0.42)

    play_music('bgm', 0.42)
    prev_ms = pygame.time.get_ticks()
    p1_r = pygame.Rect(0,0,1,1); p2_r = pygame.Rect(0,0,1,1)
    # Between-wave SKIP button (top center)
    skip_r = pygame.Rect(GW//2 - 60, UI_H + 50, 120, 36)

    while True:
        now_ms = pygame.time.get_ticks(); dt = min((now_ms-prev_ms)/1000.0, 0.05); prev_ms = now_ms
        clock.tick(FPS); mx, my = pygame.mouse.get_pos()
        if infinite_money: money = 99999

        ben_count = sum(1 for t2 in towers if t2.kind=='ben10')
        dmg_mult  = 2 ** min(ben_count, 3)

        # ── Events ──────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    selected = None; sel_tower = None; move_mode = False
                    if (won or dead) and ev.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        stop_music(); return won
                if (won or dead) and ev.key == pygame.K_m:
                    stop_music(); return None

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 3: # Right click to cancel
                    selected = None; sel_tower = None; move_mode = False; continue
                
                if ev.button == 1:
                    if won or dead: sfx('click',0.35); stop_music(); return won
                # ── Admin Panel Events ───────────────────────
                if admin_open:
                    adm_x, adm_y = 10, UI_H + 10
                    # Toggle collapse
                    toggle_r = pygame.Rect(adm_x + 210, adm_y + 4, 24, 24)
                    if toggle_r.collidepoint(ev.pos):
                        admin_collapsed = not admin_collapsed; sfx('click', 0.4); continue

                    if not admin_collapsed:
                        # Money toggle
                        money_btn_r = pygame.Rect(adm_x + 10, adm_y + 36, 220, 34)
                        kill_btn_r  = pygame.Rect(adm_x + 10, adm_y + 80, 220, 34)
                        wnum_dec_r  = pygame.Rect(adm_x + 10, adm_y + 130, 40, 34)
                        wnum_inc_r  = pygame.Rect(adm_x + 90, adm_y + 130, 40, 34)
                        wgo_btn_r   = pygame.Rect(adm_x + 140, adm_y + 130, 90, 34)
                        if money_btn_r.collidepoint(ev.pos):
                            infinite_money = not infinite_money
                            INFINITE_MONEY[0] = infinite_money
                            sfx('click', 0.4); continue
                        if kill_btn_r.collidepoint(ev.pos):
                            enemies.clear(); spawn_q.clear(); sfx('base_hit'); continue
                        if wnum_dec_r.collidepoint(ev.pos):
                            admin_wave_target = max(1, admin_wave_target - 1); sfx('click', 0.3); continue
                        if wnum_inc_r.collidepoint(ev.pos):
                            admin_wave_target = min(total_waves, admin_wave_target + 1); sfx('click', 0.3); continue
                        if wgo_btn_r.collidepoint(ev.pos):
                            # Jump to wave: wipe current state and start target wave
                            enemies.clear(); spawn_q.clear(); bullets.clear()
                            wave_idx = admin_wave_target - 2
                            in_wave = False; in_prep_phase = False; prep_time = 0.0
                            begin_wave(); sfx('wave'); continue
                # Prep-phase skip button
                if in_prep_phase and skip_r.collidepoint(ev.pos):
                    # No skip if next is boss
                    if (wave_idx + 2) not in boss_waves:
                        sfx('click', 0.35)
                        in_prep_phase = False; prep_time = 0.0; begin_wave()
                        continue
                # Page toggle
                if p1_r.collidepoint(ev.pos): sfx('click',0.35); shop_page=0; selected=None; continue
                if p2_r.collidepoint(ev.pos): sfx('click',0.35); shop_page=1; selected=None; continue
                # Tower panel buttons
                if sel_tower and panel_rects:
                    up_r2  = panel_rects.get('up');  mv_r2 = panel_rects.get('mv')
                    sl_r2  = panel_rects.get('sl');  cl_r2 = panel_rects.get('cl')
                    cost2  = panel_rects.get('cost', 0)
                    if cl_r2 and cl_r2.collidepoint(ev.pos):
                        sfx('click',0.35); sel_tower=None; move_mode=False; continue
                    if up_r2 and up_r2.collidepoint(ev.pos):
                        if sel_tower.level<5 and cost2>0 and money>=cost2:
                            sel_tower.upgrade(); money-=cost2; sfx('place')
                            for _ in range(8): parts.append(Particle(sel_tower.x,sel_tower.y,sel_tower.col,1,3))
                        continue
                    if mv_r2 and mv_r2.collidepoint(ev.pos):
                        sfx('click',0.35); move_mode=True; continue
                    if sl_r2 and sl_r2.collidepoint(ev.pos):
                        money+=sel_tower.sell_value(); towers.remove(sel_tower)
                        sel_tower=None; move_mode=False; sfx('die'); continue
                # Move mode
                if move_mode and sel_tower:
                    if mx < GW and my > UI_H:
                        others = [t2 for t2 in towers if t2 is not sel_tower]
                        can_mv = (not on_path(mx,my) and
                                  all(math.hypot(t2.x-mx,t2.y-my)>=32 for t2 in others))
                        if can_mv:
                            sel_tower.x=float(mx); sel_tower.y=float(my)
                            move_mode=False; sfx('place')
                    continue
                # Shop click
                if mx >= SHOP_X and my >= UI_H:
                    keys2 = T_KEYS_P1 if shop_page==0 else T_KEYS_P2; ss = UI_H+56
                    for i, key in enumerate(keys2):
                        sr = pygame.Rect(SHOP_X+SPAD, ss+i*SLOT_H, SHOP_W-SPAD*2, SLOT_H-8)
                        if sr.collidepoint(mx,my):
                            d = TOWERS[key]; cnt = sum(1 for t2 in towers if t2.kind==key)
                            at_max = cnt >= d.get('max_count',99)
                            if money >= d['cost'] and not at_max:
                                sfx('click',0.35)
                                selected = None if selected==key else key
                                sel_tower = None
                # Map click
                elif mx < GW and my > UI_H:
                    if selected:
                        can_place = (not on_path(mx,my) and
                                     all(math.hypot(t2.x-mx,t2.y-my)>=32 for t2 in towers))
                        d = TOWERS[selected]; cnt = sum(1 for t2 in towers if t2.kind==selected)
                        if can_place and money>=d['cost'] and cnt<d.get('max_count',99):
                            towers.append(Tower(selected,mx,my)); money-=d['cost']
                            for _ in range(10): parts.append(Particle(mx,my,d['col'],1,3.5))
                            sfx('place'); selected=None
                    else:
                        clicked_t = next((t2 for t2 in towers if math.hypot(t2.x-mx,t2.y-my)<26), None)
                        if clicked_t:
                            sel_tower = clicked_t if sel_tower is not clicked_t else None
                            move_mode = False
                        else:
                            sel_tower = None; move_mode = False

        # ── Between-wave countdown ───────────────────────
        if not in_wave and not won and not dead:
            if not in_prep_phase:
                in_prep_phase = True
                prep_time = 10.0
            prep_time -= dt
            # Ensure Finale music stays on if we just finished a boss wave or are about to start one
            # The begin_wave call will handle the start. 
            if prep_time <= 0: begin_wave()


        # ── Spawn ────────────────────────────────────────
        if in_wave and spawn_q and not won and not dead:
            kind, _ = spawn_q[0]; spawn_t -= dt
            if spawn_t <= 0:
                e = Enemy(kind, diff_key, wave_num); enemies.append(e)
                if kind == 'boss': boss_ref[0]=e; shake.trigger(12,18)
                spawn_q.pop(0)
                if spawn_q:
                    next_k = spawn_q[0][0]
                    spawn_t = get_wave_spawn_interval(diff_key, wave_num) if next_k != 'boss' else 0.0
                else: spawn_t = 0.0

        # ── Track boss alive status ──────────────────────
        if boss_ref[0] and not boss_ref[0].alive:
            boss_ref[0] = None

        # ── Boss rage + ambient shake ────────────────────
        for e in enemies:
            if e.kind=='boss' and e.hp>0:
                rage = e.hp/e.mhp < 0.40
                if random.random()<0.15: shake.trigger(2,3)
                if rage and random.random()<0.12: shake.trigger(4,5)

        # ── Update enemies ───────────────────────────────
        alive_count = 0
        for e in enemies[:]:
            if not e.alive:
                money += e.rew; enemies.remove(e)
                if e.kind == 'boss':
                    boss_ref[0]=None; shake.trigger(22,28)
                    for _ in range(50): parts.append(Particle(e.x,e.y,(220+random.randint(-20,20),20,20),1.5,9))
                    for _ in range(30): parts.append(Particle(e.x,e.y,GOLD,1,7))
                else:
                    sfx('die')
                continue
            if e.reached:
                base_hp=max(0,base_hp-e.dmg); shake.trigger(8,10); enemies.remove(e)
                sfx('base_hit')
                if base_hp<=0:
                    dead=True; sfx('lose'); stop_music()
                    ann.show("EARTH HAS FALLEN",(220,20,20))
                continue
            if not won and not dead: e.update()
            alive_count += 1

        # ── Update towers ────────────────────────────────
        for t2 in towers:
            if not won and not dead:
                t2.update(enemies, bullets, parts, floats, dt, dmg_mult)
            money += t2.income_pending; t2.income_pending = 0

        # ── Update bullets ───────────────────────────────
        for b in bullets[:]:
            b.update()
            if not b.alive: bullets.remove(b)

        # ── Particles / floats ───────────────────────────
        for p in parts[:]:
            p.update()
            if p.life<=0: parts.remove(p)
        for ft in floats[:]:
            ft.update()
            if ft.life<=0: floats.remove(ft)

        # ── Wave complete ────────────────────────────────
        if in_wave and not spawn_q and alive_count==0 and not dead and not won:
            in_wave = False
            if wave_idx == total_waves-1:
                won=True; sfx('win'); stop_music()
                ann.show(tr("VICTORY  —  EARTH SAVED!"), (0,230,60))
            else:
                money+=50
                msg = (f"ผ่านรอบที่ {wave_num}! +$50" if LANG[0]=='th'
                       else f"Wave {wave_num} clear! +$50")
                ann.show(msg, (20,210,60)); sfx('clear')

        # ── Infinite money enforcement ─────────────────────
        if infinite_money:
            money = 99999

        eleft = alive_count + len(spawn_q)
        boss_on_field = next((e for e in enemies if e.kind=='boss'), None)
        if in_wave:
            if wave_num in boss_waves: play_music('boss_bgm', 0.5)
            else:                      play_music('bgm',      0.42)

        # ── DRAW ─────────────────────────────────────────
        ox, oy = shake.get()
        screen.fill(BG)
        screen.blit(MAP_SURF, (int(ox), UI_H+int(oy)))

        # Y-sort: tiles + towers drawn together by Y
        hover_t    = next((t2 for t2 in towers if math.hypot(t2.x-mx,t2.y-my)<30), None)
        draw_order = []
        for e   in enemies: draw_order.append(('e', e,  e.y))
        for t2  in towers:  draw_order.append(('t', t2, t2.y))
        draw_order.sort(key=lambda x: x[2])
        for knd, obj, _ in draw_order:
            if knd == 'e':
                obj.draw(screen)
            else:
                obj.draw(screen, hov=(obj is hover_t))
                if obj is sel_tower and not move_mode:
                    pygame.draw.circle(screen, (255,215,50), (int(obj.x),int(obj.y)), 30, 2)

        # Tower info panel
        if sel_tower and sel_tower in towers:
            up_r2, mv_r2, sl_r2, cl_r2, uc2 = draw_tower_panel(screen, sel_tower, money, mx, my, move_mode)
            panel_rects = {'up':up_r2,'mv':mv_r2,'sl':sl_r2,'cl':cl_r2,'cost':uc2}
        else:
            panel_rects = {}
            if sel_tower and sel_tower not in towers: sel_tower = None

        # Move mode cursor
        if move_mode and sel_tower:
            others = [t2 for t2 in towers if t2 is not sel_tower]
            can_mv2 = (mx<GW and my>UI_H and not on_path(mx,my)
                       and all(math.hypot(t2.x-mx,t2.y-my)>=32 for t2 in others))
            gs2 = pygame.Surface((50,50), pygame.SRCALPHA)
            col3=sel_tower.col; al2=140 if can_mv2 else 45
            pygame.draw.circle(gs2,(col3[0],col3[1],col3[2],al2),(25,25),22)
            pygame.draw.circle(gs2,(255,255,255,al2//2),(25,25),22,2)
            screen.blit(gs2,(mx-25,my-25))
            mv_hint = 'คลิกเพื่อย้ายที่นี่' if LANG[0]=='th' else 'Click to move here'
            if not can_mv2: mv_hint = 'วางไม่ได้' if LANG[0]=='th' else 'Cannot place here'
            dtxt_bg(screen, mv_hint, 'xs', (200,220,255), mx, my-30)

        # Placement ghost
        if selected and mx<GW and my>UI_H:
            can_p=(not on_path(mx,my) and all(math.hypot(t2.x-mx,t2.y-my)>=32 for t2 in towers))
            col2=TOWERS[selected]['col']; al=155 if can_p else 50
            gs=pygame.Surface((50,50),pygame.SRCALPHA)
            pygame.draw.circle(gs,(col2[0],col2[1],col2[2],al),(25,25),22)
            pygame.draw.circle(gs,(255,255,255,al//2),(25,25),22,2)
            screen.blit(gs,(mx-25,my-25))
            if TOWERS[selected]['rng']>0:
                r2=TOWERS[selected]['rng']
                rs=pygame.Surface((r2*2+4,r2*2+4),pygame.SRCALPHA)
                pygame.draw.circle(rs,(255,255,100,12 if can_p else 5),(r2+2,r2+2),r2)
                pygame.draw.circle(rs,(255,255,100,52 if can_p else 12),(r2+2,r2+2),r2,1)
                screen.blit(rs,(mx-r2-2,my-r2-2))
            if not can_p: dtxt_bg(screen,"X",'l',(220,30,30),mx,my)

        for b in bullets: b.draw(screen)
        for p in parts:   p.draw(screen)
        for ft in floats: ft.draw(screen)

        p1_r, p2_r = draw_shop(screen,money,selected,mx,my,shop_page,towers)
        draw_hud(screen,base_hp,max_hp,money,wave_num,total_waves,eleft,boss_on_field,ben_count)
        ann.update(); ann.draw(screen)

        # Skip wave button (during active wave) - REMOVED PER USER REQUEST

        # Admin Panel (Top-Left)
        if admin_open:
            adm_x, adm_y = 10, UI_H + 10
            ah = 30 if admin_collapsed else 180
            adm_surf = pygame.Surface((240, ah), pygame.SRCALPHA)
            adm_surf.fill((10, 10, 25, 210))
            screen.blit(adm_surf, (adm_x, adm_y))
            pygame.draw.rect(screen, (255,190,0), (adm_x, adm_y, 240, ah), 2, 8)
            
            # Header
            dtxt(screen, '🔧 ADMIN PANEL', 's', (255,200,0), adm_x+105, adm_y+14, shad=True)
            # Toggle button
            toggle_r = pygame.Rect(adm_x+210, adm_y+4, 24, 24)
            rrect(screen, (60,60,80), toggle_r, 4)
            tchar = '+' if admin_collapsed else '−'
            dtxt(screen, tchar, 's', WHITE, toggle_r.centerx, toggle_r.centery)

            if not admin_collapsed:
                # Money toggle
                money_btn_r = pygame.Rect(adm_x+10, adm_y+36, 220, 34)
                mc = (40,180,40) if infinite_money else (60,60,60)
                rrect(screen, mc, money_btn_r, 6)
                ml = '💰 ∞ Money: ON' if infinite_money else '💰 ∞ Money: OFF'
                dtxt(screen, ml, 's', WHITE, money_btn_r.centerx, money_btn_r.centery)
                # Kill All
                kill_btn_r = pygame.Rect(adm_x+10, adm_y+80, 220, 34)
                rrect(screen, (160,20,100), kill_btn_r, 6)
                dtxt(screen, '☢ Kill All Enemies', 's', WHITE, kill_btn_r.centerx, kill_btn_r.centery)
                # Wave jump
                wnum_dec_r = pygame.Rect(adm_x+10, adm_y+130, 40, 34)
                wnum_inc_r = pygame.Rect(adm_x+90, adm_y+130, 40, 34)
                wgo_btn_r  = pygame.Rect(adm_x+140, adm_y+130, 90, 34)
                rrect(screen, (60,60,120), wnum_dec_r, 6)
                dtxt(screen, '−', 'm', WHITE, wnum_dec_r.centerx, wnum_dec_r.centery)
                rrect(screen, (60,60,120), wnum_inc_r, 6)
                dtxt(screen, '+', 'm', WHITE, wnum_inc_r.centerx, wnum_inc_r.centery)
                rrect(screen, (40,80,180), wgo_btn_r, 6)
                dtxt(screen, f'Go {admin_wave_target}', 's', WHITE, wgo_btn_r.centerx, wgo_btn_r.centery)
                dtxt(screen, f'Wave: {admin_wave_target}', 'xs', (180,200,255), adm_x+60, adm_y+147)
                dtxt(screen, 'V.3.4 (FINAL)', 'xs', (100,100,150), adm_x+190, adm_y+14)

        # Between-wave countdown text and skip button
        if in_prep_phase and not won and not dead:
            # Check if next wave is boss
            next_is_boss = (wave_idx + 2) in boss_waves
            txt = (f"รอบถัดไปใน {math.ceil(prep_time)} วิ" if LANG[0]=='th'
                   else f"Next wave in {math.ceil(prep_time)}s")
            # Larger text ('l'), no background pill
            from ben10_defense.font_lang import Fk
            f_surf = Fk()['l'].render(txt, True, WHITE)
            f_rect = f_surf.get_rect(center=(GW//2, skip_r.y - 25))
            screen.blit(f_surf, f_rect)
            if not next_is_boss:
                hov_skip = skip_r.collidepoint(mx, my)
                sc = (60,180,60) if hov_skip else (40,140,40)
                rrect(screen, sc, skip_r, 8)
                stxt = "เริ่มเลย (SKIP)" if LANG[0]=='th' else "SKIP"
                dtxt(screen, stxt, 'm', WHITE, skip_r.centerx, skip_r.centery, shad=True)

        # Win / loss overlay
        if won or dead:
            ov = pygame.Surface((GW,GH),pygame.SRCALPHA); ov.fill((0,0,0,155))
            screen.blit(ov,(0,UI_H))
            if won:
                glow(screen,(0,200,50),GW//2,SH//2,230,30)
                dtxt_bg(screen,tr("EARTH SAVED!"),'xxl',(0,230,55),GW//2,SH//2-55)
                dtxt_bg(screen,tr("Vilgax is defeated."),'ml',(200,225,200),GW//2,SH//2+32)
            else:
                glow(screen,(180,0,0),GW//2,SH//2,230,30)
                dtxt_bg(screen,tr("EARTH HAS FALLEN"),'xxl',(220,20,20),GW//2,SH//2-55)
                dtxt_bg(screen,tr("Vilgax conquers the planet."),'ml',(200,180,180),GW//2,SH//2+32)
            dtxt_bg(screen,tr("[ Click / ENTER: continue  |  M: menu ]"),'s',(180,190,215),GW//2,SH//2+82)

        # Cursor dot when placing
        if selected:
            pygame.draw.circle(screen, TOWERS[selected]['col'], (mx,my), 6)
            pygame.draw.circle(screen, WHITE, (mx,my), 6, 1)

        pygame.display.flip()
