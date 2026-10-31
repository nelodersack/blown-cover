# Test: Missionsbriefing (Konzept claude/KONZEPT_Briefing.md)
import sys,os,re;sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import app,shot
NAMES=['Anna','Fanuel','Lena','Max','Tom','Sara']
def setup(ev,uid,mode='survive',tasks=True,status='running',winner=None,rn=0,state='alive'):
    ev("""(()=>{__T['.info']={connected:true};notify();const T=Date.now(),R0=T-40000+2*60000,M=m=>R0+m*60000;
      __T.games={AFG5K9:{host:'u1',status:'%s',rn:%d,startAt:T-40000,c:{lat:47.0705,lng:15.4395},%s
      s:{r0:500,rMin:200,shrink:3,step:50,head:2,dur:30,ping:180,pen:1,mode:'%s',taskR:0,imm:120,shOn:true,shT:6,evT:5,ddN:1,ddT:12,mtN:1,mtT:15,bon:true,hbOn:true,hbN:2,hbC:60,hbL:40,hbT:15,gw:20,gd:60,ot:3,hk:true,hkS:9,hkZ:75,hkT:180,hkR:60,hkN:3,ozR:75},
      tasks:%s,
      players:{u1:{name:'Anna',role:'hunter',state:'alive',j:1,col:0,lat:47.0690,lng:15.4385,ts:T},u5:{name:'Fanuel',role:'hunter',state:'alive',j:5,col:4,lat:47.0688,lng:15.4405,ts:T},
        u2:{name:'Lena',role:'hider',state:'%s',j:2,col:1,lat:47.0712,lng:15.4402,ts:T},u3:{name:'Max',role:'hider',state:'alive',j:3,col:2,lat:47.0716,lng:15.4380,ts:T},
        u4:{name:'Tom',role:'hider',state:'alive',j:4,col:3,lat:47.0699,lng:15.4415,ts:T},u6:{name:'Sara',role:'hider',state:'alive',j:6,col:5,lat:47.0720,lng:15.4392,ts:T}},cols:{0:'u1',1:'u2',2:'u3',3:'u4',4:'u5',5:'u6'}}};
      uid='%s';pos={lat:47.07,lng:15.44};lastFix=Date.now()})()"""%(status,rn,("winner:'%s',"%winner) if winner else '',mode,
      ("{sh:{t0:M(6),loc:{lat:47.07,lng:15.44},rr:0},hk:{t0:M(9),loc:{lat:47.071,lng:15.441},rr:0},d1:{t0:M(12),loc:{lat:47.069,lng:15.44},rr:0,a:'u3',b:'u4'},m1:{t0:M(15),loc:{lat:47.07,lng:15.44},rr:0,a:'u2',b:'u6'}"+(",ev:{t0:M(25),loc:{lat:47.07,lng:15.44},rr:0}" if mode=='mission' else '')+"}") if tasks else 'null',state,uid))
    ev("join('AFG5K9')")
txt=lambda ev:ev("$('bfd')?$('bfd').innerText:'(kein Briefing)'")
res={}
for uid in ('u2','u3','u1','u5'):
    with app() as (pg,ev,errs):
        setup(ev,uid);pg.wait_for_timeout(1200);res[uid]=txt(ev)
        if uid=='u2':
            shot(pg,'briefing_hider.png')
            ev("document.querySelector('#bfd .bt button').click()");pg.wait_for_timeout(200)
            print('geschlossen:',ev("!$('bfd')"),'Merker:',ev("LS[bfKey()]"))
            ev("onData()");pg.wait_for_timeout(200);print('nach onData (wie Neuladen) wieder da?',ev("!!$('bfd')"))
            pg.locator('.bfb').first.click();pg.wait_for_timeout(200);print('Knopf öffnet:',ev("!!$('bfd')"))
        if uid=='u1':shot(pg,'briefing_hunter.png')
        if errs:print(uid,'ERR',errs[:5])
print('Hider gleich:',res['u2']==res['u3'],'· Hunter gleich:',res['u1']==res['u5'],'· Hider≠Hunter:',res['u2']!=res['u1'])
for k in ('u2','u1'):
    t=res[k];print('---',k,'\n'+t)
    print('Namen im Text:',[n for n in NAMES if re.search(r'\b'+n+r'\b',t)])
print('Überschrift Überleben (Hider/Hunter):',re.findall(r'MISSIONSZIELE[^\n]*|ERKENNTNISSE[^\n]*',res['u2']+'\n'+res['u1']))
hz=[int(x) for x in re.findall(r'Minute (\d+)',res['u2'])];print('Hider-Zeiten sortiert:',hz,hz==sorted(hz))
print('Hunter ohne Zeiten/Anzahl der Aufgaben:',not re.search(r'Minute \d|\d+ (Dossier|Treffen)',res['u1']))
with app() as (pg,ev,errs):
    setup(ev,'u2',state='caught');pg.wait_for_timeout(1200)
    print('Zuschauer: Umschalter',ev("document.querySelectorAll('#bfd .tabs2 button').length"),'·',ev("$('bfd').querySelector('.op').innerText.replace(/\\n/g,' ')"))
    ev("$('bfd').querySelectorAll('.tabs2 button')[1].click()");pg.wait_for_timeout(200);print('  nach Umschalten:',ev("$('bfd').querySelector('.op').innerText.replace(/\\n/g,' ')"))
    print('errors:',errs[:5])
with app() as (pg,ev,errs):
    setup(ev,'u2',tasks=False);pg.wait_for_timeout(1200);print('ohne Aufgaben: Zielliste',ev("!!$('bfd').querySelector('ul')"),'· Text:',ev("$('bfd').querySelector('.bb').innerText.replace(/\\n/g,' | ')"))
    print('errors:',errs[:5])
with app() as (pg,ev,errs):
    setup(ev,'u2',mode='mission');pg.wait_for_timeout(1200);print('Mission:',ev("[...$('bfd').querySelectorAll('.bb p.tx')][1].innerText"),'· Überschrift:',ev("$('bfd').querySelectorAll('.bb p.lb')[2].innerText"),'·',ev("[...$('bfd').querySelectorAll('li')].map(l=>l.innerText).join(' / ')"))
    print('errors:',errs[:5])
for uid,w in (('u2','hider'),('u1','hider'),('u2','host')):
    with app() as (pg,ev,errs):
        setup(ev,uid,status='over',winner=w);pg.wait_for_timeout(1500)
        print('Ende',uid,w,'->',ev("(document.querySelector('#resb .rsop')||{}).innerText"),'· Briefing zu:',ev("!$('bfd')"))
        if uid=='u2' and w=='hider':shot(pg,'briefing_ende.png')
        print('errors:',errs[:5])
with app() as (pg,ev,errs):
    print('Name deterministisch:',ev("bfName('AFG5K9',0)===bfName('AFG5K9',0)"),'· Runde 2 anders:',ev("bfName('AFG5K9',0)+' / '+bfName('AFG5K9',1)"))
    print('errors:',errs[:5])
