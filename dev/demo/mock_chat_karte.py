"""Mockup: Chat als Karte am Knopf (wie der Lagebericht). Echte App, echter Chat (#chat) mit echten Nachrichten, nur per CSS umgesetzt.
Aufruf: python3 dev/demo/mock_chat_karte.py [ordner] → Chat_Karte.png (heute | Karte Team | Karte Privat | beim Tippen)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app, shot, OUT
from PIL import Image, ImageDraw, ImageFont

GAME = """(()=>{const T=Date.now();__T['.info']={connected:true};const pl={
 u0:{name:'Manuel',role:'hunter',state:'alive',j:1,col:0,lat:47.0738,lng:15.4462,ts:T},u1:{name:'Sophie',role:'hunter',state:'alive',j:2,col:4,lat:47.0745,lng:15.444,ts:T},
 u5:{name:'Tobias',role:'hunter',state:'alive',j:6,col:9,lat:47.0731,lng:15.4452,ts:T},
 u2:{name:'Lena',role:'hider',state:'alive',j:3,col:6,lat:47.073,lng:15.448,ts:T},u3:{name:'Felix',role:'hider',state:'alive',j:4,col:3,lat:47.0722,lng:15.444,ts:T}};
 const m=(u,n,dt,x)=>({u,n,t:T-dt*1000,x,r:'hunter'});
 __T.chats={MOCK:{hunter:{a:m('u1','Sophie',300,'Ich nehme den Norden'),b:m('u0','Manuel',280,'Passt, ich bleib am Teich'),c:m('u5','Tobias',200,'Ping: Lena steht beim Spielplatz'),
   d:m('u1','Sophie',120,'Bin in 2 Min dort'),e:m('u0','Manuel',60,'Ich komm von Süden'),f:m('u5','Tobias',20,'Felix läuft Richtung Brücke!')},
   dm:{hunter:{u0_u1:{g:m('u1','Sophie',90,'Lass Tobias Felix holen, wir nehmen Lena'),h:m('u0','Manuel',70,'Deal')}}}}};
 __T.games={MOCK:{host:'u0',status:'running',startAt:T-14*6e4,c:{lat:47.0738,lng:15.4462},s:Object.assign({},DEF,preOf(30),{head:1}),players:pl}};notify();uid='u0';pos={lat:47.0738,lng:15.4462};lastFix=T})()"""

CARD = """#chat{left:auto!important;right:58px!important;top:calc(56px + env(safe-area-inset-top,0px))!important;bottom:auto!important;width:calc(100% - 116px)!important;max-width:340px;height:auto!important;max-height:58vh!important;
  border-radius:14px!important;border:1px solid var(--line);box-shadow:0 12px 34px #000a!important;background:#1b1e22!important;overflow:hidden}
#chh{padding:10px 10px 8px 12px!important;border-bottom:0!important}#chh>button{width:30px!important;height:30px;min-height:0!important;padding:0!important;border-radius:50%!important;color:var(--mut)!important}
#cht{background:var(--bg);border-radius:999px;padding:3px;gap:2px!important;flex-wrap:nowrap!important}#cht .s{border:0!important;background:none!important;padding:4px 10px!important;font-size:12.5px!important;border-radius:999px!important;opacity:1!important;color:var(--mut)!important;min-height:0!important;margin:0!important}
#cht .s.on{background:var(--fg)!important;color:var(--bg)!important}
#chp{padding:2px 12px 0!important}#chm{flex:0 1 auto!important;padding:6px 12px!important}#chm .m{font-size:13.5px;padding:5px 9px}
#chq{padding:6px 10px 0!important}#chq button.qr{min-height:30px!important;padding:4px 10px!important;font-size:12px!important}
#chr{padding:8px 10px 10px!important}#chr input{min-height:38px!important;font-size:14px}#chr button#chs{width:38px!important;min-height:38px!important;height:38px}
#chat.kb{left:8px!important;right:8px!important;width:auto!important;max-width:none!important;top:auto!important;bottom:300px!important;max-height:calc(100vh - 300px - 64px)!important}
.kbd{position:fixed;left:0;right:0;bottom:0;height:300px;background:#2b2e33;z-index:3000;display:grid;place-items:center;color:#8a8f96;font:600 14px var(--f-b);letter-spacing:.06em}"""

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(out, exist_ok=True)
    imgs = []
    for st in ('heute', 'team', 'privat', 'tippen'):
        with app(width=412, height=915) as (pg, ev, errs):
            ev(GAME); ev("join('MOCK')"); pg.wait_for_timeout(1500); ev("bfClose&&bfClose()")
            if st != 'heute': ev("document.head.insertAdjacentHTML('beforeend','<style>'+%s+'</style>')" % json.dumps(CARD))
            ev("chToggle(true)"); pg.wait_for_timeout(400)
            if st == 'privat': ev("chShow('dm:u1')")
            if st == 'tippen':
                ev("$('chat').classList.add('kb');const k=document.createElement('div');k.className='kbd';k.textContent='TASTATUR';document.body.appendChild(k);const i=document.querySelector('#chr input');i.value='Ich seh ihn, komm schnell';i.focus()")
            pg.wait_for_timeout(400); fn = 'chatkarte_%s.png' % st; shot(pg, fn); imgs.append(os.path.join(OUT, fn))
            if errs: print(st, errs[:3])
    W = Image.new('RGB', (412 * 4 + 72, 915 + 50), '#15171a'); d = ImageDraw.Draw(W)
    try: fn = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 19)
    except Exception: fn = None
    for i, (p, lab) in enumerate(zip(imgs, ['heute (Blatt von unten)', 'Karte · Team', 'Karte · Privat', 'beim Tippen'])):
        W.paste(Image.open(p), (i * 436, 50)); d.text((i * 436 + 6, 14), lab, fill='#e4e2dd', font=fn)
    p = os.path.join(out, 'Chat_Karte.png'); W.save(p); print(p)
