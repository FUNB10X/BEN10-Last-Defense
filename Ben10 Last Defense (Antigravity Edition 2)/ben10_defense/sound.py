"""
sound.py — Procedural SFX + external BGM playback.
Depends on: config (for pygame being init'd), optionally numpy.
"""
import os as _os
import sys
import pygame

# ฟังก์ชันช่วยหา Path สำหรับ PyInstaller
def resource_path(relative_path):
    try:
        # PyInstaller สร้างโฟลเดอร์ชั่วคราวและเก็บ path ไว้ใน _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = _os.path.abspath(".")
    return _os.path.join(base_path, relative_path)

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

SR = 44100
_cur_mus: list = [None]
_sfx_cache = {}

# ── Note-to-frequency helpers ──────────────────────────────
def _nf(note):
    if note == 'R': return 0.0
    bases = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    nm = note[0]; mods = note[1:-1]; oct_ = int(note[-1])
    semi = bases[nm] + (1 if '#' in mods else -1 if 'b' in mods else 0)
    return 440.0 * (2.0 ** ((semi + (oct_ - 4)*12 - 9) / 12.0))

def _ws(freq, dur, shape='sq', vol=0.28):
    n = int(SR * dur)
    if n <= 0: return np.zeros(0, dtype=np.float32)
    if freq <= 0: return np.zeros(n, dtype=np.float32)
    t = np.linspace(0, dur, n, endpoint=False)
    if shape == 'sq':    w = np.sign(np.sin(2*np.pi*freq*t))
    elif shape == 'tri': ph = (t*freq)%1.0; w = 2*np.abs(2*ph-1)-1
    elif shape == 'saw': w = 2*((t*freq)%1.0)-1
    else: w = np.sin(2*np.pi*freq*t)
    att = min(n, max(1, int(0.003*SR))); rel = min(n, max(1, int(0.012*SR)))
    w[:att] *= np.linspace(0, 1, att); w[-rel:] *= np.linspace(1, 0, rel)
    return (w * vol).astype(np.float32)

def _mk(arr):
    d = np.clip(arr, -1.0, 1.0); d16 = (d * 32767).astype(np.int16)
    st = np.column_stack([d16, d16]); return pygame.sndarray.make_sound(st)

# ── Build procedural sound library ────────────────────────
def build_sounds():
    snd = {}
    if not HAS_NP:
        return snd
    try:
        snd['wave']      = _mk(np.concatenate([_ws(_nf('C5'),.07,'sq',.45),_ws(_nf('E5'),.07,'sq',.45),_ws(_nf('G5'),.07,'sq',.45),_ws(_nf('A5'),.20,'sq',.40)]))
        snd['boss_warn'] = _mk(np.concatenate([_ws(_nf('A4'),.10,'sq',.55),_ws(0,.05),_ws(_nf('A4'),.10,'sq',.55),_ws(0,.05),_ws(_nf('A4'),.10,'sq',.55),_ws(_nf('Eb4'),.45,'sq',.50)]))
        snd['die']       = _mk(np.concatenate([_ws(523,.04,'sq',.30),_ws(392,.04,'sq',.26),_ws(261,.07,'sq',.20)]))
        snd['clear']     = _mk(np.concatenate([_ws(_nf('E5'),.07,'sq',.38),_ws(_nf('G5'),.07,'sq',.38),_ws(_nf('A5'),.07,'sq',.38),_ws(0,.04),_ws(_nf('B5'),.22,'sq',.38)]))
        snd['place']     = _mk(np.concatenate([_ws(_nf('G5'),.04,'sq',.32),_ws(_nf('B5'),.08,'sq',.30)]))
        snd['base_hit']  = _mk(np.concatenate([_ws(110,.05,'sq',.60),_ws(82,.07,'sq',.50),_ws(65,.10,'sq',.38)]))
        snd['cash']      = _mk(np.concatenate([_ws(_nf('G5'),.04,'sq',.25),_ws(_nf('A5'),.06,'sq',.22)]))
        snd['boss_hit']  = _mk(np.concatenate([_ws(200,.04,'sq',.50),_ws(150,.03,'sq',.45),_ws(100,.06,'sq',.40)]))
        snd['click']     = _mk(np.concatenate([_ws(_nf('C6'),.02,'sq',.25),_ws(_nf('G5'),.04,'sq',.20)]))
        snd['win']       = _mk(np.concatenate([_ws(_nf('C5'),.10,'sq',.40),_ws(_nf('E5'),.10,'sq',.40),_ws(_nf('G5'),.10,'sq',.40),_ws(_nf('C6'),.30,'sq',.45)]))
        snd['lose']      = _mk(np.concatenate([_ws(_nf('C4'),.15,'sq',.45),_ws(_nf('G3'),.20,'sq',.40),_ws(_nf('Eb3'),.40,'sq',.35)]))
    except Exception as e:
        print("Sound error:", e)
    return snd

SOUNDS = build_sounds()

# ── Volume Control State ────────────────────────────────
MASTER_BGM = 1.0
MASTER_SFX = 1.0

# ── Music playback ─────────────────────────────────────────
def _get_bgm_vol(base_vol):
    return max(0.0, min(1.0, base_vol * MASTER_BGM))

def play_music(name, vol=0.42):
    """Play BGM by name; skips if already playing the same track."""
    v = _get_bgm_vol(vol)
    if _cur_mus[0] == name:
        pygame.mixer.music.set_volume(v)
        return
    stop_music()
    
    # กำหนดแมพชื่อเพลงกับไฟล์จริง (ใช้ resource_path ครอบทุกชื่อไฟล์)
    if name == 'menu_bgm':
        # เช็คทั้ง wav และ mp3 ผ่าน resource_path
        f_wav = resource_path('b10mainmenu.wav')
        f_mp3 = resource_path('b10mainmenu.mp3')
        fname = f_wav if _os.path.exists(f_wav) else f_mp3
        if _os.path.exists(fname):
            try:
                pygame.mixer.music.load(fname)
                pygame.mixer.music.set_volume(v)
                pygame.mixer.music.play(-1)
                _cur_mus[0] = name; return
            except Exception as e: print(f"Music error ({fname}):", e)

    if name == 'boss_bgm':
        f_wav = resource_path('Finale.wav')
        f_mp3 = resource_path('Finale.mp3')
        fname = f_wav if _os.path.exists(f_wav) else f_mp3
        if _os.path.exists(fname):
            try:
                pygame.mixer.music.load(fname)
                pygame.mixer.music.set_volume(v)
                pygame.mixer.music.play(-1)
                _cur_mus[0] = name; return
            except Exception as e: print(f"Music error ({fname}):", e)

    if name == 'bgm':
        f_wav = resource_path('b10mainmenu_slow.wav')
        f_mp3 = resource_path('b10mainmenu_slow.mp3')
        fname = f_wav if _os.path.exists(f_wav) else f_mp3
        if _os.path.exists(fname):
            try:
                pygame.mixer.music.load(fname)
                pygame.mixer.music.set_volume(v)
                pygame.mixer.music.play(-1)
                _cur_mus[0] = name; return
            except Exception as e: print(f"Music error ({fname}):", e)

    # Fallback: ลองหา <name>.wav ตรงๆ
    fname = resource_path(f"{name}.wav" if not name.endswith('.wav') else name)
    if _os.path.exists(fname):
        try:
            pygame.mixer.music.load(fname)
            pygame.mixer.music.set_volume(v)
            pygame.mixer.music.play(-1)
            _cur_mus[0] = name
        except Exception as e: print(f"Music error ({fname}):", e)

def stop_music():
    pygame.mixer.music.stop()
    _cur_mus[0] = None

def update_music_volume(vol=0.42):
    """Update volume of currently playing music if master volume changed"""
    if _cur_mus[0] is not None:
        pygame.mixer.music.set_volume(_get_bgm_vol(vol))

def sfx(name, vol=0.18):
    """Play a sound effect by name (cached after first lookup)."""
    if name not in _sfx_cache:
        fname = resource_path(f"sfx_{name}.wav")
        if _os.path.exists(fname):
            try: _sfx_cache[name] = pygame.mixer.Sound(fname)
            except Exception: pass
        elif name in SOUNDS:
            _sfx_cache[name] = SOUNDS[name]
    snd = _sfx_cache.get(name)
    if snd is not None:
        snd.set_volume(max(0.0, min(1.0, vol * MASTER_SFX)))
        snd.play()
