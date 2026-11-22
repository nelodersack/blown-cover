"""Mockups: andere Platzierungen für die Lagebericht-Leiste (#blg). Echte App + echte Leiste, nur die Lage per CSS geändert.
Aufruf: python3 dev/demo/mock_log_platz.py [ordner]  → Log_Platz_1/2/3.png (je wenige Einträge | volle Liste)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app, shot, OUT
from PIL import Image, ImageDraw, ImageFont

GAME = """(()=>{const T=Date.now();__T['.info']={connected:true};const pl={
 u0:{name:'Manuel',role:'hunter',tm:1,tj:1,state:'alive',j:1,col:0,lat:47.0738,lng:15.4462,ts:T},u1:{name:'Tobias',role:'hunter',tm:2,tj:2,state:'alive',j:2,col:0,lat:47.0745,lng:15.444,ts:T},
 u2:{name:'Lena',role:'hider',state:'alive',j:3,col:6,lat:47.073,lng:15.448,ts:T},u3:{name:'Felix',role:'hider',state:'caught',sT:T-5*6e4,j:4,col:3,lat:47.0722,lng:15.444,ts:T}};
 __T.games={MOCK:{host:'u0',status:'running',startAt:T-20*6e4,c:{lat:47.0738,lng:15.4462},s:Object.assign({},DEF,preOf(30),{mode:'bounty',tN:2,head:1}),players:pl,
  teams:{1:{name:'Die Füchse',col:10},2:{name:'Schattenkartell',col:11}},catches:{u3:{hunter:'u1',t:T-5*6e4,status:'done',lat:47.0722,lng:15.444}}}};notify();uid='u0';pos={lat:47.0738,lng:15.4462};lastFix=T})()"""
TX = ['Ping!', 'Lena hat das Signal verloren', 'Tobias fängt Felix', 'Zone schrumpft: jetzt 420 m', 'Ping!', 'Extra-Ping!', 'Terminal verfügbar: Hacke es nicht – die Hider können es hacken',
      'Mira hackt das System', 'Zone schrumpft: jetzt 520 m', 'Ping!', 'Lena ist außerhalb der Zone – sichtbar', 'Live-Standort von Nora abgelaufen', 'Ping!', 'Zone schrumpft: jetzt 620 m',
      'Sperrgebiet aktiv', 'Ping!', 'Hider-Radar: 2 Hider in der Nähe', 'Ping!', 'Headstart vorbei – die Jagd beginnt', 'Spiel gestartet']
# Platzierungen: CSS, das die Leiste umsetzt (Knopf bleibt, wo er ist)
V = {
 '1': ('Karte am Knopf', """#blg{top:calc(56px + env(safe-area-inset-top,0px))!important;right:58px!important;left:auto;width:calc(100% - 116px)!important;max-width:340px;max-height:58vh!important;border-radius:14px!important;border:1px solid var(--line)!important;padding:12px 12px 4px!important;box-shadow:0 12px 34px #000a!important}"""),
 '2': ('Schwebende Karte unter der Anzeige', """#blg{top:calc(58px + env(safe-area-inset-top,0px))!important;left:12px!important;right:12px!important;width:auto!important;max-width:none!important;max-height:52vh!important;border-radius:16px!important;border:1px solid var(--line)!important;padding:12px 14px 4px!important;box-shadow:0 14px 40px #000b!important;transform:none!important}"""),
 '3': ('Blatt von unten über dem Panel', """#blg{top:auto!important;bottom:0!important;left:0!important;right:0!important;width:auto!important;max-width:none!important;max-height:64vh!important;border-radius:18px 18px 0 0!important;border:0!important;border-top:1px solid var(--line)!important;padding:8px 16px calc(10px + env(safe-area-inset-bottom,0px))!important;box-shadow:0 -12px 34px #000a!important;transform:none!important}
   #blg:before{content:"";display:block;width:38px;height:4px;border-radius:2px;background:var(--line);margin:0 auto 10px;flex:none}"""),
}
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(out, exist_ok=True)
    for k, (title, css) in V.items():
        imgs = []
        for n in (4, len(TX)):
            with app(width=412, height=915) as (pg, ev, errs):
                ev(GAME); ev("join('MOCK')"); pg.wait_for_timeout(1500); ev("bfClose&&bfClose()")
                pg.evaluate("""([tx,n,css])=>{const b=blLoad(),T=now();b.a=tx.slice(0,n).map((x,i)=>({t:T-i*55000-20000,x,...(x==='Ping!'?{r:{p:[['u2',47.073,15.448]]}}:{})}));b.seen=T;blSave();
                   document.head.insertAdjacentHTML('beforeend','<style>'+css+'</style>');blOpenF();
                   const k=$('lgk').getBoundingClientRect(),g=$('blg').getBoundingClientRect();$('blg').style.setProperty('--ar',(k.top-g.top+14)+'px')}""", [TX, n, css])
                pg.wait_for_timeout(400); fn = 'logplatz_%s_%d.png' % (k, n); shot(pg, fn); imgs.append(os.path.join(OUT, fn))
                if errs: print(k, errs[:3])
        W = Image.new('RGB', (412 * 2 + 24, 915 + 50), '#15171a'); d = ImageDraw.Draw(W)
        try: fn = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 19)
        except Exception: fn = None
        for i, (p, lab) in enumerate(zip(imgs, ['wenige Einträge', 'volle Liste (scrollt)'])):
            W.paste(Image.open(p), (i * 436, 50)); d.text((i * 436 + 6, 14), lab, fill='#e4e2dd', font=fn)
        p = os.path.join(out, 'Log_Platz_%s.png' % k); W.save(p); print(p, title)
