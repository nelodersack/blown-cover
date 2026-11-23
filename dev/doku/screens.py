# Screenshots und Kartensymbole für die Spielregeln (dev/doku/anleitung.py).
# Aufruf: DSF=3 python3 dev/doku/screens.py [zielordner]
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screens')
os.makedirs(OUT, exist_ok=True)

S = "{r0:500,rMin:200,shrink:4,step:55,head:5,dur:60,ping:180,pen:2,mode:'survive',taskR:0,imm:180,shOn:true,shT:20,evT:8,ddN:1,ddT:8,mtN:1,mtT:15,bon:true,hbOn:true,hbN:2,hbC:90,hbL:70,hbT:30,gw:20,gd:60,ot:5}"

def game(ev, me, el=900, extra=''):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now();
      __T.games={K7QF:{host:'u1',status:'running',rn:1,startAt:T-300000-%d*1000,c:{lat:47.07,lng:15.44},s:%s,
      tasks:{d1:{t0:T-60000,a:'u2',b:'u4',loc:{lat:47.0688,lng:15.4372}},m1:{t0:T-60000,a:'u2',b:'u3',loc:{lat:47.0724,lng:15.4428}},
        sh:{t0:T-60000,loc:{lat:47.0679,lng:15.4425}}},
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0719,lng:15.4386,ts:T},u5:{name:'Ben',role:'hunter',state:'alive',j:5,col:8,lat:47.0668,lng:15.4352,ts:T},
        u2:{name:'Lena',role:'hider',state:'alive',j:2,col:1,lat:47.0702,lng:15.4402,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0712,lng:15.4418,ts:T},
        u4:{name:'Tom',role:'hider',state:'alive',j:4,col:3,lat:47.0684,lng:15.4385,ts:T},u6:{name:'Sara',role:'hider',state:'alive',j:6,col:9,lat:47.0688,lng:15.4420,ts:T}},
      cols:{0:'u1',1:'u2',2:'u3',3:'u4',8:'u5',9:'u6'}}};%s
      uid='%s';pos={lat:__T.games.K7QF.players['%s'].lat,lng:__T.games.K7QF.players['%s'].lng};lastFix=Date.now()})()""" % (el, S, extra, me, me, me))
    ev("join('K7QF')")

def settle(ev, pg):
    pg.wait_for_timeout(1300); ev("typeof bfClose==='function'&&bfClose()")
    ev("window.__k=setInterval(()=>{const p=(__T.games.K7QF||{}).players||{};for(const u in p)p[u].ts=Date.now();lastFix=Date.now()},700)")
    pg.wait_for_timeout(500)

def view(ev, pg, z=15.6):
    ev(f"map.setView([47.0700,15.4400],{z},{{animate:false}})"); pg.wait_for_timeout(4000 if os.environ.get('MAP') else 500)

def shot(pg, n):
    pg.screenshot(path=os.path.join(OUT, n + '.png'))

PINGS = "{u2:{lat:47.0709,lng:15.4390,name:'Lena'},u3:{lat:47.0718,lng:15.4425,name:'Max'},u4:{lat:47.0681,lng:15.4377,name:'Tom'},u6:{lat:47.0683,lng:15.4428,name:'Sara'}}"

# 1 Hunter: Karte nach einem Ping
with app(390, 844) as (pg, ev, errs):
    game(ev, 'u1'); settle(ev, pg)
    ev(f"lastK=pgK(G,now()).k;ping={{k:lastK,t:now()-35000,pts:{PINGS},grey:{{}}}};draw()"); view(ev, pg)
    ev("$('panel').classList.add('c')"); pg.wait_for_timeout(500)
    shot(pg, 'hunter_ping')
    ev("$('panel').classList.remove('c')"); pg.wait_for_timeout(400)
    shot(pg, 'hunter_panel')
    ev("lgToggle()"); pg.wait_for_timeout(400); shot(pg, 'hunter_legende'); ev("lgToggle()")
    # Fang melden
    ev("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Fang melden').click()"); pg.wait_for_timeout(500)
    shot(pg, 'fang_melden')
    print('hunter', errs[:3])

# 2 Hunter: neuer Bonus nach Fang
with app(390, 844) as (pg, ev, errs):
    game(ev, 'u1', extra="__T.games.K7QF.players.u6.state='caught';__T.games.K7QF.players.u6.sT=T-200000;__T.games.K7QF.catches={u6:{hunter:'u1',t:T-200000,status:'done',lat:47.0688,lng:15.4420}};")
    settle(ev, pg); view(ev, pg)
    b = ev("[...document.querySelectorAll('#pb button')].map(b=>b.innerText.replace(/\\n/g,' '))"); print(b)
    ev("[...document.querySelectorAll('#pb button')].find(b=>/Neuer Bonus/.test(b.innerText)).click()"); pg.wait_for_timeout(500)
    shot(pg, 'hunter_bonus')
    print('bonus', errs[:3])

# 3 Hider: Karte mit eigenem Ping, Mitspielern und Aufgaben
with app(390, 844) as (pg, ev, errs):
    game(ev, 'u2'); settle(ev, pg)
    ev(f"ping={{k:pgK(G,now()).k,t:now()-35000,pts:{PINGS}}};draw()"); view(ev, pg)
    ev("$('panel').classList.add('c')"); pg.wait_for_timeout(500)
    shot(pg, 'hider_karte')
    ev("$('panel').classList.remove('c')"); pg.wait_for_timeout(500)
    shot(pg, 'hider_panel')
    ev("$('ps').scrollTop=600"); pg.wait_for_timeout(300); shot(pg, 'hider_panel_unten')
    print('hider', errs[:3])

# 4 Hider außerhalb der Zone
with app(390, 844) as (pg, ev, errs):
    game(ev, 'u2', extra="__T.games.K7QF.players.u2.lat=47.07345;__T.games.K7QF.players.u2.lng=15.4418;")
    settle(ev, pg); pg.wait_for_timeout(2500)
    ev("map.setView([47.0712,15.4405],15.6,{animate:false})"); pg.wait_for_timeout(4000 if os.environ.get('MAP') else 500)
    ev("$('panel').classList.add('c')"); pg.wait_for_timeout(500)
    shot(pg, 'hider_draussen')
    print('draussen', errs[:3])

# 5 Kartensymbole aus dem echten Code
with app(400, 800) as (pg, ev, errs):
    game(ev, 'u1'); settle(ev, pg)
    keys = {'hider': ("hider", "'u2'"), 'hunter': ("hunter", "'u1'"), 'me': ("me", "'u2'"), 'ping': ("ping", "'u3'"),
            'pingme': ("pingme", "'u2'"), 'xping': ("xping", "'u4'"), 'live': ("live", "'u2'"), 'stale': ("stale", "'u4'"),
            'next': ("next", "null"), 'catch': ("catch", "null"), 't-sh': ("t-sh", "null"), 't-dd': ("t-dd", "null"),
            't-mt': ("t-mt", "null"), 't-ev': ("t-ev", "null"), 't-hk': ("t-hk", "null"), 'oz': ("oz", "null"),
            't-ddc': ("t-ddc", "null"), 'inf': ("inf", "null")}
    ev("""(()=>{const w=document.createElement('div');w.id='symw';w.style.cssText='position:fixed;inset:0;z-index:99999;background:transparent;display:flex;flex-wrap:wrap;gap:20px;padding:20px';document.body.appendChild(w)})()""")
    for name, (k, pid) in keys.items():
        live = ' live' if k in ('live',) else ''
        ev(f"""(()=>{{const d=document.createElement('div');d.className='mkw {k}';d.id='sym_{name.replace('-','_')}';d.style.cssText='position:relative;width:36px;height:36px';d.innerHTML=shape('{k}',{pid});$('symw').appendChild(d)}})()""")
    ev("document.querySelectorAll('#symw .mkw').forEach(d=>d.style.animation='none')")
    # Immun = eigener Marker mit goldenem Ring, Zombie = Dreieck mit grünem Punkt
    ev("""(()=>{const d=document.createElement('div');d.className='mkw me';d.id='sym_immun';d.style.cssText='position:relative;width:36px;height:36px';d.innerHTML=shape('me','u2').replace('stroke="#1e7cf0"','stroke="#f2b705"');$('symw').appendChild(d)})()""")
    ev("""(()=>{P().u5.zt=1;const d=document.createElement('div');d.className='mkw hunter';d.id='sym_zombie';d.style.cssText='position:relative;width:36px;height:36px';d.innerHTML=shape('hunter','u5');$('symw').appendChild(d)})()""")
    ev("""(()=>{const d=document.createElement('div');d.id='sym_radar';d.style.cssText='position:relative;width:36px;height:36px';d.innerHTML='<svg class=bmr style="width:36px;height:36px" viewBox="-52 -52 104 104">'+BMSVG+'</svg>';$('symw').appendChild(d)})()""")
    pg.add_style_tag(content="#symw .mkw::after{display:none!important} #map,#panel,#hud,#toast{visibility:hidden} html,body{background:transparent!important}")
    pg.wait_for_timeout(400)
    ids = ev("[...document.querySelectorAll('#symw>div')].map(d=>d.id)")
    for i in ids:
        pg.locator('#' + i).screenshot(path=os.path.join(OUT, i + '.png'), omit_background=True)
    print('symbole', ids, errs[:3])
