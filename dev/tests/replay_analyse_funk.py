# Test: Analyse-Datei → Replay mit Funk (rvConv/rvAnFunk) und wiederverwendete Marker-IDs (mkMerge, Abschnitte in rvPrep)
import sys,os;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app
with app(width=412,height=915) as (pg,ev,errs):
    r=ev("""(()=>{const T=1.8e12,s=Object.assign({},DEF,preOf(30),{dur:30,head:0,ping:60}),pl=[{id:'S1',name:'Anna',role:'hunter',color:'Blau'},{id:'S2',name:'Ben',role:'hunter',color:'Rot'},{id:'S3',name:'Cleo',role:'hider',color:'Grün'},{id:'S4',name:'Dora',role:'hider',color:'Gelb'}];
      const tl=[[T+1000,1,'S3,S4','chat',['hider','Cleo','hider','Hallo',T+1000]],[T+2000,2,'S3,S4','chat',['dm:S4','Cleo','hider','Privat',T+2000]],
        [T+3000,3,'S1','chat',['all','Anna','hunter','Lobby',T+3000]],
        [T+5000,5,'S1','mk+',['S1_0','S1','arrow',47.07,15.44,null,null]],[T+5300,5,'S2','mk+',['S1_0','S1','arrow',47.07,15.44,null,null]],
        [T+9000,9,'S1','mk-','S1_0'],[T+9200,9,'S2','mk-','S1_0'],
        [T+60000,60,'S1','mk+',['S1_0','S1','pin',47.071,15.441,null,'Tor']],[T+60100,60,'S2','mk+',['S1_0','S1','pin',47.071,15.441,null,'Tor']]];
      const o={format:'blown-cover-analyse',code:'ANFK',round:0,game:{settings:s,center:{lat:47.07,lng:15.44},startAt:T,winner:'hider'},players:pl,timeline:tl,tracks:{S1:[[T,47.07,15.44,5]],S2:[[T,47.07,15.44,5]],S3:[[T,47.07,15.44,5]],S4:[[T,47.07,15.44,5]]}};
      const f=rvConv(o);rvLoad(f);return {ch:f.funk.ch.map(x=>[x[1],x[2],x[3]]),mk:f.funk.mk.map(x=>[x[1],x[2],x[3]||null]),mki:RV.mki.map(x=>[x.k,x.t1-x.t0])}})()""")
    print(r)
    assert r['ch']==[['S3','hider','Hallo'],['S3','d:hider:S3_S4','Privat']]
    assert r['mk']==[['+','S1_0','arrow'],['-','S1_0',None],['+','S1_0','pin']]
    assert len(r['mki'])==2 and r['mki'][0]==['arrow',4000] and r['mki'][1][0]=='pin'
    print('errors:',errs)
sys.exit(1 if errs else 0)
