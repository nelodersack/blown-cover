"""Spielanleitung (PDF) aus der Spielerklärung: App ab v0.3.9 ruft BlownNative.openPdf mit der richtigen Adresse
auf und bleibt auf der Seite; App ohne openPdf und Browser behalten den Link (GitHub bzw. spielregeln.pdf)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from harness import app

NB = "window.__pdf=[];window.BlownNative={info:()=>'{\"ver\":\"0.3.9\"}',log(){},notify(){},lastPos:()=>'',ready:()=>true,openPdf:u=>__pdf.push(u)}"
OLD = "window.BlownNative={info:()=>'{\"ver\":\"0.3.8\"}',log(){},notify(){},lastPos:()=>'',ready:()=>true}"

def last_step(pg, ev):
    pg.wait_for_timeout(500)
    ev("inOpen?inOpen():$('inb').click()"); pg.wait_for_timeout(600)
    ev("inStep(INS.length-1,1)"); pg.wait_for_timeout(300)

with app(390, 844, hash='', init=NB) as (pg, ev, errs):
    last_step(pg, ev)
    url0 = ev("location.href")
    pg.click('a.slink'); pg.wait_for_timeout(300)
    assert ev("__pdf") == [ev("location.origin") + '/spielregeln.pdf'], ev("__pdf")
    assert ev("location.href") == url0, 'Seite gewechselt'
    print('App v0.3.9 ok:', ev("__pdf"), 'errors:', errs)

with app(390, 844, hash='', init=OLD) as (pg, ev, errs):
    last_step(pg, ev)
    assert ev("inPdf()") is True
    assert 'github.com' in ev("document.querySelector('a.slink').href")
    print('App alt ok, errors:', errs)

with app(390, 844, hash='') as (pg, ev, errs):
    last_step(pg, ev)
    assert ev("inPdf()") is True
    assert ev("document.querySelector('a.slink').href").endswith('/spielregeln.pdf')
    print('Browser ok, errors:', errs)
