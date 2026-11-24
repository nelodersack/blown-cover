# Begrüßung beim allerersten Öffnen (§INTRO welChk/welGo) + Hinweis auf dem Einladungsbildschirm
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from harness import app, shot
errs_all = []
def ok(c, m):
    print(('OK  ' if c else 'FEHLER ') + m)
    if not c: errs_all.append(m)
INIT = 'window.__WEL=1'
with app(390, 844, hash='', init=INIT) as (pg, ev, errs):
    pg.wait_for_timeout(900)
    ok(ev("!!$('wel')"), 'Begrüßung bei ganz Neuen sichtbar')
    shot(pg, 'begruessung.png')
    ok(not ev("!!$('inb')&&getComputedStyle($('inb')).display!=='none'&&$('wel').contains($('inb'))"), 'Knopf nicht im Begrüßungsfenster')
    ev("$('wel').querySelector('button').click()"); pg.wait_for_timeout(900)
    ok(not ev("!!$('wel')"), 'Begrüßung nach So-gehts weg')
    ok(ev("!!IN&&IN.i===0"), 'Intro startet bei Schritt 1')
    ok(ev("LS.inS==='1'"), 'Intro als gesehen gemerkt')
    ev("inClose()"); pg.reload(); pg.wait_for_timeout(900)
    ok(not ev("!!$('wel')"), 'nach dem Intro keine Begrüßung mehr')
    ev("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(900)
    ok(ev("!!$('wel')"), 'nach Zurücksetzen wieder da')
    ev("$('wel').querySelector('.slink').click()"); pg.wait_for_timeout(700)
    ok(not ev("!!$('wel')") and not ev("!!IN"), 'Überspringen schließt ohne Intro')
    pg.reload(); pg.wait_for_timeout(900)
    ok(not ev("!!$('wel')"), 'nach Überspringen nicht mehr')
    ev("localStorage.clear();localStorage.setItem('n','Max')"); pg.reload(); pg.wait_for_timeout(900)
    ok(not ev("!!$('wel')"), 'mit gespeichertem Namen keine Begrüßung')
    errs_all += errs
with app(390, 844, page='index.html?c=KQWX', hash='', init=INIT) as (pg, ev, errs):
    pg.wait_for_timeout(900)
    ok(not ev("!!$('wel')"), 'Einladungslink: keine Begrüßung')
    ok(ev("[...document.querySelectorAll('#panel .slink')].some(b=>/Neu hier/.test(b.textContent))"), 'Einladungslink: Hinweis „Neu hier?“')
    shot(pg, 'begruessung_einladung.png')
    errs_all += errs
with app(390, 844, hash='') as (pg, ev, errs):
    pg.wait_for_timeout(900)
    ok(not ev("!!$('wel')"), 'Testumgebung ohne __WEL: keine Begrüßung')
    errs_all += errs
print('errors:', errs_all)
sys.exit(1 if errs_all else 0)
