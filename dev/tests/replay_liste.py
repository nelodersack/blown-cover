# Test: Replay-Liste in der App (Bridge replays/readReplay): mehrere Replays (neueste oben, Datum, Operationsname, Dauer,
# Gewinner, Zombie-Benennung), eine kaputte Datei, Analyse-Datei ausgeblendet, Zwischenspeicher, Abspielen, leere Liste,
# ohne Bridge → Dateiauswahl
import sys,os,json;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
def rep(code,rnd,start,mins,winner,mode='survive'):
    s={'r0':500,'rMin':200,'shrink':3,'step':50,'head':2,'dur':60,'ping':180,'pen':2,'mode':mode,'imm':120,'bon':True,'hbC':60,'hbL':60}
    R0=start+120000;end=R0+mins*60000
    tr={'p1':[[t,47.069,15.4385,10] for t in range(start,end+1,60000)],'p2':[[t,47.0705,15.4405,10] for t in range(start,end+1,60000)]}
    return json.dumps({'format':'blown-cover-replay','v':2,'code':code,'round':rnd,'game':{'s':s,'c':{'lat':47.07,'lng':15.44},'startAt':start,'R0':R0,'end':end,'winner':winner},
      'players':[{'id':'p1','name':'Anna','role':'hunter','col':0,'state':'alive'},{'id':'p2','name':'Lena','role':'hider','col':1,'state':'alive'}],'tracks':tr,'log':[]})
T=1794830000000
FILES={'a':rep('K7QF',2,T-86400000*3,42,'hider'),'b':rep('ZMB4',0,T-3600000,27,'hunter','zombie'),'c':'{kaputt','d':rep('Q2XY',1,T-86400000,60,'hunter'),'x':'{}'}
LIST=[{'id':'a','name':'blowncover_replay_K7QF_r2_20261113-1712.json','size':len(FILES['a']),'t':T-86400000*3+3e6,'dir':'Replays'},
      {'id':'b','name':'blowncover_replay_ZMB4_r0_20261116-0900.json','size':len(FILES['b']),'t':T-3600000+2e6,'dir':'Replays'},
      {'id':'c','name':'blowncover_replay_XXXX_r0_20261115-1200.json','size':5,'t':T-7200000,'dir':'Downloads'},
      {'id':'d','name':'blowncover_replay_Q2XY_r1_20261115-1830.json','size':len(FILES['d']),'t':T-86400000+4e6,'dir':'Replays'},
      {'id':'x','name':'blowncover_analyse_Q2XY_20261115.json','size':2,'t':T,'dir':'Downloads'}]
BR="window.__reads=0;window.BlownNative={info:()=>JSON.stringify({app:1,ver:'0.3.7'}),ready:()=>true,log:()=>{},keepAwake:()=>{},stopTracking:()=>{},lastPos:()=>'',notify:()=>{},saveFile:()=>{},replays:()=>%s,readReplay:id=>{__reads++;return (%s)[id]||''}};"
ROWS="[...document.querySelectorAll('.rlr')].map(r=>r.innerText.replace(/\\n/g,' | ')).join(' || ')"
with app(init=BR%(json.dumps(json.dumps(LIST)),json.dumps(FILES)),width=412,height=915) as (pg,ev,errs):
    pg.wait_for_timeout(400)
    ev("rlOpen()");print('sofort:',ev(ROWS)[:200])
    shot(pg,'replay_liste_platzhalter.png')
    pg.wait_for_timeout(1200)
    rows=ev(ROWS);print('gefüllt:',rows)
    assert rows.count('||')==3, 'Analyse-Datei darf nicht erscheinen'
    r=rows.split(' || ')
    lab=ev("[...document.querySelectorAll('.rlr .w')].map(w=>(w.getAttribute('aria-label')||'')+':'+(w.querySelector('path')?'D':w.querySelector('circle')?'K':'-')).join(',')");print('gewinner:',lab)
    assert lab=='Zombies gewinnen:D,:-,Hunter gewinnen:D,Hider gewinnen:K', lab
    assert '27 / 60 Min' in r[0], r[0]
    assert 'Datei nicht lesbar' in r[1], r[1]
    assert '60 Min' in r[2] and '/' not in r[2] and '42 / 60 Min' in r[3]
    ab=ev("rlRow({id:'h',size:1,t:1},{d:Date.now(),op:'X',m:12,p:60,w:'host'})+rlRow({id:'h2',size:1,t:1},{d:Date.now(),op:'Y',m:60,p:60,w:''})")
    print('ohne Gewinner:',ab.count('Abgebrochen'),ab.count('Beendet'));assert 'Abgebrochen' in ab and 'Beendet' in ab
    assert ev("bfName('K7QF',2)") in r[3]
    shot(pg,'replay_liste.png')
    n=ev("__reads");print('gelesen:',n)
    # zweites Öffnen: alles aus dem Zwischenspeicher
    ev("rlClose();rlOpen()");pg.wait_for_timeout(300);print('erneut gelesen:',ev("__reads")-n)
    assert ev("__reads")==n
    # kaputte Zeile antippen: kein Absturz, Meldung
    ev("document.querySelectorAll('.rlr')[1].click()");pg.wait_for_timeout(300);print('kaputt:',ev("$('toast').innerText"))
    assert 'nicht lesbar' in ev("$('toast').innerText") and not ev("!!RV")
    # Abspielen
    ev("document.querySelectorAll('.rlr')[3].click()");pg.wait_for_timeout(800)
    print('replay:',ev("!!RV"),ev("document.querySelector('#pb h2')&&document.querySelector('#pb h2').innerText"))
    assert ev("!!RV")
    ev("rvClose()");pg.wait_for_timeout(500);print('zurück in der Liste:',ev("RL.on"),ev("document.querySelectorAll('.rlr').length"))
    assert ev("RL.on") and ev("document.querySelectorAll('.rlr').length")==4
    e1=errs[:]

# leere Liste
with app(init=BR%(json.dumps('[]'),'{}'),width=412,height=915) as (pg,ev,errs):
    pg.wait_for_timeout(300);ev("rlOpen()");pg.wait_for_timeout(300)
    t=ev("$('pb').innerText");print('leer:',t.replace('\n',' | '))
    assert 'Noch keine Replays' in t and 'Andere Datei öffnen' in t
    shot(pg,'replay_liste_leer.png');e2=errs[:]

# ohne Bridge (Browser): Liste „Zuletzt abgespielt“; ohne IndexedDB: Dateiauswahl wie bisher
with app() as (pg,ev,errs):
    pg.wait_for_timeout(300)
    ev("window.__pick=0;rvPick=()=>{__pick++};rlOpen();0");pg.wait_for_timeout(400)
    print('Browser → Liste:',ev("RL.on"),ev("RL.src"),'Dateiauswahl:',ev("__pick"))
    assert ev("RL.on") and ev("RL.src")=='idb' and ev("__pick")==0
    ev("rlClose();Object.defineProperty(window,'indexedDB',{get:()=>undefined});rlOpen();0");pg.wait_for_timeout(300)
    print('ohne IndexedDB → Dateiauswahl:',ev("__pick"))
    assert ev("__pick")==1
    print('errors:',errs[:8]+e1+e2)
