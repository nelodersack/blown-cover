# Test: Replays nach der Runde speichern und „Zuletzt abgespielt“ im Browser (IndexedDB)
# - Browser: rpSave(f,0) legt in IndexedDB ab, Liste zeigt es, gleiches Spiel nicht doppelt, höchstens RLMAX, Abspielen aus der Liste
# - App: rpSave speichert Datei (rpDl) nur, wenn mehr Wege da sind; Knopf meldet „schon gespeichert“; nichts in IndexedDB
# - App-Liste: je Code+Runde nur die neueste Datei
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
MK="""window.mkRep=(code,rnd,start,mins,winner,np)=>{const s={r0:500,rMin:200,shrink:3,step:50,head:2,dur:60,ping:180,pen:2,mode:'survive',imm:120,bon:true,hbC:60,hbL:60};
  const R0=start+120000,end=R0+mins*60000,tr={};for(let i=1;i<=2;i++){tr['p'+i]=[];if(i<=np)for(let t=start;t<=end;t+=60000)tr['p'+i].push([t,47.069+i*1e-3,15.4385,10])}
  return{format:'blown-cover-replay',v:2,code,round:rnd,game:{s,c:{lat:47.07,lng:15.44},startAt:start,R0,end,winner},
    players:[{id:'p1',name:'Anna',role:'hunter',col:0,state:'alive'},{id:'p2',name:'Lena',role:'hider',col:1,state:'alive'}],tracks:tr,log:[]}};"""
ROWS="[...document.querySelectorAll('.rlr')].map(r=>r.innerText.replace(/\\n/g,' | ')).join(' || ')"
T=1794830000000
# 1) Browser
with app(init=MK,width=412,height=915) as (pg,ev,errs):
    pg.wait_for_timeout(300)
    ev("rlOpen()");pg.wait_for_timeout(500)
    print('leer:',ev("$('pb').innerText").replace('\n',' | ')[:160])
    assert 'Zuletzt abgespielt' in ev("$('pb').innerText")
    shot(pg,'replay_zuletzt_leer.png')
    ev("rlClose()")
    ev(f"(async()=>{{await rlIdbPut(mkRep('K7QF',2,{T}-86400000,42,'hider',2));await rlIdbPut(mkRep('Q2XY',1,{T}-3600000,25,'hunter',2));}})()");pg.wait_for_timeout(600)
    ev(f"rpSave(mkRep('K7QF',2,{T}-86400000,42,'hider',2),0)");pg.wait_for_timeout(600)   # gleiches Spiel nochmal → nicht doppelt, nach oben
    ev("rlOpen()");pg.wait_for_timeout(600)
    rows=ev(ROWS);print('liste:',rows)
    assert rows.count('||')==1 and rows.startswith(ev("rlDate(%d-86400000)"%T)) and ev("bfName('K7QF',2)") in rows.split(' || ')[0]
    shot(pg,'replay_zuletzt.png')
    ev("document.querySelectorAll('.rlr')[1].click()");pg.wait_for_timeout(900)
    print('abspielen:',ev("!!RV"));assert ev("!!RV")
    ev("rvClose()");pg.wait_for_timeout(500)
    print('nach dem Abspielen oben:',ev(ROWS).split(' || ')[0])
    assert ev("bfName('Q2XY',1)") in ev(ROWS).split(' || ')[0]
    # Grenze RLMAX
    ev(f"(async()=>{{for(let i=0;i<RLMAX+3;i++)await rlIdbPut(mkRep('M'+String(i).padStart(3,'0'),0,{T}-i*7200000,10,'hider',1))}})()");pg.wait_for_timeout(2500)
    n=ev("(async()=>(await rlReq('meta','readonly',tx=>tx.objectStore('meta').getAll())).length)()");print('gespeichert:',n,'max',ev("RLMAX"))
    assert n==ev("RLMAX")
    e1=errs[:]

# 2) App: Datei nur bei mehr Wegen, keine IndexedDB, Liste je Spiel nur neueste Datei
LIST=[{'id':'n','name':'blowncover_replay_K7QF_r2_20261116-1015.json','size':900,'t':T,'dir':'Replays'},
      {'id':'o','name':'blowncover_replay_K7QF_r2_20261116-1012.json','size':500,'t':T-180000,'dir':'Replays'},
      {'id':'z','name':'blowncover_replay_Q2XY_r1_20261115-1830.json','size':800,'t':T-86400000,'dir':'Downloads'}]
BR="window.BlownNative={info:()=>JSON.stringify({app:1,ver:'0.3.7'}),ready:()=>true,log:()=>{},keepAwake:()=>{},stopTracking:()=>{},lastPos:()=>'',notify:()=>{},saveFile:()=>{},replays:()=>%s,readReplay:id=>''};"%json.dumps(json.dumps(LIST))
with app(init=MK+BR,width=412,height=915) as (pg,ev,errs):
    pg.wait_for_timeout(300)
    ev("window.__dl=0;rpDl=()=>{__dl++};0")
    ev(f"window.f1=mkRep('K7QF',2,{T}-3600000,30,'hider',1);window.f2=mkRep('K7QF',2,{T}-3600000,30,'hider',2)")
    ev("rpSave(f1,0)");ev("rpSave(f1,0)");ev("rpSave(f1,1)");pg.wait_for_timeout(300)
    print('Downloads nach 3× gleich:',ev("__dl"),'| Meldung:',ev("$('toast').innerText"))
    assert ev("__dl")==1 and 'schon gespeichert' in ev("$('toast').innerText")
    ev("rpSave(f2,1)");print('mit mehr Wegen:',ev("__dl"));assert ev("__dl")==2
    print('IndexedDB in der App:',ev("rlIdbOk()"));assert not ev("rlIdbOk()")
    ev("rlOpen()");pg.wait_for_timeout(300)
    print('app-liste:',ev("RL.items.map(f=>f.id).join(',')"))
    assert ev("RL.items.map(f=>f.id).join(',')")=='n,z'
    print('errors:',errs[:8]+e1)
