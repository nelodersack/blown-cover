# Test: Chat/Log verschieben + Größe ändern + merken + zurücksetzen; Schnellnachrichten bei langem Chat sichtbar; Panel beim Tippen weg
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
with app(width=412,height=915) as (pg,ev,errs):
    ev("""(()=>{const T=Date.now();__T['.info']={connected:true};const pl={u0:{name:'Manuel',role:'hunter',state:'alive',j:1,col:0,lat:47.07,lng:15.44,ts:T},u1:{name:'Sophie',role:'hunter',state:'alive',j:2,col:4,lat:47.071,lng:15.441,ts:T},
      u2:{name:'Lena',role:'hider',state:'alive',j:3,col:6,lat:47.0705,lng:15.4405,ts:T}};const h={};for(let i=0;i<25;i++)h['m'+i]={u:i%2?'u1':'u0',n:i%2?'Sophie':'Manuel',t:T-(30-i)*20000,x:'Nachricht '+i,r:'hunter'};
      __T.chats={FENS:{hunter:h}};__T.games={FENS:{host:'u0',status:'running',startAt:T-6e5,c:{lat:47.07,lng:15.44},s:Object.assign({},DEF,preOf(30),{head:0}),players:pl}};notify();uid='u0';pos={lat:47.07,lng:15.44};lastFix=T})()""")
    ev("join('FENS')");pg.wait_for_timeout(1500);ev("bfClose&&bfClose()");ev("chToggle(true)");pg.wait_for_timeout(400)
    q=ev("(()=>{const c=$('chat').getBoundingClientRect(),r=$('chq').getBoundingClientRect();return[r.height,r.bottom<=c.bottom+1,getComputedStyle($('chq')).display]})()");print('Schnellnachrichten:',q)
    assert q[2]=='none' or (q[0]>=28 and q[1])
    r0=ev("(()=>{const r=$('chat').getBoundingClientRect();return[r.left,r.top,r.width,r.height]})()")
    # an der Kopfzeile (freie Stelle) ziehen
    hx,hy=r0[0]+r0[2]*0.6,r0[1]+18
    pg.mouse.move(hx,hy);pg.mouse.down();pg.mouse.move(hx-40,hy+200,steps=6);pg.mouse.up();pg.wait_for_timeout(200)
    r1=ev("(()=>{const r=$('chat').getBoundingClientRect();return[r.left,r.top,r.width,r.height]})()");g=ev("JSON.parse(LS.win_chat||'null')");print('verschoben:',r0,'→',r1,g)
    assert abs(r1[1]-r0[1]-200)<3 and abs(r1[0]-(r0[0]-40))<3 and g
    # Größe über die Ecke
    cx,cy=r1[0]+r1[2]-8,r1[1]+r1[3]-8
    pg.mouse.move(cx,cy);pg.mouse.down();pg.mouse.move(cx+30,cy-120,steps=6);pg.mouse.up();pg.wait_for_timeout(200)
    r2=ev("(()=>{const r=$('chat').getBoundingClientRect();return[r.left,r.top,r.width,r.height]})()");print('Größe:',r2);assert abs(r2[3]-(r1[3]-120))<3
    shot(pg,'fenster_chat.png')
    ev("chToggle(false);chToggle(true)");pg.wait_for_timeout(200)
    r3=ev("(()=>{const r=$('chat').getBoundingClientRect();return[r.left,r.top,r.width,r.height]})()");assert [round(x) for x in r3]==[round(x) for x in r2]
    # Tippen: feste Lage, Panel weg, danach wieder eigene Lage
    ev("$('chi').focus()");pg.wait_for_timeout(200);assert ev("$('chat').classList.contains('kb')&&document.body.classList.contains('chkb')&&!$('chat').style.top")
    ev("$('chi').blur()");pg.wait_for_timeout(300);assert not ev("document.body.classList.contains('chkb')") and ev("$('chat').style.top")
    # zurücksetzen
    ev("winReset('chat')");assert ev("!LS.win_chat&&!$('chat').style.top&&!$('chat').classList.contains('cust')")
    # Log
    ev("blOpenF()");pg.wait_for_timeout(300);b0=ev("(()=>{const r=$('blg').getBoundingClientRect();return[r.left,r.top,r.width,r.height]})()")
    pg.mouse.move(b0[0]+20,b0[1]+20);pg.mouse.down();pg.mouse.move(b0[0]-10,b0[1]+300,steps=5);pg.mouse.up();pg.wait_for_timeout(200)
    print('LS:',ev('LS.win_blg'),ev("(()=>{const r=$('blg').getBoundingClientRect();return[r.left,r.top]})()"));ev("blClose();blOpenF()");pg.wait_for_timeout(200)
    b1=ev("(()=>{const r=$('blg').getBoundingClientRect();return[r.left,r.top]})()");print('Log:',b0,'→',b1);assert abs(b1[1]-b0[1]-280)<3
    assert ev("getComputedStyle(document.querySelector('#blg .wrst')).display")!='none'
    shot(pg,'fenster_log.png')
    print('errors:',errs[:5]);assert not errs
