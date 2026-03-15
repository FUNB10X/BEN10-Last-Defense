"""
font_lang.py — Font loading, language selection, translation dict, tr(), Fk().
Depends only on config (for pygame being already initialised).
"""
import os as _os
import pygame

# ── Language toggle (mutable 1-elem list) ──────────────────
LANG = ['th']

# ── Font discovery ─────────────────────────────────────────
def _find_font(name):
    for base in [_os.path.dirname(_os.path.abspath(__file__)),
                 _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                 _os.getcwd(), '.']:
        p = _os.path.join(base, name)
        if _os.path.isfile(p):
            return p
    return None

_ANAKO_BOLD = _find_font('Anakotmai-Bold.ttf') or _find_font('AnakotmaiBold.ttf')
_ANAKO_MED  = _find_font('Anakotmai-Medium.ttf') or _find_font('AnakotmaiMedium.ttf')

def _sys_font(sz, bold=False):
    for nm in ['segoeui', 'tahoma', 'arial', 'freesans', 'dejavusans']:
        try:
            f = pygame.font.SysFont(nm, sz, bold=bold)
            if f: return f
        except Exception:
            pass
    return pygame.font.Font(None, sz + 2)

def _afont(sz, bold=False):
    path = _ANAKO_BOLD if bold else (_ANAKO_MED or _ANAKO_BOLD)
    if path:
        try:
            return pygame.font.Font(path, sz)
        except Exception:
            pass
    return _sys_font(sz, bold)

# ── Unified font dict ──────────────────────────────────────
F = {
    'xs' : _afont(13, False),
    's'  : _afont(15, False),
    'm'  : _afont(18, False),
    'ml' : _afont(20, True),
    'l'  : _afont(26, True),
    'xl' : _afont(40, True),
    'xxl': _afont(60, True),
    'ttl': _afont(72, True),
}

def Fk():
    """Return the shared font dict."""
    return F

# ── Translation table ──────────────────────────────────────
TR = {
    # ── HUD ─────────────────────────────────────────────
    'EARTH HP':{'th':'HP โลก'},
    'MONEY':{'th':'เงิน'},
    'WAVE':{'th':'รอบ'},
    'ENEMIES':{'th':'ศัตรู'},
    'ATK BOOST':{'th':'พลังโจมตี'},
    # ── Difficulty labels ─────────────────────────────
    'EASY':{'th':'ง่าย'},
    'NORMAL':{'th':'ปกติ'},
    'HARD':{'th':'ยาก'},
    # ── Shop UI ───────────────────────────────────────
    'SHOP':{'th':'ร้านค้า'},
    'Aliens':{'th':'เอเลี่ยน'},
    'Support':{'th':'ซัพพอร์ต'},
    'CLICK MAP TO PLACE':{'th':'คลิกแผนที่เพื่อวาง'},
    'MAX':{'th':'เต็มแล้ว'},
    'Hover: range · ESC: cancel':{'th':'เลื่อนเมาส์: รัศมี · ESC: ยกเลิก'},
    # ── Tower names ───────────────────────────────────
    'Heatblast':{'th':'ฮีทบลาสต์'},
    'Four Arms':{'th':'โฟร์อาร์มส์'},
    'XLR8':{'th':'เอ็กซ์-เซเลอเรต'},
    'Diamondhead':{'th':'ไดมอนด์เฮด'},
    'Grandpa Max':{'th':'ปู่แม็กซ์'},
    'Ben 10':{'th':'เบ็นเท็น'},
    'Idin':{'th':'พรี่ไอดิน'},
    # ── Tower descs ───────────────────────────────────
    'Fast DPS · Cheap':{'th':'ยิงเร็ว · ถูก'},
    'Heavy damage · Short':{'th':'ดาเมจสูง · ระยะสั้น'},
    'Insane fire rate':{'th':'ยิงเร็วที่สุด'},
    'Sniper · Long range':{'th':'สไนเปอร์ · ระยะไกลมาก'},
    'Earns $50 / 10s':{'th':'รับเงิน $50 ทุก 10 วินาที'},
    '×2 ATK · $10 / 5s':{'th':'เพิ่มพลัง x2 · $10 ทุก 5 วิ'},
    # ── Announce ──────────────────────────────────────
    'EARTH HAS FALLEN':{'th':'โลกล่มสลายแล้ว!'},
    'VICTORY  —  EARTH SAVED!':{'th':'ชนะแล้ว — โลกปลอดภัย!'},
    # ── Menu ──────────────────────────────────────────
    ' PLAY':{'th':' เล่นเกม'},
    'QUIT':{'th':'ออกจากเกม'},
    'Tower Defense  |  6 Towers  |  3 Difficulties':
        {'th':'เกมป้องกัน · 6 ป้อม · 3 ระดับความยาก'},
    'Click to place towers  |  ESC: deselect  |  Hover tower: range':
        {'th':'คลิกวางป้อม · ESC ยกเลิก · เมาส์บนป้อม: รัศมี'},
    # ── Difficulty select ─────────────────────────────
    'SELECT DIFFICULTY':{'th':'เลือกระดับความยาก'},
    'Press 1 / 2 / 3  or  click':{'th':'กดปุ่ม 1 / 2 / 3 หรือคลิก'},
    '10 Waves':{'th':'10 รอบ'},
    '20 Waves':{'th':'20 รอบ'},
    '30 Waves':{'th':'30 รอบ'},
    'Fewer enemies':{'th':'ศัตรูน้อย'},
    'Low HP & slow':{'th':'HP ต่ำ & เคลื่อนที่ช้า'},
    'Generous income':{'th':'ได้เงินเยอะ'},
    'Boss on Wave 10':{'th':'บอสปรากฏรอบที่ 10'},
    'Standard count':{'th':'จำนวนศัตรูปกติ'},
    'Normal HP/speed':{'th':'HP และความเร็วปกติ'},
    'Normal income':{'th':'เงินรายได้ปกติ'},
    'Boss on Wave 20':{'th':'บอสปรากฏรอบที่ 20'},
    'Many enemies':{'th':'ศัตรูจำนวนมาก'},
    'High HP & fast':{'th':'HP สูง & เคลื่อนที่เร็ว'},
    'Scarce money':{'th':'เงินหายากมาก'},
    'Boss at Wave 15 & 30':{'th':'บอสปรากฎรอบที่ 15 และ 30'},
    # ── Story ─────────────────────────────────────────
    'SEASON 4 : FINAL WAR':{'th':'ซีซั่น 4 : สงครามครั้งสุดท้าย'},
    'Alien armies are invading Earth.':
        {'th':'กองทัพเอเลี่ยนบุกโจมตีโลก'},
    'Cities are burning.  Defenses have fallen.':
        {'th':'เมืองลุกเป็นไฟ  การป้องกันล่มสลาย'},
    'Ben Tennyson activates the Omnitrix...':
        {'th':'เบ็น เทนนีสัน สวมใส่ออมนิทริกซ์...'},
    '...and stands between humanity and extinction.':
        {'th':'...ยืนเป็นกำแพงกั้นระหว่างมนุษยชาติกับการสูญพันธุ์'},
    'The mastermind of this invasion:':
        {'th':'สมองกลเบื้องหลังการรุกรานครั้งนี้:'},
    'V I L G A X':{'th':'วิ ล แ ก็ ก ซ์'},
    '[ Click or press any key ]':
        {'th':'[ คลิก หรือกดปุ่มใดก็ได้ เพื่อดำเนินการต่อ ]'},
    # ── End screen ────────────────────────────────────
    'VILGAX DEFEATED!':{'th':'วิลแก็กซ์พ่ายแพ้แล้ว!'},
    "Vilgax's army retreats into deep space.":
        {'th':'กองทัพของวิลแก็กซ์ถอยทัพสู่ห้วงอวกาศลึก'},
    "Earth breathes again.  For now.":
        {'th':'โลกได้หายใจอีกครั้ง...แต่เพียงชั่วคราว'},
    "A mysterious signal pulses from the cosmos...":
        {'th':'สัญญาณลึกลับกระพริบมาจากห้วงจักรวาล...'},
    "Ben looks up.  This isn't over.":
        {'th':'เบ็นเงยหน้ามอง... เรื่องราวยังไม่จบ'},
    "Vilgax conquers the planet.":
        {'th':'วิลแก็กซ์ยึดครองโลกได้สำเร็จ'},
    "The Omnitrix goes dark.":
        {'th':'ออมนิทริกซ์ดับสนิท'},
    "All hope... is lost.":
        {'th':'ความหวังทั้งหมด...ได้สูญสิ้นแล้ว'},
    '[ Click or press any key  →  menu ]':
        {'th':'[ คลิก หรือกดปุ่มใดก็ได้ → กลับเมนู ]'},
    '[ Click / ENTER: continue  |  M: menu ]':
        {'th':'[ คลิก/ENTER: ดำเนินต่อ  |  M: เมนูหลัก ]'},
    '[ Click / ENTER: end  |  M: menu ]':
        {'th':'[ คลิก/ENTER: จบเกม  |  M: เมนูหลัก ]'},
    # ── In-game messages ──────────────────────────────
    'Next wave in':{'th':'คลื่นถัดไปใน'},
    'clear! +$50':{'th':'ผ่านรอบ! +$50'},
    'Vilgax is defeated.':{'th':'วิลแก็กซ์พ่ายแพ้แล้ว'},
    'Vilgax conquers the planet.2':{'th':'วิลแก็กซ์ยึดครองโลก'},
    'EARTH SAVED!':{'th':'โลกปลอดภัยแล้ว!'},
    'Start:':{'th':'เงินเริ่ม:'},
    'Base HP:':{'th':'HP ฐาน:'},
    # ── Wave announces ────────────────────────────────
    '⚠  VILGAX !':{'th':'⚠ วิลแก็กซ์ !'},
    'APPROACHES  EARTH':{'th':'กำลังมุ่งหน้าสู่โลก'},
    'VILGAX DEFEATED':{'th':'วิลแก็กซ์พ่ายแล้ว'},
    # ── Boss screen ───────────────────────────────────
    '⚠ VILGAX ⚠':{'th':'⚠ วิลแก็กซ์ ⚠'},
}

def tr(text):
    """Translate text based on current LANG setting."""
    if LANG[0] == 'th':
        return TR.get(str(text), {}).get('th', str(text))
    return str(text)
