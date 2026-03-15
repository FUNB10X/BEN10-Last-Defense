"""
data.py — Static game data: towers, enemies, waves, difficulties.
Imports only from config (for GOLD, OMNI_G colours used in tower defs).
"""
from ben10_defense.config import GOLD, OMNI_G

# ── Tower definitions ──────────────────────────────────────
TOWERS = {
    'heatblast':   dict(name="Heatblast",   cost= 50, rng=118, dmg= 9,  rate= 58, bspd= 9.5,
                        col=(255,105,15),  bc=(255,200,40),  btype='fire',    income=False, desc="Fast DPS · Cheap"),
    'fourarms':    dict(name="Four Arms",   cost=100, rng= 78, dmg=30,  rate=112, bspd= 7.0,
                        col=(210, 30, 30), bc=(255, 70,70),  btype='fist',    income=False, desc="Heavy damage · Short"),
    'xlr8':        dict(name="XLR8",        cost=150, rng=112, dmg= 6,  rate= 20, bspd=14.0,
                        col=( 35,170,255), bc=(140,225,255), btype='bolt',    income=False, desc="Insane fire rate"),
    'diamondhead': dict(name="Diamondhead", cost=200, rng=202, dmg=42,  rate=175, bspd=11.0,
                        col=(110,220,255), bc=(210,248,255), btype='crystal', income=False, desc="Sniper · Long range"),
    'grandpa':     dict(name="Grandpa Max", cost=150, rng=  0, dmg= 0,  rate=  1, bspd= 0,
                        col=(180,130,55),  bc=GOLD,          btype='none',    income=True,
                        income_amt=50, income_interval=10.0, max_count=99,   desc="Earns $50 / 10s"),
    'ben10':       dict(name="Ben 10",      cost=300, rng=  0, dmg= 0,  rate=  1, bspd= 0,
                        col=(0, 185, 50),  bc=(0,230,60),    btype='none',    income=True,
                        income_amt=10, income_interval=5.0,  max_count=3,    desc="×2 ATK · $10 / 5s"),
    'idin':        dict(name="Idin",        cost=999, rng=  0, dmg= 0,  rate=  1, bspd= 0,
                        col=(40, 60, 120), bc=GOLD,          btype='none',    income=True,
                        income_amt=200, income_interval=8.0, max_count=99,   desc="Supreme Support · Rich"),
}
T_KEYS_P1 = ['heatblast', 'fourarms', 'xlr8', 'diamondhead']
T_KEYS_P2 = ['grandpa', 'ben10', 'idin']

# ── Enemy base stats ───────────────────────────────────────
BASE_ENEMIES = {
    'grunt': dict(hp= 32,  spd=2.15, dmg= 5, rew= 10, col=(195,55,55)),
    'drone': dict(hp= 55,  spd=1.60, dmg= 8, rew= 15, col=(55,150,225)),
    'tank':  dict(hp=125,  spd=0.85, dmg=20, rew= 30, col=(88,90,95)),
    'elite': dict(hp=185,  spd=1.45, dmg=25, rew= 40, col=(165,40,210)),
    'boss':  dict(hp=900,  spd=0.55, dmg=60, rew=200, col=(220,20,20)),
}

# ── Wave tables ────────────────────────────────────────────
WAVES_EASY = [
    [('grunt', 2.2)]*10,
    [('grunt', 2.0)]*12,
    [('grunt', 2.1)]*8 + [('drone', 2.4)]*5,
    [('drone', 2.2)]*10,
    [('drone', 2.2)]*6 + [('tank', 2.5)]*3,
    [('tank',  2.4)]*6,
    [('tank',  2.3)]*4 + [('elite', 2.4)]*5,
    [('elite', 2.2)]*8,
    [('elite', 2.0)]*10,
    # Easy Wave 10 — Boss wave with 5 elite minions leading in
    [('elite', 0)]*5 + [('boss', 0)],
]
WAVES_NORMAL = [
    [('grunt', 2.2)]*12,
    [('grunt', 2.0)]*18,
    [('grunt', 2.1)]*10 + [('drone', 2.3)]*6,
    [('drone', 2.1)]*14,
    [('drone', 2.0)]*9  + [('tank', 2.5)]*4,
    [('tank',  2.3)]*8,
    [('tank',  2.2)]*6   + [('elite', 2.3)]*6,
    [('elite', 2.1)]*10,
    [('elite', 2.0)]*14,
    [('grunt', 2.0)]*10 + [('drone', 2.1)]*8 + [('tank', 2.3)]*4,
    [('drone', 2.1)]*14 + [('elite', 2.4)]*6,
    [('tank',  2.3)]*9   + [('elite', 2.2)]*8,
    [('elite', 2.1)]*18,
    [('elite', 2.0)]*20,
    [('tank',  2.3)]*8   + [('elite', 2.1)]*10,
    [('elite', 2.0)]*18 + [('tank', 2.3)]*6,
    [('grunt', 2.0)]*12 + [('drone', 2.1)]*10 + [('elite', 2.2)]*8,
    [('elite', 2.0)]*22,
    [('elite', 1.8)]*28,
    # Normal Wave 20 — Boss wave with 8 elite + 1 tank leading in
    [('elite', 0)]*8 + [('tank', 0)]*1 + [('boss', 0)],
]
WAVES_HARD = [
    [('grunt', 2.0)]*15,
    [('grunt', 1.8)]*22,
    [('grunt', 1.9)]*12 + [('drone', 2.2)]*9,
    [('drone', 2.0)]*18,
    [('drone', 1.9)]*12 + [('tank', 2.4)]*6,
    [('tank',  2.3)]*10,
    [('tank',  2.2)]*9   + [('elite', 2.3)]*8,
    [('elite', 2.1)]*15,
    [('elite', 2.0)]*20,
    [('grunt', 2.0)]*12 + [('drone', 2.1)]*10 + [('tank', 2.3)]*6,
    [('drone', 2.0)]*15 + [('elite', 2.2)]*9,
    [('tank',  2.2)]*11  + [('elite', 2.1)]*9,
    [('elite', 2.0)]*22,
    [('elite', 1.9)]*28,
    # Hard Wave 15 — Boss 1 wave with 5 elite leading in
    [('elite', 0)]*5 + [('boss', 0)],           # BOSS 1 – wave 15
    [('grunt', 1.8)]*15 + [('drone', 2.0)]*12,
    [('drone', 1.8)]*18 + [('tank', 2.3)]*8,
    [('tank',  2.1)]*12  + [('elite', 2.0)]*10,
    [('elite', 1.8)]*25,
    [('elite', 1.7)]*30,
    [('grunt', 1.8)]*12 + [('drone', 1.9)]*12 + [('elite', 2.1)]*9,
    [('elite', 1.8)]*30 + [('tank', 2.2)]*8,
    [('elite', 1.8)]*32,
    [('tank',  2.0)]*15  + [('elite', 1.9)]*18,
    [('elite', 1.8)]*35,
    [('drone', 1.8)]*15 + [('elite', 1.9)]*15 + [('tank', 2.1)]*8,
    [('elite', 1.8)]*35 + [('tank', 2.0)]*8,
    [('elite', 1.7)]*35 + [('elite', 1.7)]*8,
    [('elite', 1.7)]*32 + [('tank', 1.9)]*12,
    # Hard Wave 30 — Boss 2 wave with 18 elite + 2 tank leading in
    [('elite', 0)]*18 + [('tank', 0)]*2 + [('boss', 0)],           # BOSS 2 – wave 30
]

# ── Difficulty settings ────────────────────────────────────
DIFFICULTIES = {
    'easy':   dict(label='EASY',   sub='10 Waves',
                   waves=WAVES_EASY,   total=10,
                   hp=0.75, spd=0.82, rew=1.30, money=300, bhp=120,
                   col=(40,200,75),  boss_waves={10}),
    'normal': dict(label='NORMAL', sub='20 Waves',
                   waves=WAVES_NORMAL, total=20,
                   hp=1.20, spd=1.00, rew=1.00, money=300, bhp=100,
                   col=(80,140,255), boss_waves={20}),
    'hard':   dict(label='HARD',   sub='30 Waves',
                   waves=WAVES_HARD,   total=30,
                   hp=1.50, spd=1.22, rew=0.70, money=300, bhp=80,
                   col=(225,50,50),  boss_waves={15,30}),
}

def get_wave_spd_mult(diff_key, wave_num, is_boss=False):
    """Specific speed scaling requested by user:
    Easy: 0.75
    Normal: 1-5: 0.75, 6-12: 1.05, 13-16: 1.2, 17-20: 1.3
    Hard: 1-3: 0.75, 4-10: 1.05, 11-15: 1.2, 16-20: 1.3, 21-25: 1.4, 26-30: 1.5 (except boss)
    """
    if diff_key == 'easy':
        return 0.75
    
    if diff_key == 'normal': # Medium
        if wave_num <= 5:   return 0.75
        if wave_num <= 12:  return 1.05
        if wave_num <= 16:  return 1.2
        return 1.3
    
    if diff_key == 'hard':
        if is_boss: return 1.0 # Bosses stay at predicted pace
        if wave_num <= 3:   return 0.75
        if wave_num <= 10:  return 1.05
        if wave_num <= 15:  return 1.2
        if wave_num <= 20:  return 1.3
        if wave_num <= 25:  return 1.4
        return 1.5
    
    return 1.0


def get_wave_spawn_interval(diff_key, wave_num):
    """Dynamically set spawn interval based on speed:
    Slower wave (0.75x) -> 1.3s interval
    Faster wave (1.5x)  -> 0.6s interval
    """
    spd = get_wave_spd_mult(diff_key, wave_num)
    ratio = (spd - 0.75) / 0.75  # 0.0 to 1.0
    interval = 1.3 - ratio * 0.7
    return max(0.6, min(1.3, interval))

# Mutable 1-element list so screens can update the chosen difficulty globally
CURRENT_DIFF = ['normal']
