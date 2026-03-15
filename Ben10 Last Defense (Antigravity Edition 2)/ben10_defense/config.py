"""
config.py — Screen layout, palette, waypoints, and display setup.
No imports from other ben10_defense modules.
"""
import pygame

# ── Screen Layout ──────────────────────────────────────────
SW, SH  = 1100, 720
UI_H    = 64
GW      = 860
GH      = SH - UI_H
SHOP_X  = GW
SHOP_W  = SW - GW
FPS     = 60
PATH_W  = 50

# ── Path waypoints (world-space) ───────────────────────────
WP = [
    (-70,   UI_H + 195),
    (155,   UI_H + 195),
    (155,   UI_H + 458),
    (425,   UI_H + 458),
    (425,   UI_H + 120),
    (665,   UI_H + 120),
    (665,   UI_H + 415),
    (GW+70, UI_H + 415),
]

# ── Palette ────────────────────────────────────────────────
BG       = (10,  14,  26)
GRASS_A  = (26,  82,  26)
GRASS_B  = (32,  96,  32)
GRASS_C  = (20,  68,  20)
PATH_COL = (148, 110, 65)
PATH_EDG = (95,  60,  32)
PATH_DRK = (72,  44,  18)
HUD_BG   = (8,   10,  22)
HUD_LINE = (30,  55, 115)
SHOP_BG  = (11,  14,  33)
SHOP_LN  = (28,  48, 108)
WHITE    = (255, 255, 255)
BLACK    = (0,     0,   0)
GOLD     = (255, 210,  50)
OMNI_G   = (30,  185,  50)
HP_G     = (20,  210,  60)
HP_O     = (255, 165,   0)
HP_R     = (210,  15,  15)

# ── Display (initialised here, shared across all modules) ──
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init(44100, -16, 2, 512)

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("BEN 10 Last Defense")
clock  = pygame.time.Clock()
# ── Global State (Persists across screens) ─────────────
ADMIN_UNLOCKED = [False]
INFINITE_MONEY = [False]
