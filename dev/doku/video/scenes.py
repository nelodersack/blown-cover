# Szenen des Erklärvideos. Aufruf: python3 dev/doku/video/scenes.py <arbeitsordner> [szene …]
# Braucht <arbeitsordner>/tts/meta.json (Sprechzeiten je Satz, aus tts.py), damit die Aktionen zum Text passen.
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import scene

WORK = sys.argv[1]
OUT = os.path.join(WORK, 'frames')
META = json.load(open(os.path.join(WORK, 'tts', 'meta.json')))
LEAD, GAP = 0.8, 0.45

def cues(n):
    t, c = LEAD, []
    for m in META[str(n)]:
        c.append(t); t += m['dur'] + GAP
    return c, t - GAP   # Satzanfänge, Ende des Textes

# Spiel: Graz Innenstadt, Voreinstellung 60 Min (preOf(60))
S = ("{r0:900,rMin:400,shrink:4,step:55,head:5,dur:60,ping:180,pen:2,mode:'survive',taskR:0,imm:180,shOn:true,shT:20,evT:8,"
     "ddN:0,ddT:8,mtN:0,mtT:15,bon:true,hbOn:true,hbN:2,hbC:90,hbL:70,hbT:30,gw:20,gd:60,ot:5,hp:true}")
C = (47.0712, 15.4390)
def ll(n, e): return (round(C[0] + n / 111320, 6), round(C[1] + e / 75800, 6))
POS = {'u1': ll(250, -150), 'u5': ll(-320, 210), 'u2': ll(80, -120), 'u3': ll(230, 250), 'u4': ll(-190, -260), 'u6': ll(-250, 140)}
PL = [('u1', 'Anna', 'hunter', 0), ('u5', 'Ben', 'hunter', 8), ('u2', 'Lena', 'hider', 1), ('u3', 'Max', 'hider', 2), ('u4', 'Tom', 'hider', 3), ('u6', 'Sara', 'hider', 9)]

def game_js(status='running', el=0.0, players=None, extra=''):
    """el = Sekunden seit Ende des Vorsprungs (negativ = Vorsprung läuft)."""
    players = players or [p[0] for p in PL]
    pj = ','.join(f"{u}:{{name:'{n}',role:'{r}',state:'alive',j:{i+1},col:{c},lat:{POS[u][0]},lng:{POS[u][1]},ts:T}}"
                  for i, (u, n, r, c) in enumerate(PL) if u in players)
    return f"""(()=>{{__T['.info']={{connected:true}};notify();const T=Date.now();
      __T.games={{K7QF:{{host:'u1',status:'{status}',rn:1,startAt:T-300000-({el})*1000,c:{{lat:{C[0]},lng:{C[1]}}},s:{S},
      tasks:{{}},players:{{{pj}}}}}}};{extra}}})()"""

def me_js(u):
    return f"(()=>{{uid='{u}';const p=__T.games.K7QF.players['{u}'];pos=p?{{lat:p.lat,lng:p.lng}}:{{lat:{C[0]},lng:{C[1]}}};lastFix=Date.now()}})()"

KEEP = "window.__k=setInterval(()=>{const g=__T.games.K7QF;if(!g)return;const p=g.players||{};for(const u in p)p[u].ts=Date.now();lastFix=Date.now();if(pos&&p[uid]){p[uid].lat=pos.lat;p[uid].lng=pos.lng}notify()},600)"

def walk_js(u, to, secs, me=False):
    """Spieler u in secs Sekunden geradlinig nach to bewegen (bei me auch pos)."""
    return f"""(()=>{{const g=__T.games.K7QF,p=g.players['{u}'],a=[p.lat,p.lng],b=[{to[0]},{to[1]}],t0=Date.now(),D={secs}*1000;
      const iv=setInterval(()=>{{const f=Math.min(1,(Date.now()-t0)/D),e=f<.5?2*f*f:1-Math.pow(-2*f+2,2)/2;p.lat=a[0]+(b[0]-a[0])*e;p.lng=a[1]+(b[1]-a[1])*e;
        {"pos={lat:p.lat,lng:p.lng};lastFix=Date.now();" if me else ""}p.ts=Date.now();notify();if(f>=1)clearInterval(iv)}},120)}})()"""

def retime(sc, kind, n, off):
    """Spielzeit so verschieben, dass Ping Nr. n (kind='ping') bzw. Verkleinerung Nr. n (kind='zone') in off Sekunden kommt."""
    step = "g.s.ping*1000" if kind == 'ping' else "g.s.shrink*60000"
    sc.ev(f"(()=>{{const g=__T.games.K7QF,R0=now()+{off}*1000-{n}*{step};g.startAt=R0-g.s.head*60000;G&&(G.startAt=g.startAt);lastK=pgK(g,now()).k;notify()}})()")
    sc.wait(1.3); sc.ev("$('toast')&&($('toast').innerHTML='')")

def until(sc, t):
    d = t - (time.time() - sc.t_start)
    if d > 0: sc.wait(d)

def view(sc, z=15.25, c=None, ms=3500):
    c = c or C
    sc.ev(f"map.setView([{c[0]},{c[1]}],{z},{{animate:false}})"); sc.wait(ms / 1000)

def settle(sc, ms=1800):
    sc.wait(ms / 1000); sc.ev("typeof bfClose==='function'&&$('bfd')&&bfClose()"); sc.ev(KEEP)

# ---------------------------------------------------------------- Szenen
def s01():
    c, end = cues(1)
    with scene('s01', OUT) as sc:
        sc.ev("map.setView([47.0712,15.4390],14,{animate:false})"); sc.wait(3.5)
        sc.start()
        until(sc, c[1] - 0.4); sc.typ('#nm', 'Anna', 0.13)
        until(sc, end + 1.0); sc.stop()

def s02a():   # Anna erstellt das Spiel → Lobby
    c, end = cues(2)
    with scene('s02a', OUT) as sc:
        sc.ev("map.setView([47.0712,15.4390],14,{animate:false})"); sc.wait(3.5)
        sc.ev("$('nm').value='Anna'")
        sc.start(); sc.wait(0.6)
        sc.tap(text='Spiel erstellen', click=False); sc.wait(0.3)
        sc.ev(game_js('lobby', -300, ['u1'])); sc.ev(me_js('u1')); sc.ev("join('K7QF')"); settle(sc, 1500)
        sc.ev("$('panel').classList.remove('m','c')")
        until(sc, c[1] - 0.2); sc.stop()

def s02b():   # Lena öffnet den Einladungslink
    c, end = cues(2)
    with scene('s02b', OUT, url='index.html?c=K7QF') as sc:
        sc.ev(game_js('lobby', -300, ['u1'])); sc.ev(me_js('u2'))
        sc.ev("map.setView([47.0712,15.4390],14,{animate:false})"); sc.wait(3.5)
        sc.start(); sc.wait(0.4)
        sc.typ('#nm', 'Lena', 0.12); sc.wait(0.3)
        sc.ev("__T.games.K7QF.players.u2={name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:%s,lng:%s,ts:Date.now()}" % POS['u2'])
        sc.tap(text='beitreten', click=False); sc.ev("join('K7QF')"); settle(sc, 1200)
        sc.ev("$('panel').classList.remove('m','c')")
        sc.wait(max(1.6, end - c[1] - 2.6)); sc.stop()

def s03():    # Lobby füllt sich, Anna startet
    c, end = cues(3)
    with scene('s03', OUT) as sc:
        sc.ev(game_js('lobby', -300, ['u1', 'u2'])); sc.ev(me_js('u1')); sc.ev("join('K7QF')"); settle(sc, 1500)
        sc.ev("$('panel').classList.remove('m','c')"); sc.wait(3)
        sc.start()
        for i, u in enumerate(['u5', 'u3', 'u4', 'u6']):
            sc.wait(0.55)
            uu = [p for p in PL if p[0] == u][0]
            sc.ev("__T.games.K7QF.players.%s={name:'%s',role:'%s',state:'alive',j:%d,col:%d,lat:%s,lng:%s,ts:Date.now()};notify()" % (u, uu[1], uu[2], 3 + i, uu[3], POS[u][0], POS[u][1]))
        until(sc, c[1] + 1.6)
        sc.ev("$('ps').scrollTop=9999"); sc.wait(0.8)
        sc.tap(text='Spiel starten', click=False)
        until(sc, end + 0.6); sc.stop()

def s04():    # Briefing bei Lena, Vorsprung läuft
    c, end = cues(4)
    with scene('s04', OUT) as sc:
        sc.ev(game_js('running', -292)); sc.ev(me_js('u2')); sc.ev("join('K7QF')"); sc.wait(1.6); sc.ev(KEEP)
        view(sc, 15.0)
        sc.ev("if(!$('bfd'))bfShow(1)"); sc.wait(1.0)
        sc.start()
        until(sc, c[1] + 0.3); sc.tap(text='Verstanden')
        until(sc, end + 1.2); sc.stop()

def s05():    # Zone schrumpft, Lena geht hinaus
    c, end = cues(5)
    # 25 Min nach Vorsprung; nächste Verkleinerung 1,6 s nach Start der Aufnahme
    el = 6 * 240 - 6.2
    with scene('s05', OUT) as sc:
        sc.ev(game_js('running', el)); sc.ev(me_js('u2')); sc.ev("join('K7QF')"); settle(sc)
        sc.ev("ping={k:pgK(G,now()).k,t:now()-90000,pts:{}};"); view(sc, 15.35, (47.0722, 15.4390))
        sc.ev("$('panel').classList.add('c')"); sc.wait(0.6)
        retime(sc, 'zone', 7, c[1] + 0.4); sc.wait(0.3); sc.ev("ping=null;draw()")
        sc.start()
        until(sc, c[2] - 0.3)
        sc.ev(walk_js('u2', ll(640, -60), 3.0, me=True))
        until(sc, end + 1.4); sc.stop()

def s06():    # Ping beim Hunter
    c, end = cues(6)
    el = 8 * 180 - (c[0] + 1.2) - 6.0
    with scene('s06', OUT) as sc:
        sc.ev(game_js('running', el)); sc.ev(me_js('u1')); sc.ev("join('K7QF')"); settle(sc)
        view(sc, 15.25)
        sc.ev("$('panel').classList.add('c')"); sc.wait(0.5)
        retime(sc, 'ping', 9, c[0] + 2.2); sc.wait(0.3); sc.ev("ping=null;draw()")
        sc.start()
        until(sc, c[2])
        for u, to in [('u2', ll(10, 60)), ('u3', ll(140, 330)), ('u4', ll(-110, -340)), ('u6', ll(-300, 40))]:
            sc.ev(walk_js(u, to, 4))
        until(sc, end + 1.2); sc.stop()

def s06b():   # Lena bekommt den Ping
    with scene('s06b', OUT) as sc:
        el = 8 * 180 - 1.6 - 6.0
        sc.ev(game_js('running', el)); sc.ev(me_js('u2')); sc.ev("join('K7QF')"); settle(sc)
        view(sc, 15.25)
        sc.ev("$('panel').classList.add('c')"); sc.wait(0.5)
        retime(sc, 'ping', 9, 1.2); sc.wait(0.3); sc.ev("ping=null;draw()")
        sc.start(); sc.wait(3.6); sc.stop()

def s07():    # Safehouse
    c, end = cues(7)
    sh = ll(-40, 300)
    with scene('s07', OUT) as sc:
        sc.ev(game_js('running', 9 * 180 + 20, extra=f"__T.games.K7QF.players.u2.lat={ll(60,170)[0]};__T.games.K7QF.players.u2.lng={ll(60,170)[1]};"))
        sc.ev(me_js('u2')); sc.ev("join('K7QF')"); settle(sc)
        view(sc, 16.1, ll(20, 230))
        sc.start(); sc.wait(0.5)
        sc.ev(f"__T.games.K7QF.tasks.sh={{t0:now()-500,loc:{{lat:{sh[0]},lng:{sh[1]}}}}};notify()")
        until(sc, c[1] - 0.6)
        sc.ev(walk_js('u2', ll(-34, 296), 3.2, me=True))
        until(sc, c[2] + 0.2)
        sc.tap(text='Einchecken'); sc.wait(1.0)
        until(sc, c[3] - 0.6)
        sc.tap(sel='#pb button.gb:has-text("Immunität")'); sc.wait(0.7)
        sc.tap(sel='#gd button:has-text("einsetzen")'); sc.wait(0.5)
        sc.ev("$('panel').classList.add('c')")
        until(sc, end + 1.4); sc.stop()

def s08a():   # Anna meldet den Fang an Tom
    c, end = cues(8)
    with scene('s08a', OUT) as sc:
        sc.ev(game_js('running', 10 * 180, extra=f"__T.games.K7QF.players.u1.lat={ll(-185,-262)[0]};__T.games.K7QF.players.u1.lng={ll(-185,-262)[1]};"))
        sc.ev(me_js('u1')); sc.ev("join('K7QF')"); settle(sc)
        view(sc, 16.3, ll(-180, -250))
        sc.start(); sc.wait(0.9)
        sc.tap(text='Fang melden'); sc.wait(1.0)
        sc.tap(sel='button.cgt:has-text("Tom")'); sc.wait(1.6)
        sc.stop()

def s08b():   # Tom bestätigt
    with scene('s08b', OUT) as sc:
        sc.ev(game_js('running', 10 * 180, extra=f"__T.games.K7QF.players.u1.lat={ll(-186,-263)[0]};__T.games.K7QF.players.u1.lng={ll(-186,-263)[1]};")); sc.ev(me_js('u4')); sc.ev("join('K7QF')"); settle(sc)
        view(sc, 16.3, ll(-180, -250))
        sc.start(); sc.wait(0.3)
        sc.ev("(()=>{const p=__T.games.K7QF.players.u1;__T.games.K7QF.catches={u4:{hunter:'u1',t:now(),status:'pending',lat:p.lat,lng:p.lng}};notify()})()"); sc.wait(1.6)
        sc.tap(sel='#fa button:has-text("Ja")'); sc.wait(1.6)
        sc.stop()

def s08c():   # Handschellen auf Annas Karte
    with scene('s08c', OUT) as sc:
        sc.ev(game_js('running', 10 * 180, extra=f"__T.games.K7QF.players.u4.state='caught';__T.games.K7QF.catches={{u4:{{hunter:'u1',t:T-2000,status:'done',lat:{POS['u4'][0]},lng:{POS['u4'][1]}}}}};"))
        sc.ev(me_js('u1')); sc.ev("join('K7QF')"); settle(sc)
        view(sc, 16.3, ll(-180, -250))
        sc.ev("$('panel').classList.add('c')"); sc.wait(0.5)
        sc.start(); sc.wait(2.6); sc.stop()

def s09():    # Bonus: Extra-Ping, Lena immun
    c, end = cues(9)
    with scene('s09', OUT) as sc:
        sc.ev(game_js('running', 10 * 180 + 50, extra=f"__T.games.K7QF.players.u4.state='caught';__T.games.K7QF.players.u2.immUntil=T+120000;__T.games.K7QF.catches={{u4:{{hunter:'u1',t:T-100000,status:'done',lat:{POS['u4'][0]},lng:{POS['u4'][1]}}}}};"))
        sc.ev(me_js('u1')); sc.ev("join('K7QF')"); settle(sc)
        view(sc, 15.25)
        sc.start(); sc.wait(0.6)
        sc.tap(sel='#pb button:has-text("Neuer Bonus")'); sc.wait(1.0)
        until(sc, c[1] - 0.2)
        sc.tap(sel='#gd button.gopt:has-text("Extra-Ping")'); sc.wait(1.0)
        sc.ev("gdClose&&gdClose()"); sc.wait(0.4)
        sc.tap(sel='#pb button.gb:has-text("Extra-Ping")'); sc.wait(0.8)
        sc.tap(sel='#gd button:has-text("einsetzen")'); sc.wait(0.6)
        sc.ev("$('panel').classList.add('c')")
        until(sc, end + 1.4); sc.stop()

def s10():    # Ergebnis
    c, end = cues(10)
    with scene('s10', OUT) as sc:
        sc.ev(game_js('running', 55 * 60, extra=f"__T.games.K7QF.players.u4.state='caught';__T.games.K7QF.catches={{u4:{{hunter:'u1',t:T-1500000,status:'done',lat:{POS['u4'][0]},lng:{POS['u4'][1]}}}}};"))
        sc.ev(me_js('u2')); sc.ev("join('K7QF')"); settle(sc)
        view(sc, 15.0)
        sc.start(); sc.wait(0.5)
        sc.ev("__T.games.K7QF.status='over';__T.games.K7QF.winner='hider';__T.games.K7QF.end=now();notify()")
        until(sc, end + 1.6); sc.stop()

ALL = ['s01', 's02a', 's02b', 's03', 's04', 's05', 's06', 's06b', 's07', 's08a', 's08b', 's08c', 's09', 's10']
if __name__ == '__main__':
    for n in (sys.argv[2:] or ALL):
        t = time.time(); globals()[n](); print(n, 'ok', round(time.time() - t, 1), 's', flush=True)
