# Nimmt die echte App für das Erklärvideo auf (Playwright + Firebase-Stub, Kartenkacheln von openfreemap).
# Jede Szene: eigene Seite, Bilder per CDP-Screencast (JPEG q92) mit Zeitstempel → frames/<name>/NNNNN.jpg + times.json.
import os, json, time, base64, contextlib, shutil
from playwright.sync_api import sync_playwright

DEV = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(DEV)
STUB = open(os.path.join(DEV, 'memdb.js'), encoding='utf-8').read()
W, H, DSF = 390, 844, 2

# Tipp-Anzeige (Kreis, der kurz aufleuchtet) und Ausblenden des Testmodus-Balkens
INIT = r"""
addEventListener('DOMContentLoaded',()=>{
  const st=document.createElement('style');st.textContent=`
  .vtap{position:fixed;z-index:2147483647;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;
    background:rgba(255,255,255,.35);border:2px solid rgba(255,255,255,.9);box-shadow:0 0 0 1px rgba(0,0,0,.25),0 2px 10px rgba(0,0,0,.3);
    pointer-events:none;animation:vtap .55s ease-out forwards}
  @keyframes vtap{0%{transform:scale(.4);opacity:0}25%{transform:scale(1);opacity:1}100%{transform:scale(1.5);opacity:0}}`;
  document.head.appendChild(st);
  new MutationObserver(()=>{document.querySelectorAll('body>div').forEach(d=>{if((d.textContent||'').startsWith('TESTMODUS'))d.remove()})}).observe(document.body,{childList:true});
});
window.vtap=(x,y)=>{const d=document.createElement('div');d.className='vtap';d.style.left=x+'px';d.style.top=y+'px';document.body.appendChild(d);setTimeout(()=>d.remove(),700)};
"""

class Scene:
    def __init__(self, pg, cdp, out):
        self.pg, self.cdp, self.out = pg, cdp, out
        self.frames, self.t0, self.on = [], None, False
        cdp.on('Page.screencastFrame', self._frame)

    def _frame(self, p):
        try: self.cdp.send('Page.screencastFrameAck', {'sessionId': p['sessionId']})
        except Exception: pass
        if not self.on: return
        ts = p['metadata'].get('timestamp') or time.time()
        if self.t0 is None: self.t0 = ts
        n = len(self.frames)
        fn = os.path.join(self.out, '%05d.jpg' % n)
        open(fn, 'wb').write(base64.b64decode(p['data']))
        self.frames.append([round(ts - self.t0, 4), os.path.basename(fn)])

    def ev(self, js): return self.pg.evaluate(js)
    def wait(self, s): self.pg.wait_for_timeout(int(s * 1000))

    def start(self):
        self.ev("document.getElementById('toast')&&(document.getElementById('toast').innerHTML='');document.querySelectorAll('body>div').forEach(d=>{if((d.textContent||'').startsWith('TESTMODUS'))d.remove()})")
        self.wait(0.25)
        self.on = True
        self.cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 92, 'maxWidth': W * DSF, 'maxHeight': H * DSF, 'everyNthFrame': 1})
        # erster Frame kommt erst bei Änderung: kleine Bewegung erzwingen
        self.ev("document.body.style.outline='0px solid transparent'")
        self.wait(0.15)
        self.t_start = time.time()

    def stop(self):
        self.wait(0.2); self.on = False
        try: self.cdp.send('Page.stopScreencast')
        except Exception: pass
        dur = time.time() - self.t_start
        json.dump({'frames': self.frames, 'dur': dur}, open(os.path.join(self.out, 'times.json'), 'w'))
        return dur

    def tap(self, sel=None, xy=None, click=True, text=None):
        """Tipp sichtbar machen und auslösen. sel = CSS-Selektor, text = Knopftext (exakt oder Anfang)."""
        if text is not None:
            loc = self.pg.locator('button:visible', has_text=text).first
        elif sel:
            loc = self.pg.locator(sel).first
        else:
            loc = None
        if loc is not None:
            b = loc.bounding_box(); x, y = b['x'] + b['width'] / 2, b['y'] + b['height'] / 2
        else:
            x, y = xy
        self.ev(f"vtap({x},{y})"); self.wait(0.18)
        if click:
            if loc is not None: loc.click(force=True)
            else: self.pg.mouse.click(x, y)

    def typ(self, sel, txt, delay=0.11):
        self.tap(sel=sel)
        for ch in txt:
            self.pg.locator(sel).first.press(ch if ch != ' ' else 'Space'); self.wait(delay)

@contextlib.contextmanager
def scene(name, outdir, url='index.html', hash='#test'):
    out = os.path.join(outdir, name)
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(out)
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
        ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=DSF, has_touch=False)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('PE:' + str(e)))
        def route(r):
            u = r.request.url
            if 'vendor/firebase-' in u:
                return r.fulfill(body=STUB if 'app-compat' in u else '', content_type='application/javascript')
            if 'openfreemap' in u or 'maplibre' in u or u.startswith('file:'):
                return r.continue_()
            return r.abort()
        pg.route('**/*', route)
        pg.add_init_script(INIT)
        pg.goto('file://' + os.path.join(ROOT, url) + hash)
        pg.wait_for_timeout(600)
        cdp = ctx.new_cdp_session(pg)
        sc = Scene(pg, cdp, out)
        try:
            yield sc
        finally:
            if errs: print(name, 'Fehler:', errs[:3])
            b.close()
