"""Mockups für KONZEPT_Log („Lagebericht“): drei Gestaltungen, jeweils Reiter „Verlauf“ und „Lage“.
Aufruf: python3 dev/demo/mock_log.py [ausgabeordner]  → Log_Mockup_A/B/C.png
Echte App (laufendes Kopfgeld-Spiel, Hunter-Sicht) + eingeblendetes Fenster aus App-Tokens/Klassen.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app, shot, OUT
from PIL import Image, ImageDraw, ImageFont

GAME = """(()=>{const T=Date.now();__T['.info']={connected:true};const pl={
 u0:{name:'Manuel',role:'hunter',tm:1,tj:1,state:'alive',j:1,col:0,lat:47.0738,lng:15.4462,ts:T},u1:{name:'Sophie',role:'hunter',tm:1,tj:2,state:'alive',j:2,col:0,lat:47.0745,lng:15.4440,ts:T},
 u2:{name:'Tobias',role:'hunter',tm:2,tj:3,state:'alive',j:3,col:0,lat:47.072,lng:15.447,ts:T},u4:{name:'Lena',role:'hider',state:'alive',j:5,col:6,lat:47.0730,lng:15.448,ts:T},
 u5:{name:'Nora',role:'hider',state:'alive',j:6,col:7,lat:47.0722,lng:15.444,ts:T}};
 __T.games={MOCK:{host:'u0',status:'running',startAt:T-17*6e4,c:{lat:47.0738,lng:15.4462},s:Object.assign({},DEF,preOf(30),{mode:'bounty',tN:3,head:0}),players:pl,
  teams:{1:{name:'Die Füchse',col:10},2:{name:'Schattenkartell',col:11},3:{name:'Agentur Nord',col:0}}}};notify();uid='u0';pos={lat:47.0738,lng:15.4462};lastFix=T})()"""

# Verlauf: [Zeit, Symbol, Farbe, Text, Zusatz, antippbar]
V = [['16:52','ping','#9ca1a8','Ping','5 Hider-Positionen',1],
     ['16:20','catch','#e5484d','Sophie fängt Felix','Die Füchse · Fangort',1],
     ['15:05','extra','#4fb3f0','Sophie setzt Extra-Ping ein','Die Füchse',1],
     ['14:40','zone','#9ca1a8','Zone schrumpft auf 420 m','',0],
     ['14:00','ping','#9ca1a8','Ping','5 Hider-Positionen',1],
     ['12:10','catch','#e5484d','Jakob wurde gefangen','Schattenkartell · Fangort',1],
     ['11:30','knapp','#ff8a1f','Lena außerhalb der Zone – sichtbar','×2',0],
     ['10:00','hack','#7c6cff','Mira hackt das System','Terminal',1],
     ['08:00','ping','#9ca1a8','Ping','5 Hider-Positionen',1],
     ['04:00','zone','#9ca1a8','Headstart vorbei – die Jagd beginnt','',0]]
TEAMS = [['Die Füchse', 10, 2, '16:20', 1], ['Schattenkartell', 11, 1, '12:10', 0], ['Agentur Nord', 0, 0, '–', 0]]
HIDER = [['Lena', 6, 'frei', ''], ['Mira', 1, 'frei', ''], ['Nora', 7, 'frei', ''], ['Felix', 3, 'gefangen', 'Sophie · 16:20'], ['Jakob', 8, 'gefangen', 'Tobias · 12:10']]
STAT = [['Restzeit', '13:08'], ['Zone', '420 m'], ['Verkleinerung', 'in 1:20'], ['Ping', 'in 0:48']]
LIST = '<svg class=ic viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M8 6h12M8 12h12M8 18h12"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/></svg>'

BASE_CSS = """
.lgX{position:fixed;z-index:3000;color:var(--fg);font-family:var(--f-b)}
.lgX .tri{display:inline-block;width:12px;height:11px;flex:none}
.lgX .ci{display:inline-block;width:11px;height:11px;border-radius:50%;flex:none}
.hbtn{position:fixed;z-index:1300;display:grid;place-items:center;background:color-mix(in srgb,var(--panel) 92%,transparent);color:var(--fg);border-radius:50%;width:40px;height:40px}
.hbtn .ic{width:19px;height:19px}.hbtn i{position:absolute;top:6px;right:6px;width:9px;height:9px;border-radius:50%;background:var(--ac);box-shadow:0 0 0 2px var(--panel)}
#toast{display:none!important}
"""

A_CSS = """
.lgA{left:0;right:0;bottom:0;top:120px;background:var(--panel);border-radius:18px 18px 0 0;box-shadow:0 -8px 30px #0008;padding:10px 16px 0;display:flex;flex-direction:column}
.lgA .gr{width:38px;height:4px;border-radius:2px;background:var(--line);margin:0 auto 10px}
.lgA h2{margin:0;font-size:22px}.lgA .sub{color:var(--mut);font-size:12.5px;margin-top:2px}
.lgA .tb{display:flex;gap:22px;border-bottom:1px solid var(--line);margin:12px 0 4px}.lgA .tb span{padding:8px 0;font-weight:600;color:var(--mut)}.lgA .tb span.on{color:var(--fg);box-shadow:inset 0 -2px 0 var(--fg)}
.lgA .r{display:grid;grid-template-columns:42px 30px 1fr 14px;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid var(--line2)}
.lgA .r .t{color:var(--mut);font-size:12.5px;font-variant-numeric:tabular-nums}.lgA .r .o{width:28px;height:28px;border-radius:50%;display:grid;place-items:center;border:1.5px solid var(--c);color:var(--c)}.lgA .r .o .ic{width:14px;height:14px}
.lgA .r b{font-weight:600;font-size:14px;display:block}.lgA .r small{color:var(--mut);font-size:12px}.lgA .r .ch{color:var(--mut)}.lgA .r .ch .ic{width:14px;height:14px}
.lgA .st{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0 14px}.lgA .st div{background:var(--panel2);border-radius:10px;padding:9px 12px}.lgA .st small{color:var(--mut);font-size:11.5px;display:block}.lgA .st b{font-size:19px;font-family:var(--f-d)}
.lgA h4{margin:6px 0 4px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut)}
.lgA .pr{display:flex;align-items:center;gap:10px;padding:9px 10px;border-radius:10px}.lgA .pr.me{background:var(--panel2)}.lgA .pr .n{flex:1;font-weight:600}.lgA .pr .v{font:700 18px var(--f-d)}.lgA .pr small{color:var(--mut);font-size:12px;margin-left:4px}
.lgA .chip{font-size:11.5px;font-weight:600;padding:2px 8px;border-radius:999px;border:1px solid var(--line);color:var(--mut)}.lgA .chip.f{color:#3ecf8e;border-color:#3ecf8e66}.lgA .chip.g{color:#e5484d;border-color:#e5484d66}
"""

B_CSS = """
.lgB{inset:0;background:var(--bg);padding:calc(14px + env(safe-area-inset-top,0px)) 18px 0;overflow:hidden}
.lgB .hd{display:flex;align-items:flex-start;justify-content:space-between}.lgB .k{font:600 11px var(--f-b);letter-spacing:.14em;color:var(--ac);text-transform:uppercase}
.lgB h2{margin:2px 0 0;font-size:26px;line-height:1.1}.lgB .x{width:36px;height:36px;border-radius:50%;background:var(--panel2);display:grid;place-items:center;font-size:18px;color:var(--mut)}
.lgB .sg{display:flex;background:var(--panel);border-radius:12px;padding:4px;margin:14px 0 10px}.lgB .sg span{flex:1;text-align:center;padding:8px;border-radius:9px;font-weight:600;color:var(--mut)}.lgB .sg span.on{background:var(--panel2);color:var(--fg);box-shadow:inset 0 0 0 1px var(--line)}
.lgB .grp{font:600 11px var(--f-b);letter-spacing:.08em;color:var(--mut);text-transform:uppercase;margin:12px 0 6px 34px}
.lgB .tl{position:relative}.lgB .tl:before{content:"";position:absolute;left:12px;top:6px;bottom:0;width:2px;background:var(--line)}
.lgB .e{position:relative;display:grid;grid-template-columns:26px 1fr auto;gap:8px;align-items:start;padding:6px 0}
.lgB .e .nd{width:26px;height:26px;border-radius:50%;background:var(--bg);border:2px solid var(--c);color:var(--c);display:grid;place-items:center;z-index:1}.lgB .e .nd .ic{width:13px;height:13px}
.lgB .e b{display:block;font-weight:600;font-size:14.5px;line-height:1.3}.lgB .e small{color:var(--mut);font-size:12px}.lgB .e .t{font:600 13px var(--f-d);color:var(--mut);padding-top:4px}
.lgB .e.tap b:after{content:" ›";color:var(--mut)}
.lgB .big{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:4px 0 16px;text-align:center}.lgB .big b{display:block;font:700 22px var(--f-d)}.lgB .big small{color:var(--mut);font-size:11px}
.lgB .bar{height:8px;border-radius:4px;background:var(--panel2);overflow:hidden;margin:6px 0 2px}.lgB .bar i{display:block;height:100%;background:#3ecf8e}
.lgB .sec{font:600 11px var(--f-b);letter-spacing:.08em;color:var(--mut);text-transform:uppercase;margin:18px 0 8px}
.lgB .tr{display:grid;grid-template-columns:14px 1fr auto;gap:10px;align-items:center;margin:8px 0}.lgB .tr .bb{grid-column:2/4;height:6px;border-radius:3px;background:var(--panel2);margin-top:-4px}.lgB .tr .bb i{display:block;height:100%;border-radius:3px}
.lgB .tr .n{font-weight:600}.lgB .tr .v{font:700 16px var(--f-d)}.lgB .tr.me .n:after{content:"  · ihr";color:var(--mut);font-weight:400}
.lgB .hg{display:grid;grid-template-columns:1fr 1fr;gap:8px}.lgB .hc{background:var(--panel);border-radius:12px;padding:10px 12px;display:flex;gap:8px;align-items:center}.lgB .hc.out{opacity:.55}.lgB .hc b{display:block;font-weight:600}.lgB .hc small{color:var(--mut);font-size:11.5px}
"""

C_CSS = """
.lgC{top:0;bottom:0;right:0;width:86%;background:#1b1e22;box-shadow:-10px 0 30px #0009;padding:calc(14px + env(safe-area-inset-top,0px)) 14px 0;border-left:1px solid var(--line)}
.lgC .hd{display:flex;align-items:center;gap:8px}.lgC .hd b{font-size:17px;flex:1}.lgC .hd .tg{display:flex;background:var(--bg);border-radius:999px;padding:3px}.lgC .hd .tg span{padding:4px 11px;border-radius:999px;font-size:12.5px;font-weight:600;color:var(--mut)}.lgC .hd .tg span.on{background:var(--fg);color:var(--bg)}
.lgC .fl{display:flex;gap:6px;margin:12px 0 8px;overflow:hidden}.lgC .fl span{flex:none;font-size:12px;font-weight:600;padding:4px 10px;border-radius:999px;border:1px solid var(--line);color:var(--mut);display:flex;gap:5px;align-items:center}.lgC .fl span.on{color:var(--fg);border-color:var(--fg)}.lgC .fl .ic{width:12px;height:12px}
.lgC .r{display:flex;align-items:center;gap:8px;padding:7px 4px;border-bottom:1px solid var(--line2);font-size:13px}.lgC .r .t{width:36px;color:var(--mut);font-size:11.5px;font-variant-numeric:tabular-nums;flex:none}
.lgC .r .ic{width:14px;height:14px;color:var(--c);flex:none}.lgC .r .x{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lgC .r .x small{color:var(--mut)}
.lgC .r.tap{background:linear-gradient(90deg,transparent,transparent)}.lgC .r .go{font-size:11px;color:var(--mut);border:1px solid var(--line);border-radius:6px;padding:1px 6px;flex:none}
.lgC .sb{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:12px 0}.lgC .sb div{padding:8px 10px;border-bottom:1px solid var(--line);border-right:1px solid var(--line)}.lgC .sb div:nth-child(2n){border-right:0}.lgC .sb div:nth-last-child(-n+2){border-bottom:0}
.lgC .sb small{display:block;color:var(--mut);font-size:11px}.lgC .sb b{font:700 17px var(--f-d)}
.lgC h4{margin:12px 0 4px;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);display:flex;justify-content:space-between}
.lgC .q{display:flex;align-items:center;gap:8px;padding:6px 2px;font-size:13.5px}.lgC .q .n{flex:1}.lgC .q .v{font:700 15px var(--f-d)}.lgC .q small{color:var(--mut);font-size:11.5px}.lgC .q.me{font-weight:700}.lgC .q.out .n{color:var(--mut);text-decoration:line-through}
"""

JS = r"""(d)=>{const P=d.pal,tri=c=>`<svg class=tri viewBox="0 0 12 11"><path d="M6 1.2L11 10H1Z" fill="${c}" stroke="#fff" stroke-width=".9" stroke-linejoin=round /></svg>`,
 ci=c=>`<span class=ci style="background:${c};box-shadow:0 0 0 1px #fff8"></span>`,I=n=>ic(n==='hack'?'hack':n==='zone'?'zone':n);
 document.head.insertAdjacentHTML('beforeend','<style>'+d.css+'</style>');
 const btn=document.createElement('div');btn.className='hbtn';btn.innerHTML=d.list+(d.dot?'<i></i>':'');Object.assign(btn.style,d.bpos);if(d.bpill){btn.style.borderRadius='999px';btn.style.width='auto';btn.style.padding='0 12px';btn.style.gridAutoFlow='column';btn.style.gap='6px';btn.innerHTML=d.list+'<span style="font-weight:600;font-size:13px">Log</span>'+(d.dot?'<i style="top:4px;right:4px"></i>':'')}
 document.body.appendChild(btn);
 const w=document.createElement('div');w.className='lgX lg'+d.k;let h='';
 const V=d.V,T=d.T,X=d.X,S=d.S;
 if(d.k==='A'){h=`<div class=gr></div><h2>Lagebericht</h2><div class=sub>Operation Schwarzer Bote · Die Füchse</div><div class=tb><span class="${d.tab==='v'?'on':''}">Verlauf</span><span class="${d.tab==='l'?'on':''}">Lage</span></div>`;
  if(d.tab==='v')h+=V.map(r=>`<div class=r style="--c:${r[2]}"><span class=t>${r[0]}</span><span class=o>${I(r[1])}</span><span><b>${r[3]}</b>${r[4]?`<small>${r[4]}</small>`:''}</span><span class=ch>${r[5]?ic('chev'):''}</span></div>`).join('');
  else h+=`<div class=st>${S.map(s=>`<div><small>${s[0]}</small><b>${s[1]}</b></div>`).join('')}</div><h4>Agenturen</h4>`+T.map(t=>`<div class="pr ${t[4]?'me':''}">${tri(P[t[1]])}<span class=n>${t[0]}</span><small>letzter ${t[3]}</small><span class=v>${t[2]}</span></div>`).join('')
   +`<h4 style="margin-top:14px">Hider · 3 von 5 frei</h4>`+X.map(x=>`<div class=pr>${ci(P[x[1]])}<span class=n>${x[0]}</span>${x[3]?`<small>${x[3]}</small>`:''}<span class="chip ${x[2]==='frei'?'f':'g'}">${x[2]}</span></div>`).join('')}
 if(d.k==='B'){h=`<div class=hd><div><div class=k>Lagebericht</div><h2>Operation<br>Schwarzer Bote</h2></div><span class=x>✕</span></div><div class=sg><span class="${d.tab==='v'?'on':''}">Verlauf</span><span class="${d.tab==='l'?'on':''}">Lage</span></div>`;
  if(d.tab==='v'){const g=[['Minute 15 – 17',V.slice(0,3)],['Minute 10 – 15',V.slice(3,8)],['Minute 0 – 10',V.slice(8)]];
   h+=g.map(([n,a])=>`<div class=grp>${n}</div><div class=tl>${a.map(r=>`<div class="e ${r[5]?'tap':''}" style="--c:${r[2]}"><span class=nd>${I(r[1])}</span><span><b>${r[3]}</b>${r[4]?`<small>${r[4]}</small>`:''}</span><span class=t>${r[0]}</span></div>`).join('')}</div>`).join('')}
  else{h+=`<div class=big>${S.map(s=>`<div><b>${s[1].replace('in ','')}</b><small>${s[0]}</small></div>`).join('')}</div>
   <div style="display:flex;justify-content:space-between"><b>Hider frei</b><b style="font-family:var(--f-d)">3 / 5</b></div><div class=bar><i style="width:60%"></i></div>
   <div class=sec>Agenturen</div>`+T.map(t=>`<div class="tr ${t[4]?'me':''}">${tri(P[t[1]])}<span class=n>${t[0]}</span><span class=v>${t[2]}</span><span class=bb><i style="width:${t[2]*45+4}%;background:${P[t[1]]}"></i></span></div>`).join('')
   +`<div class=sec>Gejagt</div><div class=hg>`+X.map(x=>`<div class="hc ${x[2]!=='frei'?'out':''}">${x[2]==='frei'?ci(P[x[1]]):`<span style="color:#e5484d">${ic('catch')}</span>`}<span><b>${x[0]}</b><small>${x[2]==='frei'?'frei':x[3]}</small></span></div>`).join('')+`</div>`}}
 if(d.k==='C'){h=`<div class=hd><b>Log</b><span class=tg><span class="${d.tab==='v'?'on':''}">Verlauf</span><span class="${d.tab==='l'?'on':''}">Lage</span></span></div>`;
  if(d.tab==='v')h+=`<div class=fl><span class=on>Alle</span><span>${ic('catch')}Fang</span><span>${ic('ping')}Ping</span><span>${ic('extra')}Boni</span><span>${ic('box')}Aufgaben</span></div>`
   +V.map(r=>`<div class="r ${r[5]?'tap':''}" style="--c:${r[2]}"><span class=t>${r[0]}</span>${I(r[1])}<span class=x>${r[3]}${r[4]?` <small>· ${r[4]}</small>`:''}</span>${r[5]?`<span class=go>${r[1]==='ping'?'Karte':'zeigen'}</span>`:''}</div>`).join('');
  else h+=`<div class=sb>${S.map(s=>`<div><small>${s[0]}</small><b>${s[1]}</b></div>`).join('')}</div><h4><span>Agenturen</span><span>Fänge</span></h4>`
   +T.map(t=>`<div class="q ${t[4]?'me':''}">${tri(P[t[1]])}<span class=n>${t[0]}</span><small>${t[3]}</small><span class=v>${t[2]}</span></div>`).join('')
   +`<h4><span>Hider</span><span>3 / 5 frei</span></h4>`+X.map(x=>`<div class="q ${x[2]!=='frei'?'out':''}">${ci(P[x[1]])}<span class=n>${x[0]}</span><small>${x[2]==='frei'?'frei':x[3]}</small></div>`).join('')}
 w.innerHTML=h;document.body.appendChild(w)}"""

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(out, exist_ok=True)
    CFG = {'A': (A_CSS, {'left': '10px', 'top': 'calc(108px + env(safe-area-inset-top,0px))'}, False, 'Fenster von unten'),
           'B': (B_CSS, {'left': '50%', 'transform': 'translateX(-50%)', 'top': 'calc(60px + env(safe-area-inset-top,0px))'}, True, 'Vollbild-Akte'),
           'C': (C_CSS, {'right': '10px', 'top': 'calc(156px + env(safe-area-inset-top,0px))'}, False, 'Seitenleiste')}
    for k, (css, bpos, pill, title) in CFG.items():
        imgs = []
        for tab in ('knopf', 'v', 'l'):
            with app(width=412, height=915) as (pg, ev, errs):
                ev(GAME); ev("join('MOCK')"); pg.wait_for_timeout(1500); ev("bfClose&&bfClose()"); pg.wait_for_timeout(200)
                pal = ev('PAL')
                pg.evaluate(JS if tab != 'knopf' else JS.replace("w.innerHTML=h;document.body.appendChild(w)", ""),
                            {'k': k, 'tab': tab, 'css': BASE_CSS + css, 'list': LIST, 'dot': True, 'bpos': bpos, 'bpill': pill, 'pal': pal, 'V': V, 'T': TEAMS, 'X': HIDER, 'S': STAT})
                pg.wait_for_timeout(250); fn = 'log_%s_%s.png' % (k, tab); shot(pg, fn); imgs.append(os.path.join(OUT, fn))
                if errs: print(k, tab, errs[:3])
        ims = [Image.open(p) for p in imgs]
        W = Image.new('RGB', (412 * 3 + 48, 915 + 50), '#15171a'); d = ImageDraw.Draw(W)
        try: fn = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
        except Exception: fn = None
        for i, (im, lab) in enumerate(zip(ims, ['HUD-Knopf (Punkt = neu)', 'Verlauf', 'Lage'])):
            W.paste(im, (i * 436, 50)); d.text((i * 436 + 6, 14), lab, fill='#e4e2dd', font=fn)
        p = os.path.join(out, 'Log_Mockup_%s.png' % k); W.save(p); print(p, title)
