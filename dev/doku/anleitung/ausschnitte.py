# Schneidet die App-Screenshots für die Anleitung zu (img/<name>.jpg, 780 px breit).
# Quellen: 390x844-Screens mit DSF=3, Kartenkacheln nur mit MAP=1 (Domain tiles.openfreemap.org muss erreichbar sein).
#   1) MAP=1 DSF=3 python3 dev/doku/screens.py dev/out/doku      (eigene Szenen + Kartensymbole sym_*.png)
#   2) MAP=1 DSF=3 python3 dev/tests/<test>.py                    (landen in dev/out/, siehe QUELLE)
#   3) python3 dev/doku/anleitung/ausschnitte.py dev/out/doku dev/out
import sys, os, glob, shutil
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(D, 'img')
# Name: (Quelldatei, y von, y bis) in CSS-Pixeln des 390x844-Screens; Kommentar = woher die Datei kommt
CROP = {
    'hunter_ping': ('hunter_ping.png', 0, 650),           # screens.py
    'hider_karte': ('hider_karte.png', 0, 425),           # screens.py
    'hider_draussen': ('hider_draussen.png', 0, 690),     # screens.py
    'fang_melden': ('fang_melden.png', 400, 770),         # screens.py
    'hider_panel': ('hider_panel.png', 425, 765),         # screens.py
    'hunter_bonus': ('hunter_bonus.png', 235, 615),       # screens.py
    'ux_fang_alarm': ('ux_fang_alarm.png', 215, 625),     # tests/ux_feinschliff.py
    'ux_lobby': ('ux_lobby.png', 175, 722),               # tests/ux_feinschliff.py
    'ux_ende': ('ux_ende.png', 140, 705),                 # tests/ux_feinschliff.py
    'briefing_hider': ('briefing_hider.png', 80, 768),    # tests/briefing.py
    'radar_kontakt': ('radar_kontakt.png', 0, 580),       # tests/radar.py
    'zombie_verwandlung': ('zombie_verwandlung.png', 270, 585),  # tests/zombie.py
    'kopfgeld_lobby': ('kopfgeld_lobby.png', 175, 640),   # tests/kopfgeld.py
    'fs_hider_alarm': ('fs_hider_alarm.png', 230, 612),   # tests/fang_starten.py
}
src = sys.argv[1:] or [os.path.join(D, '..', '..', 'out')]
def find(f):
    for s in src:
        p = os.path.join(s, f)
        if os.path.exists(p): return p
for n, (f, a, b) in CROP.items():
    p = find(f)
    if not p: print('fehlt:', f); continue
    im = Image.open(p).convert('RGB'); k = im.width / 390
    im.crop((0, int(a * k), im.width, int(b * k))).resize((780, int((b - a) * 2)), Image.LANCZOS).save(os.path.join(IMG, n + '.jpg'), quality=86)
for s in src:
    for p in glob.glob(os.path.join(s, 'sym_*.png')):
        im = Image.open(p).convert('RGBA'); im.crop(im.getbbox()).save(os.path.join(IMG, os.path.basename(p)))
print('ok')
