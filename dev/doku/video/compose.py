# Setzt das Erklärvideo zusammen: Dossier-Rahmen (HTML → PNG), App-Aufnahmen, Untertitel, Stimme.
# Aufruf: python3 dev/doku/video/compose.py <arbeitsordner>   → <arbeitsordner>/Blown_Cover_Erklaervideo.mp4
import os, sys, json, subprocess, wave, shutil
import numpy as np
from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(D), 'anleitung', 'fonts')
WORK = sys.argv[1]
FR, OV, CL = [os.path.join(WORK, x) for x in ('frames', 'ov', 'clips')]
for x in (OV, CL): os.makedirs(x, exist_ok=True)
META = json.load(open(os.path.join(WORK, 'tts', 'meta.json')))
LEAD, GAP, FPS = 0.8, 0.45, 30
VW, VH = 1080, 1920
SX, SY, SW, SH = 215, 300, 650, 1406           # App-Bildschirm im Bild
BZ = 16                                         # Rahmenbreite des Telefons

ANNA = ('Anna', 'Hunter', '#1c5fd6', 'tri'); LENA = ('Lena', 'Hider', '#e3cc1f', 'circ'); TOM = ('Tom', 'Hider', '#0fb5ae', 'circ')
HOST = ('Anna', 'Host', '#1c5fd6', 'tri')
# Szene: Titel, [(Aufnahme, von, bis | None = Ende, Sicht)]
SCENES = [
    (1, 'Blown Cover', [('s01', 0, None, None)]),
    (2, 'In die Lobby', [('s02a', 0, None, HOST), ('s02b', 0, None, LENA)]),
    (3, 'Zwei Seiten', [('s03', 0, None, HOST)]),
    (4, 'Das Briefing', [('s04', 0, None, LENA)]),
    (5, 'Die Zone', [('s05', 0, None, LENA)]),
    (6, 'Der Ping', [('s06', 0, None, ANNA), ('s06b', 0, 3.0, LENA)]),
    (7, 'Aufgabe: Safehouse', [('s07', 0, None, LENA)]),
    (8, 'Der Fang', [('s08a', 0, 3.9, ANNA), ('s08b', 0, None, TOM), ('s08c', 0, None, ANNA)]),
    (9, 'Bonus: Extra-Ping', [('s09', 0, None, ANNA)]),
    (10, 'Wer gewinnt', [('s10', 0, None, LENA)]),
]

def font_css():
    f = lambda fam, w, fn, st='normal': f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:{st};src:url(file://{FONTS}/{fn})}}'
    return (f('Plex Serif', 400, 'fontsource-ibm-plex-serif/files/ibm-plex-serif-latin-400-normal.woff2') +
            f('Plex Serif', 600, 'fontsource-ibm-plex-serif/files/ibm-plex-serif-latin-600-normal.woff2') +
            f('Plex Serif', 400, 'fontsource-ibm-plex-serif/files/ibm-plex-serif-latin-400-italic.woff2', 'italic') +
            f('Plex Mono', 400, 'fontsource-ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2') +
            f('Plex Mono', 600, 'fontsource-ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2') +
            f('Plex Mono', 700, 'fontsource-ibm-plex-mono/files/ibm-plex-mono-latin-700-normal.woff2'))

BASE = f"""<style>{font_css()}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:{VW}px;height:{VH}px;background:transparent;overflow:hidden}}
:root{{--ink:#1d1b18;--muted:#6b665c;--red:#a8261f;--rule:#2a2723}}
.paper{{position:absolute;inset:0;background:url(file://{WORK}/paper_hd.jpg) center/cover}}
.cls{{position:absolute;left:0;right:0;text-align:center;font:700 25px 'Plex Mono';letter-spacing:.5em;color:var(--red)}}
.hdr{{position:absolute;left:70px;right:70px;top:84px;display:flex;justify-content:space-between;border-top:4px solid var(--rule);border-bottom:1.5px solid var(--rule);padding:10px 0 9px;
  font:600 21px 'Plex Mono';letter-spacing:.16em;text-transform:uppercase;color:var(--ink)}}
.hdr .m{{color:var(--muted);font-weight:400}}
.ttl{{position:absolute;left:70px;right:70px;top:152px;text-align:center;font:600 58px/1.05 'Plex Serif';color:var(--ink);letter-spacing:-.005em}}
.sight{{position:absolute;left:0;right:0;top:232px;display:flex;justify-content:center;align-items:center;gap:14px;font:600 21px 'Plex Mono';letter-spacing:.18em;text-transform:uppercase;color:var(--muted)}}
.sight b{{color:var(--ink);font-weight:600}}
.phone{{position:absolute;left:{SX-BZ}px;top:{SY-BZ}px;width:{SW+2*BZ}px;height:{SH+2*BZ}px;border-radius:64px;background:#15171a;
  box-shadow:0 2px 0 rgba(255,255,255,.06) inset,0 30px 60px rgba(40,30,10,.35),0 8px 18px rgba(40,30,10,.25)}}
.hole{{position:absolute;left:{SX}px;top:{SY}px;width:{SW}px;height:{SH}px;border-radius:48px;box-shadow:0 0 0 2px #0b0c0e}}
.sub{{position:absolute;left:80px;right:80px;top:1742px;height:130px;display:flex;align-items:center;justify-content:center;text-align:center;
  font:400 41px/1.28 'Plex Serif';color:var(--ink)}}
</style>"""

def sight_html(s):
    if not s: return ''
    n, r, col, sh = s
    g = (f'<svg width="30" height="30" viewBox="0 0 36 36"><polygon points="18,4 32,30 4,30" fill="{col}" stroke="#fff" stroke-width="2.5" stroke-linejoin="round"/></svg>' if sh == 'tri'
         else f'<svg width="30" height="30" viewBox="0 0 36 36"><circle cx="18" cy="18" r="12" fill="{col}" stroke="#fff" stroke-width="2.5"/></svg>')
    return f'<div class="sight">Sicht {g} <b>{n}</b> · {r}</div>'

def render(pg, html, out, transparent=False):
    fn = os.path.join(OV, '_page.html')
    open(fn, 'w').write(f'<!DOCTYPE html><html><head><meta charset="utf-8">{BASE}</head><body>{html}</body></html>')
    pg.goto('file://' + fn); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
    pg.screenshot(path=out, omit_background=transparent)

def overlays():
    """Hintergrund je Aufnahme (Papier, Kopf, Titel, Telefon) + Rahmen über dem Bildschirm + Untertitel je Satz."""
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': VW, 'height': VH})
        for n, title, clips in SCENES:
            for name, a, z, s in clips:
                render(pg, f"""<div class=paper></div><div class=cls style="top:34px">GEHEIM</div>
                  <div class=hdr><span>Blown Cover <span class=m>· Einsatzeinweisung</span></span><span><span class=m>Szene</span> {n:02d} / 10</span></div>
                  <div class=ttl>{title}</div>{sight_html(s)}<div class=phone></div>
                  <div class=cls style="top:1878px;font-size:21px">GEHEIM</div>""", os.path.join(OV, f'bg_{name}.png'))
            for i, m in enumerate(META[str(n)]):
                render(pg, f'<div class=sub>{m["text"]}</div>', os.path.join(OV, f'sub_{n:02d}_{i}.png'), True)
        # Rahmenkante über dem Bildschirm (runde Ecken)
        render(pg, f"""<svg width="{VW}" height="{VH}" style="position:absolute;left:0;top:0"><defs><mask id="m"><rect width="{VW}" height="{VH}" fill="#fff"/>
          <rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="46" fill="#000"/></mask></defs>
          <rect x="{SX-BZ}" y="{SY-BZ}" width="{SW+2*BZ}" height="{SH+2*BZ}" rx="64" fill="#15171a" mask="url(#m)"/></svg>""", os.path.join(OV, 'bezel.png'), True)
        # Vor- und Abspann
        render(pg, f"""<div class=paper></div><div class=cls style="top:34px">GEHEIM</div>
          <div class=hdr><span>Blown Cover <span class=m>· Einsatzeinweisung</span></span><span class=m>AZ BC-26/07</span></div>
          <div style="position:absolute;left:0;right:0;top:640px;text-align:center;font:700 150px/0.98 'Plex Serif';color:var(--ink)">BLOWN<br>COVER</div>
          <div style="position:absolute;left:0;right:0;top:985px;text-align:center;font:600 26px 'Plex Mono';letter-spacing:.34em;color:var(--muted)">EINSATZEINWEISUNG</div>
          <div style="position:absolute;left:300px;top:1120px;width:480px;transform:rotate(-7deg)">{STAMP}</div>
          <div class=cls style="top:1878px;font-size:21px">GEHEIM</div>""", os.path.join(OV, 'intro.png'))
        render(pg, f"""<div class=paper></div><div class=cls style="top:34px">GEHEIM</div>
          <div class=hdr><span>Blown Cover <span class=m>· Einsatzeinweisung</span></span><span class=m>Ende</span></div>
          <div style="position:absolute;left:0;right:0;top:700px;text-align:center;font:700 120px/0.98 'Plex Serif';color:var(--ink)">BLOWN<br>COVER</div>
          <div style="position:absolute;left:0;right:0;top:990px;text-align:center;font:600 46px 'Plex Mono';letter-spacing:.06em;color:var(--red)">blowncover.app</div>
          <div style="position:absolute;left:0;right:0;top:1075px;text-align:center;font:400 italic 32px 'Plex Serif';color:var(--muted)">Spielregeln und App unter dem Link.</div>
          <div class=cls style="top:1878px;font-size:21px">GEHEIM</div>""", os.path.join(OV, 'outro.png'))
        b.close()

STAMP = """<svg viewBox="0 0 220 70" width="480"><defs><filter id="ink" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.55" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in" result="c"/>
<feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="1" seed="9" result="w"/><feDisplacementMap in="c" in2="w" scale="2.2"/></filter></defs>
<g filter="url(#ink)" fill="none" stroke="#b02a24" opacity=".9"><rect x="4" y="4" width="212" height="62" rx="3" stroke-width="3.2"/><rect x="9" y="9" width="202" height="52" rx="2" stroke-width="1.2"/>
<text x="110" y="45" text-anchor="middle" fill="#b02a24" stroke="none" font-family="Plex Mono" font-weight="700" font-size="25" letter-spacing="3">GEHEIM</text></g></svg>"""

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(' '.join(cmd)[:300]); print(r.stderr[-1500:]); raise SystemExit(1)

def clip_raw(name, a, z):
    """Aufnahme als Video mit fester Bildrate (Bildschirmgröße SW x SH)."""
    T = json.load(open(os.path.join(FR, name, 'times.json'))); F = T['frames']
    end = T['dur'] if z is None else z
    lst = os.path.join(CL, f'{name}.txt')
    with open(lst, 'w') as f:
        for i, (t, fn) in enumerate(F):
            nt = F[i + 1][0] if i + 1 < len(F) else end
            t0, t1 = max(t, a), min(nt, end)
            if t1 <= t0: continue
            f.write(f"file '{os.path.join(FR, name, fn)}'\nduration {t1 - t0:.4f}\n")
        f.write(f"file '{os.path.join(FR, name, F[-1][1])}'\n")
    out = os.path.join(CL, f'{name}_raw.mp4'); tmp = out + '.tmp.mp4'
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', f'scale={SW}:{SH}:flags=lanczos,fps={FPS},format=yuv420p',
         '-t', f'{end - a:.3f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', tmp])
    os.replace(tmp, out)
    return end - a

def dur(fn):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', fn], capture_output=True, text=True).stdout)

def scene_file(n, clips, lens):
    """Szene: Hintergründe wechseln mit der Aufnahme, Bildschirm, Rahmen, Untertitel mit weicher Blende."""
    total = sum(lens)
    meta = META[str(n)]; t, cues = LEAD, []
    for m in meta: cues.append((t, t + m['dur'])); t += m['dur'] + GAP
    ins, fl, k = [], [], 0
    # Bildschirm: Aufnahmen der Szene hintereinander
    for name, *_ in clips: ins += ['-i', os.path.join(CL, f'{name}_raw.mp4')]
    fl.append(''.join(f'[{i}:v]' for i in range(len(clips))) + f'concat=n={len(clips)}:v=1:a=0[scr]')
    base = len(clips)
    for name, *_ in clips: ins += ['-loop', '1', '-framerate', str(FPS), '-t', f'{total:.3f}', '-i', os.path.join(OV, f'bg_{name}.png')]
    ins += ['-loop', '1', '-framerate', str(FPS), '-t', f'{total:.3f}', '-i', os.path.join(OV, 'bezel.png')]
    nsub = len(meta)
    for i in range(nsub): ins += ['-loop', '1', '-framerate', str(FPS), '-t', f'{total:.3f}', '-i', os.path.join(OV, f'sub_{n:02d}_{i}.png')]
    # Hintergrund je Abschnitt
    cur, t0 = None, 0.0
    for j, L in enumerate(lens):
        src = f'[{base + j}:v]'
        if cur is None:
            fl.append(f'{src}format=yuv420p[b{j}]'); cur = f'[b{j}]'
        else:
            fl.append(f"{cur}{src}overlay=0:0:enable='gte(t,{t0:.3f})'[b{j}]"); cur = f'[b{j}]'
        t0 += L
    fl.append(f'{cur}[scr]overlay={SX}:{SY}[v0]')
    fl.append(f'[v0][{base + len(clips)}:v]overlay=0:0[v1]'); cur = '[v1]'
    for i, (a, z) in enumerate(cues):
        a2, z2 = a - 0.1, min(total, (cues[i + 1][0] - 0.12) if i + 1 < nsub else z + 0.9)
        si = base + len(clips) + 1 + i
        fl.append(f"[{si}:v]format=rgba,fade=t=in:st={a2:.3f}:d=0.18:alpha=1,fade=t=out:st={z2 - 0.18:.3f}:d=0.18:alpha=1[s{i}]")
        fl.append(f"{cur}[s{i}]overlay=0:0:enable='between(t,{a2:.3f},{z2:.3f})'[v{i + 2}]"); cur = f'[v{i + 2}]'
    out = os.path.join(CL, f'scene_{n:02d}.mp4'); tmp = out + '.tmp.mp4'
    run(['ffmpeg', '-y', '-v', 'error'] + ins + ['-filter_complex', ';'.join(fl), '-map', cur, '-t', f'{total:.3f}', '-r', str(FPS),
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp])
    os.replace(tmp, out)
    return total, cues

def still(png, secs, out, fade_in=0.0, fade_out=0.0):
    vf = f'format=yuv420p,loop=-1:1,trim=duration={secs}'
    if fade_in: vf += f',fade=t=in:st=0:d={fade_in}'
    if fade_out: vf += f',fade=t=out:st={secs - fade_out}:d={fade_out}'
    tmp = out + '.tmp.mp4'
    run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', png, '-vf', vf, '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp])
    os.replace(tmp, out)

def read_wav(fn):
    with wave.open(fn) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return sr, x

if __name__ == '__main__':
    overlays(); print('Einblendungen ok', flush=True)
    INTRO, OUTRO = 2.2, 3.0
    still(os.path.join(OV, 'intro.png'), INTRO, os.path.join(CL, 'scene_00.mp4'), fade_in=0.5)
    parts, starts, t = [os.path.join(CL, 'scene_00.mp4')], {}, INTRO
    for n, title, clips in SCENES:
        lens = [clip_raw(name, a, z) for name, a, z, s in clips]
        total, cues = scene_file(n, clips, lens)
        starts[n] = (t, cues); t += total
        parts.append(os.path.join(CL, f'scene_{n:02d}.mp4')); print('Szene', n, round(total, 2), 's', flush=True)
    still(os.path.join(OV, 'outro.png'), OUTRO, os.path.join(CL, 'scene_99.mp4'), fade_out=0.8)
    parts.append(os.path.join(CL, 'scene_99.mp4')); t += OUTRO
    lst = os.path.join(CL, 'all.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    vid = os.path.join(CL, 'video.mp4')
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid])
    # Tonspur: Sätze an ihren Zeitpunkten
    sr = 22050; track = np.zeros(int((t + 0.5) * sr), np.float32)
    for n, (st, cues) in starts.items():
        for (a, z), m in zip(cues, META[str(n)]):
            _, x = read_wav(os.path.join(WORK, m['file'])); i = int((st + a) * sr); track[i:i + len(x)] += x
    pk = np.abs(track).max(); track = track / pk * 0.89 if pk > 0 else track
    wav = os.path.join(CL, 'voice.wav')
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((track * 32767).astype(np.int16).tobytes())
    out = os.path.join(WORK, 'Blown_Cover_Erklaervideo.mp4'); tmp = out + '.tmp.mp4'
    run(['ffmpeg', '-y', '-v', 'error', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'highpass=f=70,acompressor=threshold=-18dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=9',
         '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-shortest', tmp])
    os.replace(tmp, out); print(out, round(t, 1), 's')
