"""Spielerklärung (§INTRO): Knopf auf dem Startbildschirm, alle Schritte, Ansichten und Aktionen ohne Fehler,
Schließen stellt Karte und Panel wieder her, Knopf weg in Lobby/Spiel, Einladungslink zeigt „Lobby … beitreten“."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from harness import app, shot

with app(390, 844, hash='') as (pg, ev, errs):
    pg.wait_for_timeout(600)
    assert ev("getComputedStyle($('inb')).display") != 'none', 'Knopf fehlt'
    assert ev("$('inb').classList.contains('new')"), 'Punkt für Neue fehlt'
    z0 = ev("map.getZoom()")
    pg.click('#inb'); pg.wait_for_timeout(1500)
    assert ev("document.body.classList.contains('inx')") and ev("getComputedStyle($('panel')).display") == 'none'
    n = ev("INS.length")
    for i in range(n):
        ev(f"inStep({i},1)"); pg.wait_for_timeout(300)
        for v in ev(f"(INS[{i}].vw||INS[{i}].tabs||[[null]]).map(x=>x[0])"):
            if v: ev(f"inView('{v}')"); pg.wait_for_timeout(200)
            na = ev("(INS[IN.i].act?INS[IN.i].act(inV()):[]).length")
            for a in range(na):
                ev("IN.busy=0;inAct()"); pg.wait_for_timeout(3600)
            if na:
                assert 'Noch einmal' in ev("$('inact').textContent"), (i, v, ev("$('inact').textContent"))
                ev("IN.busy=0;inAct()"); pg.wait_for_timeout(200)
                assert ev("IN.a") == 0
        assert ev("$('intro').scrollHeight") > 0
    assert ev("$('intro').textContent.includes('Spiel erstellen')")
    shot(pg, 'intro_ende.png')
    ev("inClose()"); pg.wait_for_timeout(200)
    assert not ev("document.body.classList.contains('inx')")
    assert ev("$('hud').innerHTML") == '' and ev("$('inbx').className") == ''
    assert abs(ev("map.getZoom()") - z0) < .01, 'Karte nicht zurückgesetzt'
    assert not ev("$('inb').classList.contains('new')")
    # Lobby: Knopf verschwindet, offene Erklärung schließt sich
    pg.click('#inb'); pg.wait_for_timeout(300)
    ev("__T['.info']={connected:true};__T.games={KQWX:{host:'u1',status:'lobby',rn:1,c:{lat:47.07,lng:15.44},s:{r0:900,rMin:400,shrink:4,step:55,head:5,dur:60,ping:180,mode:'survive'},players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0}}}};uid='u1';pos={lat:47.07,lng:15.44};lastFix=Date.now();notify();$('cd').value='KQWX';jn()")
    pg.wait_for_timeout(800)
    print('G',ev('!!G'),ev('IN&&IN.i'));assert ev("!!G") and ev("IN") is None, 'Erklärung bleibt in der Lobby offen'
    assert ev("getComputedStyle($('inb')).display") == 'none'
    print('errors:', errs)
    assert not errs

with app(390, 844, hash='?c=ABCD') as (pg, ev, errs):
    pg.wait_for_timeout(600)
    pg.click('#inb'); pg.wait_for_timeout(300)
    ev("inStep(INS.length-1,1)")
    assert 'Lobby ABCD beitreten' in ev("$('intro').textContent")
    print('errors:', errs)
    assert not errs

# Introspiel in Teilen (25.11.): Weiter Teil für Teil, Sicht-Hinweis bei need, Spotlight/Pulsieren, Zurück
with app(390, 844, hash='') as (pg, ev, errs):
    pg.wait_for_timeout(500)
    pg.click('#inb'); pg.wait_for_timeout(1500)
    last = ev("INS.map((s,i)=>s.p?i:-1).filter(i=>i>=0).pop()")
    seen = 0
    for _ in range(80):
        k = ev("[IN.i,IN.j]")
        pt = ev("JSON.stringify({t:inPt().t,need:inPt().need||null,spot:inPt().spot||null,pulse:inPt().pulse||null})")
        import json; pt = json.loads(pt)
        assert abs(ev("IN.t") - pt['t']) < .01, (k, ev("IN.t"), pt)
        if pt['need'] and ev("inV()") not in pt['need']:
            assert ev("$('intro').querySelector('.innx').disabled"), ('Weiter nicht gesperrt', k)
            assert 'Tippe oben' in ev("$('intro').querySelector('.inp').textContent")
            pg.wait_for_timeout(300)
            assert ev("!!document.querySelector('.inspt')"), ('Reiter ohne Ring', k)
            ev(f"inView('{pt['need'][0]}')")
        pg.wait_for_timeout(450 + max(0, ev("Math.round((IN.fe||0)-performance.now())")))
        if pt['spot']:
            assert ev("!!$('insp')&&$('insp').classList.contains('on')"), ('Spotlight fehlt', k, pt)
            if k == [0, 2] or k == [5, 1]: shot(pg, f'intro_teil_{k[0]}_{k[1]}.png')
        if pt['pulse']:
            assert ev("document.querySelectorAll('.inpl').length") > 0, ('Pulsieren fehlt', k, pt)
        seen += 1
        if k[0] == last and k[1] == ev(f"INS[{last}].p.length-1"): break
        ev("inNext()")
        for _ in range(80):
            pg.wait_for_timeout(250)
            if not ev("IN.play"): break
    assert seen >= 25, seen
    assert 'Hider gewinnen' in ev("$('inbx').textContent")
    ev("inNext()"); pg.wait_for_timeout(300)
    assert ev("IN.i") == last + 1 and not ev("!!$('insp')&&$('insp').classList.contains('on')")
    ev("inBack()"); pg.wait_for_timeout(300)
    assert ev("[IN.i,IN.j]") == [last, ev(f"INS[{last}].p.length-1")]
    ev("inStep(4,1,2)"); pg.wait_for_timeout(200)
    for v in ['all', 'h', 'x']:
        ev(f"inView('{v}')"); pg.wait_for_timeout(100)
    assert ev("$('inbx').classList.contains('on')"), 'Fangmeldung fehlt beim Hider'
    ev("$('inbx').querySelector('.fy').click()"); pg.wait_for_timeout(2500)
    assert ev("[IN.i,IN.j]") == [4, 3], ev("[IN.i,IN.j]")
    ev("IN.gv='all';inStep(0,1)"); pg.wait_for_timeout(200)
    assert ev("!IN.mk.a&&!IN.mk.b"), 'Hunter in 1a sichtbar'
    ev("inNext()"); pg.wait_for_timeout(200)
    assert ev("!!IN.mk.a&&!!IN.mk.b"), 'Hunter in 1b fehlen'
    print('errors:', errs)
    assert not errs
