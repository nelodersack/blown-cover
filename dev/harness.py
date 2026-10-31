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
def app(width=400, height=800, page='index.html'):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_context(viewport={'width': width, 'height': height}).new_page()
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
        pg.goto('file://' + os.path.join(ROOT, page) + '#test')
        pg.wait_for_timeout(500)
        try:
            yield pg, (lambda s: pg.evaluate(s)), errs
        finally:
            b.close()


def shot(pg, name):
    pg.screenshot(path=os.path.join(OUT, name))
