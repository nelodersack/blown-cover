# Test: Sprungfilter – einzelne GPS-Ausreißer werden verworfen, bestätigte Ortswechsel übernommen (ohne Testmodus, echte watchPosition)
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app
INIT="""(()=>{const g={cb:null,watchPosition(ok){g.cb=ok;return 1},clearWatch(){},getCurrentPosition(ok){ok({coords:{latitude:47.0716,longitude:15.4355,accuracy:8}})}};
  Object.defineProperty(navigator,'geolocation',{value:g,configurable:true});
  window.__fix=(la,ln,ac)=>g.cb&&g.cb({coords:{latitude:la,longitude:ln,accuracy:ac||10}})})()"""
with app(390,844,hash='',init=INIT) as (pg,ev,errs):
    ev("AL.on=true;startGPS()");pg.wait_for_timeout(200)
    P=lambda:ev("pos&&[+pos.lat.toFixed(6),+pos.lng.toFixed(6)]")
    def fix(la,ln,wait=1100,ac=10):ev(f"__fix({la},{ln},{ac})");pg.wait_for_timeout(wait)
    fix(47.072219,15.435025);assert P()==[47.072219,15.435025]
    fix(47.07044,15.434491,ac=13);print('Ausreißer 200 m:',P());assert P()==[47.072219,15.435025]   # verworfen
    fix(47.072206,15.435084);assert P()==[47.072206,15.435084]                                        # normal weiter
    fix(47.074099,15.435338);fix(47.072489,15.435514);print('Ping-Pong:',P());assert P()==[47.072489,15.435514]
    pg.wait_for_timeout(5000);fix(47.0730,15.4355);print('57 m in 6 s:',P());assert P()==[47.0730,15.4355]            # Gehen/Laufen bleibt erlaubt
    fix(47.0700,15.4360);fix(47.07002,15.43602);print('bestätigter Wechsel:',P());assert P()==[47.07002,15.43602]
    n=ev("AL.ev.filter(e=>e[1]==='gj').length");print('gj-Einträge',n);assert n==3
    print('errors:',[e for e in errs if 'PE:' in e]);assert not [e for e in errs if 'PE:' in e]
