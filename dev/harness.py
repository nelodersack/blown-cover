"""Testumgebung für index.html: Chromium (Playwright) + Firebase-Stub (memdb.js).

Benutzung in einem Test (dev/tests/*.py):
    from harness import app, OUT
    with app() as (pg, ev, errs):
        ev("...JS im Seitenkontext...")      # __T = In-Memory-Datenbank, notify() löst Listener aus
        pg.wait_for_timeout(500)
        print('errors:', errs)

Die Seite läuft mit #test (Positionen per Kartenklick, sessionStorage). Vendor-Dateien
kommen aus dem Repo (vendor/), Firebase wird durch memdb.js ersetzt, MapLibre und
Kacheln werden nicht geladen (Leaflet-Rasterfallback ohne Netz).
"""
import os, contextlib
from playwright.sync_api import sync_playwright

DEV = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DEV)
OUT = os.path.join(DEV, 'out')          # Screenshots (in .gitignore)
STUB = open(os.path.join(DEV, 'memdb.js'), encoding='utf-8').read()
os.makedirs(OUT, exist_ok=True)


@contextlib.contextmanager
def app(width=400, height=800, page='index.html', hash='#test', init=None):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_context(viewport={'width': width, 'height': height}, device_scale_factor=float(os.environ.get('DSF', '1'))).new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('PE:' + str(e)))
        pg.on('console', lambda m: errs.append('C:' + m.text)
              if m.type == 'error' and 'Failed to load' not in m.text else None)

        def route(r):
            u = r.request.url
            if 'vendor/firebase-' in u:
                return r.fulfill(body=STUB if 'app-compat' in u else '', content_type='application/javascript')
            if 'maplibre' in u and u.endswith('.js'):
                return r.fulfill(body='', content_type='application/javascript')
            if u.startswith('file:'):
                return r.continue_()
            return r.abort()
        pg.route('**/*', route)
        if init:
            pg.add_init_script(init)
        wlog = os.environ.get('WLOG')            # Schreibprotokoll für die Regelprüfung (dev/rules/)
        if wlog:
            pg.add_init_script('window.__WLOG=1')
        pg.goto('file://' + os.path.join(ROOT, page) + hash)
        pg.wait_for_timeout(500)
        try:
            yield pg, (lambda s: pg.evaluate(s)), errs
        finally:
            if wlog:
                try:
                    import json, sys, time
                    w = pg.evaluate('JSON.stringify(window.__W||[])')
                    os.makedirs(wlog, exist_ok=True)
                    name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
                    open(os.path.join(wlog, '%s_%d.json' % (name, time.time() * 1000)), 'w').write(w)
                except Exception:
                    pass
            b.close()


def shot(pg, name):
    pg.screenshot(path=os.path.join(OUT, name))
