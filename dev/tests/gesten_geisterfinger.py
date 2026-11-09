# Test: verlorene Finger (iOS ohne pointerup) dürfen keine Dauer-Zwei-Finger-Geste auslösen
import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ux_feinschliff.py')).read().split('# 1 Lobby')[0])
PE="(t,id,x,y,pr)=>mapEl.dispatchEvent(new PointerEvent(t,{pointerId:id,pointerType:'touch',isPrimary:pr,clientX:x,clientY:y,bubbles:true}))"
with app(390,844) as (pg,ev,errs):
    game(ev,'u2');go(ev,pg);pg.wait_for_timeout(1000);assert ev("rotOn")
    ev(f"window.pe={PE}")
    ev("pe('pointerdown',1,150,300,true);pe('pointerdown',2,250,300,false)");assert ev("!!gz")
    ev("dispatchEvent(new PointerEvent('pointerup',{pointerId:2,pointerType:'touch'}))")   # Finger 1 geht verloren (kein pointerup)
    assert ev("tps.size")==1 and not ev("gz")
    ev("pe('pointerdown',3,200,400,true)");print('nach neuem Ein-Finger-Start: tps',ev("tps.size"),'Geste',ev("!!gz"));assert ev("tps.size")==1 and not ev("gz")
    z0=ev("map.getZoom()");ev("pe('pointermove',3,200,300,true)");pg.wait_for_timeout(200);assert ev("map.getZoom()")==z0
    # touchend ohne Finger auf dem Glas räumt auf
    ev("pe('pointerdown',4,100,100,false)");assert ev("!!gz")
    ev("document.dispatchEvent(new TouchEvent('touchend',{touches:[],bubbles:true}))");assert ev("tps.size")==0 and not ev("gz")
    print('errors:',[e for e in errs if 'PE:' in e]);assert not [e for e in errs if 'PE:' in e]
