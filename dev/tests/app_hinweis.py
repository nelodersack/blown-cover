# App-Hinweis für Android-Browser (§INTRO apChk/apGo): nur einmal, erst nach Begrüßung oder Intro
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from harness import app, shot
errs_all = []
def ok(c, m):
    print(('OK  ' if c else 'FEHLER ') + m)
    if not c: errs_all.append(m)
UA = "Object.defineProperty(navigator,'userAgent',{get:()=>'Mozilla/5.0 (Linux; Android 14) Chrome/120 Mobile'});"
INIT = 'window.__WEL=1;window.__APO=1;' + UA
# 1) Begrüßung überspringen → Hinweis; Neuladen → keiner mehr
with app(390, 844, hash='', init=INIT) as (pg, ev, errs):
    pg.wait_for_timeout(900)
    ok(ev("!!$('wel')") and not ev("!!$('apo')"), 'erst Begrüßung, noch kein App-Hinweis')
    ev("welGo(0)"); pg.wait_for_timeout(1000)
    ok(ev("!!$('apo')"), 'App-Hinweis nach Überspringen')
    shot(pg, 'app_hinweis.png')
    ev("apGo(0)"); pg.wait_for_timeout(600)
    ok(not ev("!!$('apo')"), 'Später schließt')
    pg.reload(); pg.wait_for_timeout(900)
    ok(not ev("!!$('apo')") and not ev("!!$('wel')"), 'nach Neuladen nichts mehr')
    print('errors:', errs); errs_all += errs
# 2) Intro bis zum Ende → „Zurück zum Menü“ → Hinweis
with app(390, 844, hash='', init=INIT) as (pg, ev, errs):
    pg.wait_for_timeout(900)
    ev("welGo(1)"); pg.wait_for_timeout(600)
    ok(not ev("!!$('apo')"), 'während des Intros kein Hinweis')
    ev("inStep(INS.length-1,1)"); pg.wait_for_timeout(400)
    ev("$('intro').querySelector('.innx').click()"); pg.wait_for_timeout(800)
    ok(ev("!!$('apo')"), 'App-Hinweis nach dem Intro')
    print('errors:', errs); errs_all += errs
# 3) Kein Android → nie; in der App (NB) → nie
with app(390, 844, hash='', init='window.__WEL=1;window.__APO=1') as (pg, ev, errs):
    pg.wait_for_timeout(900); ev("welGo(0)"); pg.wait_for_timeout(1000)
    ok(not ev("!!$('apo')"), 'ohne Android kein Hinweis')
    print('errors:', errs); errs_all += errs
print('errors:', errs_all)
sys.exit(1 if errs_all else 0)
