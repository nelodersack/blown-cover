# Test: Hunter sieht offene Fangmeldung („Warte auf …“), keine Doppelmeldung; Meldungen „geschützt“ vs. „kein Signal“; Meeting-Schnellnachrichten
import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ux_feinschliff.py')).read().split('# 1 Lobby')[0])
TO="window.__toasts=[];const _t=toast;window.toast=m=>{__toasts.push(String(m));return _t(m)}"
with app(390,844) as (pg,ev,errs):
    game(ev,'u1');go(ev,pg);pg.wait_for_timeout(800);ev(TO)
    ev("__T.games.K7QF.catches.u2={hunter:'u1',t:Date.now()-8000,status:'pending'};notify()");pg.wait_for_timeout(1300)
    w=ev("(document.querySelector('.cwt')||{}).textContent||''");print('Karte:',w);assert 'Warte auf Lena' in w and '0:2' in w
    ev("cc()");pg.wait_for_timeout(300);assert ev("document.querySelector('.cgt.off b').textContent")=='Lena'
    ev("(()=>{const r0=db.ref.bind(db);window.__S=[];db.ref=p=>{const r=r0(p);r.set=v=>{__S.push(p);return Promise.resolve()};return r}})()")
    ev("rq('u2')");pg.wait_for_timeout(200);print(ev("__toasts.slice(-1)[0]"));assert 'läuft schon' in ev("__toasts.slice(-1)[0]") and ev("__S.length")==0
    ev("rq('u3')");pg.wait_for_timeout(300);assert ev("__S.length")==1 and 'Max gesendet' in ev("__toasts.slice(-1)[0]")
    shot(pg,'fang_warten')
    # Live-Ortung: kein Signal vs. geschützt
    ev("__T.games.K7QF.hb={u1:{x1:{k:'live',av:Date.now()-1000}}};clearInterval(__k);const p=__T.games.K7QF.players;p.u3.ts=Date.now()-75000;p.u4.immUntil=Date.now()+60000;notify()");pg.wait_for_timeout(600)
    ev("hbLive='x1';hbLock=0;hbLiveGo('u3')");m=ev("__toasts.slice(-1)[0]");print(m);assert 'Max hat gerade kein Signal (letzter Standort vor 1:1' in m
    ev("hbLock=0;hbLiveGo('u4')");m=ev("__toasts.slice(-1)[0]");print(m);assert m.startswith('Tom ist gerade geschützt')
    print('errors:',[e for e in errs if 'PE:' in e]);assert not [e for e in errs if 'PE:' in e]
with app(390,844) as (pg,ev,errs):
    game(ev,'u2');go(ev,pg);pg.wait_for_timeout(1200);ev("chToggle(true)");pg.wait_for_timeout(400)
    q=ev("[...document.querySelectorAll('#chq button')].map(b=>b.textContent)");print(q);assert 'Wo treffen wir uns?' in q and 'Bin am Treffpunkt' not in q
    assert not [e for e in errs if 'PE:' in e]
