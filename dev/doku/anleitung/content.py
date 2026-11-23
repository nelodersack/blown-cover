# -*- coding: utf-8 -*-
# Texte der Spielregeln (Kurzanleitung KURZ, Vollversion V). Eine Seite = ein Handybildschirm (90 x 160 mm).
# Bauen: python3 dev/doku/anleitung/build.py  (siehe README.md)
import os
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img") + "/"

def sym(name, cls="sy"):
    return f'<img class="{cls}" src="{IMG}sym_{name}.png" alt="">'

def page(cls, kicker, title, body, sub=None):
    sub_html = f'<p class="sub">{sub}</p>' if sub else ""
    return f'''<section class="page {cls}">
  <div class="kicker"><span>{kicker}</span></div>
  <h2>{title}</h2>{sub_html}
  <div class="body">{body}</div>
  <div class="foot"><span class="brand">BLOWN COVER</span><span class="pn"></span></div>
</section>'''

def fig(name, cap, w=76, h=None):
    st = f"width:{w}mm" + (f";height:{h}mm" if h else "")
    return f'<figure class="fig" style="width:{w}mm"><div class="shot" style="{st}"><img src="{IMG}{name}.jpg" alt=""></div><figcaption>{cap}</figcaption></figure>'

def pair(a, b, h=None):
    return f'<div class="pair">{fig(a[0], a[1], 36.5, h)}{fig(b[0], b[1], 36.5, h)}</div>'

def side(text, name, cap, w=33, h=None):
    return f'<div class="side"><div class="side-t">{text}</div>{fig(name, cap, w, h)}</div>'

def rule(n, title, text):
    return f'<div class="rule"><div class="num">{n}</div><div><h3>{title}</h3><p>{text}</p></div></div>'

def item(title, text, icon=""):
    ic = f'<div class="it-ic">{sym(icon)}</div>' if icon else ""
    return f'<div class="item{" has-ic" if icon else ""}">{ic}<div><h4>{title}</h4><p>{text}</p></div></div>'

def role(kind, name, goal, points):
    lis = "".join(f"<li>{p}</li>" for p in points)
    icon = sym("hider" if kind == "hider" else "hunter", "role-ic")
    return f'<div class="role {kind}"><div class="role-h">{icon}<div><div class="role-name">{name}</div><div class="goal">{goal}</div></div></div><ul>{lis}</ul></div>'

def note(text, cls=""):
    return f'<div class="note {cls}">{text}</div>'

def checklist(items):
    return '<ul class="check">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def dash(items):
    return '<ul class="dash">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def steps(items):
    return '<ol class="steps">' + "".join(f"<li>{i}</li>" for i in items) + "</ol>"

def kv(rows):
    return '<table class="kv">' + "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in rows) + "</table>"

def symgrid(keys):
    rows = "".join(f'<div class="sym">{sym(k)}<div><b>{t}</b><span>{d}</span></div></div>' for k, t, d in keys)
    return f'<div class="symgrid">{rows}</div>'

def cover(kind, lead, toc, az):
    toc_html = "".join(f'<li><span>{a}</span><span class="dots"></span><span>{b}</span></li>' for a, b in toc)
    return f'''<section class="page cover">
  <div class="cv-head"><span>{az}</span><span class="cv-kind">{kind}</span></div>
  <div class="stamp"><svg viewBox="0 0 220 70"><defs><filter id="ink" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.55" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in" result="c"/><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="1" seed="9" result="w"/><feDisplacementMap in="c" in2="w" scale="2.2"/></filter></defs>
    <g filter="url(#ink)" fill="none" stroke="#b02a24"><rect x="4" y="4" width="212" height="62" rx="3" stroke-width="3.2"/><rect x="9" y="9" width="202" height="52" rx="2" stroke-width="1.2"/>
    <text x="110" y="45" text-anchor="middle" fill="#b02a24" stroke="none" font-family="Plex Mono" font-weight="700" font-size="25" letter-spacing="3">GEHEIM</text></g></svg></div>
  <div class="cv-mid">
    <div class="logo">BLOWN<br>COVER</div>
    <div class="cv-sub">{kind}</div>
    <p class="cv-lead">{lead}</p>
  </div>
  <ol class="toc">{toc_html}</ol>
  <div class="foot"><span class="brand">BLOWN COVER</span><span class="pn"></span></div>
</section>'''

LEAD = ("Ein Versteckspiel für draußen, gespielt mit dem Handy. Die <b>Hider</b> bewegen sich in einer Zone, "
        "die immer kleiner wird. Die <b>Hunter</b> sehen in regelmäßigen Abständen, wo die Hider gerade "
        "waren, und versuchen, sie zu fangen.")

PING_TXT = ("In festen Abständen zeigt die App den Huntern, wo jeder Hider in diesem Moment steht: "
            "einen Kreis in der Farbe des Hiders mit seinem Anfangsbuchstaben. Bis zum nächsten Ping bleibt "
            "dieser Punkt stehen, auch wenn der Hider längst weitergelaufen ist.")

# =====================================================================
# KURZANLEITUNG
# =====================================================================
KURZ = [cover("Kurzanleitung", LEAD,
    [("<b>Teil 1</b> · Die erste Runde", "2–6"), ("<b>Teil 2</b> · Aufgaben, Boni, Modi", "7–9")], "AZ BC-26 · K")]

KURZ.append(page("c-roles", "Teil 1 · Die erste Runde", "Zwei Seiten",
    role("hider", "Hider", "Bis zum Ende frei bleiben.", [
        "Bleib in der roten Zone.",
        "Bleib in Bewegung. Bei jedem Ping sehen die Hunter, wo du gerade stehst.",
    ]) +
    role("hunter", "Hunter", "Alle Hider fangen, bevor die Zeit abläuft.", [
        "Zu Beginn haben die Hider einige Minuten Vorsprung.",
        "Ein Ping zeigt, wo die Hider waren, nicht wo sie jetzt sind.",
    ]) +
    note("Die Hunter gewinnen, wenn alle Hider gefangen sind. Die Hider gewinnen, wenn die Zeit abläuft.", "win")
))

KURZ.append(page("c-zone", "Teil 1 · Die erste Runde", "Die Zone",
    side("<p>Der rote Kreis ist das Spielfeld. Er wird in festen Abständen kleiner, der gestrichelte Kreis zeigt die nächste Größe.</p>"
    "<p>Wer als Hider hinausgeht, ist für die Hunter live sichtbar. Wer zu lange draußen bleibt, scheidet aus.</p>",
    "hider_draussen", "Hider außerhalb der Zone", 34)
))

KURZ.append(page("c-ping", "Teil 1 · Die erste Runde", "Der Ping",
    side(f"<p>{PING_TXT}</p><p>Oben rechts läuft die Zeit bis zum nächsten Ping.</p>",
    "hunter_ping", "Ansicht eines Hunters nach einem Ping", 34)
))

KURZ.append(page("c-catch", "Teil 1 · Die erste Runde", "Fangen",
    "<p>Der Hunter berührt den Hider und tippt <b>Fang melden</b>. Die beiden Handys dürfen dabei höchstens 40&nbsp;m auseinander sein.</p>"
    "<p>Der Hider bestätigt den Fang. Antwortet er nicht, gilt er nach 30&nbsp;Sekunden automatisch. Wer gefangen ist, schaut als Zuschauer weiter zu.</p>" +
    fig("ux_fang_alarm", "Die Fangmeldung beim Hider", 54)
))

KURZ.append(page("c-start", "Teil 1 · Die erste Runde", "Vor dem Start",
    steps(["<b>Der Host</b> erstellt das Spiel und teilt den Link.",
           "<b>Alle anderen</b> öffnen den Link und wählen eine Seite.",
           "<b>Nach dem Start</b> laufen die Hider los. Die Hunter warten den Vorsprung ab."]) +
    '<h3 class="mini">Am Handy</h3>' +
    checklist([
        "<b>Android:</b> Blown-Cover-App installieren. Der Bildschirm darf aus sein.",
        "<b>iPhone:</b> Seite offen und Bildschirm an lassen.",
        "WLAN aus, mobile Daten an, Energiesparmodus aus",
        "Standort auf „genau“, Akku voll, Powerbank einpacken",
    ]) +
    note("Auf den Verkehr achten und keine Privatgrundstücke betreten.")
))

KURZ.append(page("c-task", "Teil 2 · Aufgaben, Boni, Modi", "Aufgaben für Hider",
    "<p>Aufgaben sind freiwillig und bringen Vorteile.</p>" +
    item("Safehouse", "Zwei Plätze. Wer zuerst eincheckt, bekommt Immunität, der Zweite die halbe Zeit.", "t_sh") +
    item("Dead Drop", "Einer legt ein Dossier ab, ein anderer holt es. Jeder bekommt einen Bonus.", "t_dd") +
    item("Meeting", "Zwei Hider machen im Chat einen Treffpunkt aus und treffen sich dort. Jeder wählt vorher einen Bonus.", "t_mt") +
    fig("hider_panel", "Aufgaben im Panel eines Hiders", 44)
))

KURZ.append(page("c-bonus", "Teil 2 · Aufgaben, Boni, Modi", "Boni",
    '<div class="split"><div class="col hider-c"><h3>Hider</h3>' +
    item("Immunität", "Bei keinem Ping sichtbar. Fangen ist trotzdem möglich.") +
    item("Satellitenbild", "Alle Hunter 60&nbsp;s auf der Karte.") +
    item("Hunter-Radar", "Zählt die Hunter in deiner Nähe.") +
    '</div><div class="col hunter-c"><h3>Hunter</h3>' +
    item("Live-Standort", "Nach einem Fang: einen Hider kurz live verfolgen.") +
    item("Extra-Ping", "Nach einem Fang: sofort alle Hider orten.") +
    item("Hider-Radar", "Zur Halbzeit: zählt die Hider in deiner Nähe.") +
    '</div></div>' +
    fig("hunter_bonus", "Bonuswahl nach einem Fang", 42)
))

KURZ.append(page("c-modes", "Teil 2 · Aufgaben, Boni, Modi", "Modi und Extras",
    item("Untertauchen", "Das Grundspiel. Es reicht, bis zum Ende frei zu bleiben.") +
    item("Mission", "Die Hider müssen alle Dead Drops und Meetings erledigen und am Ende einen Abholpunkt erreichen.") +
    item("Zombie", "Wer gefangen wird, jagt ab dann selbst mit.") +
    item("Kopfgeld", "Mehrere Hunter-Teams jagen dieselben Hider und spielen gegeneinander.") +
    item("Terminal", "Hider hacken in einer Zone, die die Hunter kennen. Gelingt es, sehen sie die Hunter kurz live. Scheitert es, bekommen die Hunter ein Sperrgebiet.") +
    note("Was gespielt wird, stellt der Host in der Lobby ein. Im Spiel erklärt der Knopf ⓘ alle Kartensymbole.")
))

# =====================================================================
# VOLLVERSION
# =====================================================================
V = [cover("Spielregeln", LEAD,
    [("Grundspiel", "2–10"), ("Aufgaben und Boni", "11–19"), ("Zombie und Kopfgeld", "20–23"), ("Weitere Einstellungen", "24–25"), ("Karte, Vorbereitung, Werte", "26–28")],
    "AZ BC-26 · V")]

G = "Grundspiel"
V.append(page("c-roles", G, "Zwei Seiten",
    role("hider", "Hider", "Bis zum Ende der Zeit frei bleiben.", [
        "Bleib in der roten Zone.",
        "Bleib in Bewegung. Bei jedem Ping sehen die Hunter, wo du gerade stehst.",
        "Erledige Aufgaben, um dir Schutz oder Vorteile zu holen.",
    ]) +
    role("hunter", "Hunter", "Alle Hider fangen, bevor die Zeit abläuft.", [
        "Zu Beginn haben die Hider einen Vorsprung und sind nicht zu orten.",
        "Danach zeigen Pings, wo die Hider waren. Sie laufen aber weiter.",
        "Nach jedem Fang bekommst du einen Bonus.",
    ])
))

V.append(page("c-win", G, "Wer gewinnt?",
    '<div class="winbox hunter-w"><h3>Die Hunter gewinnen,</h3><p>wenn alle Hider gefangen sind oder ausgeschieden (aufgegeben, disqualifiziert).</p></div>'
    '<div class="winbox hider-w"><h3>Die Hider gewinnen,</h3><p>wenn die Zeit abläuft oder alle Hunter ausgeschieden sind.</p></div>'
    '<h3 class="mini">Abweichungen je nach Modus</h3>' +
    kv([("Mission", "Die Hider gewinnen nur, wenn zusätzlich alle Dead Drops und Meetings erledigt sind."),
        ("Zombie", "Wer bei Zeitende frei ist, gewinnt. Sind alle verwandelt, gewinnen die Zombies sofort."),
        ("Kopfgeld", "Jeder Hider, der am Ende frei ist, gewinnt. Bei den Huntern gewinnt das Team mit den meisten Fängen.")])
))

V.append(page("c-start", G, "Ablauf einer Runde",
    steps(["<b>Erstellen.</b> Der Host legt die Zone auf der Karte fest und wählt Dauer, Modus und Aufgaben.",
           "<b>Beitreten.</b> Alle öffnen den Einladungslink oder geben den Spielcode ein und wählen eine Seite. Der Host kann die Seiten auch auslosen.",
           "<b>Vorsprung.</b> Jeder bekommt sein Briefing. Die Hider verstecken sich (Standard 5&nbsp;Min). Erst danach beginnen Zone und Pings.",
           "<b>Jagd.</b> Die Zone schrumpft, Pings kommen, Aufgaben erscheinen.",
           "<b>Ende.</b> Das Ergebnis zeigt Fänge, Aufgaben und den Ausgang der Operation."]) +
    note("Wer erst nach dem Start beitritt, schaut als Zuschauer zu.")
))

V.append(page("c-start", G, "Lobby und Briefing",
    "<p>In der Lobby sieht jeder, wer auf welcher Seite steht. Beim Start öffnet sich das Briefing mit dem Namen der Operation und den Aufgaben dieser Runde. Der Knopf <b>Briefing</b> im Panel öffnet es später wieder.</p>" +
    pair(("ux_lobby", "Lobby"), ("briefing_hider", "Briefing der Hider"))
))

V.append(page("c-zone", G, "Die Zone",
    "<p>Der rote Kreis ist das Spielfeld, alle Hider müssen darin bleiben. In festen Abständen wird er kleiner (Standard alle 4&nbsp;Min um 55&nbsp;m), bis er seinen Mindestradius erreicht. Der grau gestrichelte Kreis zeigt die nächste Größe.</p>" +
    side("<h3 class='mini'>Wer hinausgeht,</h3>" + dash([
        "ist für alle Hunter live sichtbar,",
        "bleibt nach der Rückkehr noch 2&nbsp;Min sichtbar,",
        "darf insgesamt nur 5&nbsp;Min draußen sein. Danach scheidet er aus. Eine Minute vorher warnt die App."]),
        "hider_draussen", "Hider außerhalb der Zone", 34)
))

V.append(page("c-ping", G, "Der Ping",
    f"<p>{PING_TXT} Antippen zeigt, wie lange der Ping her ist.</p>" +
    side("<p>Standardmäßig kommt alle 3&nbsp;Min ein Ping. Der Countdown steht oben rechts, die Hider sehen ihn auch.</p>"
         "<p>Die Hider bekommen bei jedem Ping eine Meldung.</p>",
         "hunter_ping", "Vier Hider beim letzten Ping", 34)
))

V.append(page("c-ping", G, "Was Hider sehen",
    side("<p>Hider sehen ihren eigenen letzten Ping als größeren Kreis und wissen so, was die Hunter von ihnen wissen.</p>"
         "<p>Bei jedem Ping sehen sie auch die Positionen ihrer Mitspieler. Der Host kann das in der Lobby abschalten.</p>",
         "hider_karte", "Ansicht eines Hiders", 36) +
    note("Kein Ping für Hider mit Immunität oder beim Hacken. Wer ohnehin gerade live sichtbar ist, bekommt keinen zusätzlichen.")
))

V.append(page("c-catch", G, "Fangen",
    steps(["Der Hunter berührt den Hider, tippt <b>Fang melden</b> und wählt ihn aus. Die Handys dürfen höchstens 40&nbsp;m auseinander sein.",
           "Beim Hider erscheint ein Alarm. Er bestätigt mit <b>Ja, erwischt</b> oder lehnt ab. Antwortet er nicht, gilt der Fang nach 30&nbsp;s."]) +
    pair(("fang_melden", "Beim Hunter"), ("ux_fang_alarm", "Beim Hider"))
))

V.append(page("c-catch", G, "Nach dem Fang",
    side("<p>Der Gefangene scheidet aus und schaut als Zuschauer weiter zu. Der Fangort bleibt für die Hunter als rotes Handschellen-Symbol auf der Karte, und der Hunter bekommt einen Bonus.</p>"
    "<p>Liegen die Positionen zu weit auseinander oder sind sie nicht aktuell, lehnt die App den Fang ab.</p>",
    "ux_ende", "Ergebnis am Ende einer Runde", 33) +
    note("Die App ersetzt keinen Schiedsrichter. Wer geschummelt hat oder sich unwohl fühlt, sagt es.")
))

A = "Aufgaben und Boni"
V.append(page("c-modes", A, "Vier Modi",
    '<div class="modes">'
    '<div class="mode"><h4>Untertauchen</h4><p>Das Grundspiel. Die Hider müssen nur durchhalten, Aufgaben und Boni sind freiwillig.</p></div>'
    '<div class="mode"><h4>Mission</h4><p>Dead Drops und Meetings sind Pflicht. Ein Safehouse gibt es nicht, dafür am Ende die Evakuierung.</p></div>'
    '<div class="mode"><h4>Zombie</h4><p>Gefangene werden selbst zu Jägern. <span class="ref">S.&nbsp;20</span></p></div>'
    '<div class="mode"><h4>Kopfgeld</h4><p>Mehrere Hunter-Teams jagen dieselben Hider. <span class="ref">S.&nbsp;22</span></p></div>'
    '</div>'
))

V.append(page("c-task", A, "Aufgaben für Hider",
    "<p>Aufgaben erscheinen im Lauf der Runde im Panel. Safehouse, Dead Drop und Evakuierung haben einen festen Ort, der als lila Quadrat mit einem Kreis von 40&nbsp;m auf der Karte liegt. Den Treffpunkt für ein Meeting legen die beiden Hider selbst fest.</p>" +
    fig("hider_panel", "Aufgaben im Panel eines Hiders", 62) +
    note("Dead Drops und Meetings brauchen je zwei Hider. Fällt ein Partner aus, übernimmt ein Hider ohne Aufgabe.")
))

V.append(page("c-task", A, "Safehouse und Dead Drop",
    item("Safehouse", "Erscheint nach etwa einem Drittel der Zeit (Standard Minute 20). Es gibt zwei Plätze: Wer zuerst eincheckt, bekommt 3&nbsp;Min Immunität, der Zweite die Hälfte. Passt der Ort nicht, wählen alle Hider „Ort unpassend“, dann wechselt er.", "t_sh") +
    item("Dead Drop", "Ein Hider legt ein Dossier am markierten Ort ab, ein zweiter holt es ab. Darin liegen ein Satellitenbild und ein Hunter-Radar. Wer ablegt, bekommt sofort eines davon per Zufall, wer abholt, das andere.", "t_dd")
))

V.append(page("c-task", A, "Meeting und Evakuierung",
    item("Meeting", "Zwei Hider machen im privaten Chat einen Treffpunkt aus. Sobald sie höchstens 40&nbsp;m auseinander sind, bestätigen beide das Treffen. Vorher wählt jeder seine Belohnung: Hunter-Radar oder Satellitenbild, aber nicht beide dasselbe.", "t_mt") +
    item("Evakuierung", "Nur im Modus Mission, in den letzten Minuten (Standard 8): Wer den Abholpunkt erreicht und bestätigt, ist in Sicherheit.", "t_ev") +
    note("Die festen Orte liegen im Bereich der drittletzten Zone, gegen Ende also möglicherweise knapp außerhalb. Nur die Evakuierung liegt immer in der kleinsten Zone.")
))

V.append(page("c-term", A, "Das Terminal",
    "<p>Eine freiwillige Aufgabe mit hohem Risiko, die der Host unter „Aufgaben“ einschaltet. Die Hunter kennen die Terminal-Zone von Anfang an, die Hider erst, wenn sie aktiv wird (Standard ab Minute 17).</p>" +
    item("Hacken", "Wer in der Zone ist, tippt „Hacken starten“. Allein dauert es 4:30&nbsp;Min, mit mindestens einem Helfer 50&nbsp;% kürzer. Alle sehen den Fortschritt, auch die Hunter.", "t_hk") +
    item("Während des Hacks", "Hacker sind nicht ortbar, laufende Immunität endet. Wer die Zone verlässt, hat 10&nbsp;s für die Rückkehr. Danach scheidet er aus dem Hack aus und wird zur Strafe live geortet.") +
    note("Verlässt der letzte Hacker die Zone, ist der Versuch abgebrochen. Es gibt drei Versuche.")
))

V.append(page("c-term", A, "Gehackt oder verteidigt",
    '<div class="winbox hider-w"><h3>Gehackt</h3><p>Alle beteiligten Hider bekommen 1:30&nbsp;Min Immunität. Dazu kommt die <b>Gegenüberwachung</b>: Wenn der Hacker sie einsetzt, sehen alle Hider die Hunter 90&nbsp;s lang live. Die Hunter werden gewarnt.</p></div>'
    '<div class="winbox hunter-w"><h3>Verteidigt</h3><p>Alle Hacker gefangen oder drei Versuche abgebrochen: Ein Hunter bekommt das <b>Sperrgebiet</b>.</p></div>' +
    item("Sperrgebiet", "Der Inhaber legt einen Kreis von 135&nbsp;m in die Zone. Nach 45&nbsp;s Vorwarnung wird jeder Hider darin live angezeigt, so lange wie ein Hack dauert. Wer hinausgeht, ist sofort wieder unsichtbar.", "oz")
))

V.append(page("c-bonus", A, "Boni für Hider",
    item("Immunität", "Aus dem Safehouse oder nach einem Hack. Du tauchst bei keinem Ping auf und kannst nicht live geortet werden. Dein Marker hat dann einen goldenen Ring. Fangen kann man dich trotzdem.", "immun") +
    item("Satellitenbild", "Aus Meeting oder Dead Drop. Alle Hunter erscheinen 60&nbsp;s lang auf deiner Karte.") +
    item("Hunter-Radar", "Aus Meeting oder Dead Drop. Zeigt ein Ping-Intervall lang als Zahl, wie viele Hunter im Umkreis sind (Standard 180&nbsp;m). Keine Richtung, keine Positionen. Die Hunter merken nichts davon.", "radar")
))

V.append(page("c-bonus", A, "Das Radar",
    side("<p>Solange niemand in der Nähe ist, dreht sich eine Nadel im grünen Kreis. Kommt ein Gegner in den Umkreis, pulsiert der Kreis, oben erscheint die Zahl und das Handy vibriert.</p>"
         "<p>Hunter bekommen das Gegenstück, das <b>Hider-Radar</b>, zur Halbzeit. Immune und hackende Hider zählt es nicht.</p>",
         "radar_kontakt", "Hunter-Radar mit Kontakt", 34)
))

V.append(page("c-bonus", A, "Boni für Hunter",
    "<p>Nach jedem Fang wählst du einen Bonus. Einsetzen kannst du ihn nach einer Wartezeit von 1:30&nbsp;Min.</p>" +
    item("Live-Standort", "Du verfolgst einen Hider 70&nbsp;s lang live. Er bekommt eine Meldung.", "live") +
    item("Extra-Ping", "Sofort alle Hider orten, sichtbar als Doppelring. Die Hider erfahren davon.", "xping") +
    fig("hunter_bonus", "Bonuswahl nach einem Fang", 44) +
    "<p class='small'>Höchstens zwei Boni gleichzeitig. Ist der Vorrat voll, tauschst du einen oder lässt den neuen verfallen.</p>"
))

Z = "Zombie und Kopfgeld"
V.append(page("c-zombie", Z, "Zombie-Modus",
    "<p>Wer gefangen wird, scheidet nicht aus, sondern wird zum <b>Zombie</b> und jagt mit. In der App heißen die Hunter in diesem Modus überall Zombies.</p>" +
    side(dash(["Der Gefangene bleibt 60&nbsp;s im grünen Kreis um den Fangort. Verlässt er ihn, beginnt es von vorn.",
               "Erst danach darf er fangen."]),
         "zombie_verwandlung", "Verwandlung läuft", 36) +
    note("Wer aufgibt oder disqualifiziert wird, wird kein Zombie.")
))

V.append(page("c-zombie", Z, "Die Horde wächst",
    item("Ping", "Je mehr Zombies und je weniger Hider, desto seltener der Ping, höchstens dreimal so selten wie zu Beginn. Abschaltbar.") +
    item("Zone", "Der Mindestradius ist größer, damit die letzten Hider Platz haben.") +
    item("Zeitbonus", "Das Hider-Radar bekommen nur Zombies, die zur Halbzeit schon verwandelt sind.") +
    item("Ende", "Wer bei Zeitende frei ist, gewinnt. Sind alle verwandelt, gewinnen die Zombies sofort. Das Ergebnis zeigt eine Rangliste nach Überlebenszeit.") +
    item("Kennzeichen", "Verwandelte Spieler tragen einen grünen Punkt am Dreieck.", "zombie")
))

V.append(page("c-kopf", Z, "Kopfgeld",
    "<p>Für große Gruppen: Zwei bis vier Hunter-Teams („Agenturen“) jagen dieselben Hider, jedes Team für sich. Die Hider spielen einzeln ums Überleben.</p>" +
    side(kv([("Teams", "Wer zuerst beitritt, ist Teamchef und wählt Name und Farbe."),
             ("Sicht", "Jedes Team sieht nur die eigenen Leute, Markierungen und Chat."),
             ("Wertung", "Ein Fang zählt für das Team des Hunters, der ihn meldet.")]),
         "kopfgeld_lobby", "Agenturen in der Lobby", 33)
))

V.append(page("c-kopf", Z, "Pings, Boni, Informanten",
    "<p>Pings kommen für alle Teams gleichzeitig. Extra-Ping, Live-Standort, Radar und Sperrgebiet wirken nur für das eigene Team. Es gewinnt das Team mit den meisten Fängen, bei Gleichstand das mit dem früheren letzten Fang.</p>"
    "<p>Zwischen 20&nbsp;% und 80&nbsp;% der Spielzeit tauchen <b>Informanten</b> auf, die nur Hunter sehen. Wer als Erster bis auf 30&nbsp;m herankommt, bekommt einen davon:</p>" +
    item("Abhören", "Dein Team sieht 1:30&nbsp;Min lang die Hunter der anderen Teams live.", "inf") +
    item("Störsender", "Der nächste Ping eines anderen Teams kommt 1:30&nbsp;Min später. Es erfährt nicht, von wem.")
))

E = "Weitere Einstellungen"
V.append(page("c-switch", E, "Auslosen und Festsetzen",
    item("Teams auslosen", "Der Host stellt nur ein, wie viele Hunter (oder Zombies, Teams) es gibt. Die App lost beim Start aus, jeder erfährt seine Rolle im Briefing.") +
    side("<h4>Festsetzen</h4><p>Für Gruppen ohne Verfolgungsjagd. Der Hunter tippt <b>Festsetzen</b> und wählt einen Hider, den er sieht. Ist der höchstens 40&nbsp;m entfernt, muss er 40&nbsp;s stehen bleiben, und jeder Hunter darf ihn fangen.</p>"
         "<p>Gelingt in der Zeit kein Fang, bekommt der Hider halbe Immunität und sieht den Hunter so lange live.</p>",
         "fs_hider_alarm", "Beim festgesetzten Hider", 32)
))

V.append(page("c-switch", E, "Kompromittierung und Signal",
    item("Kompromittierung", "Fällt ein Partner durch einen Fang aus und ist kein Hider mehr frei, sehen die Hunter, wo die Aufgabe erledigt werden muss (magenta). Bei einem Meeting legt die App dafür einen Ort fest. Der Übriggebliebene kann sie allein erledigen und behält die Belohnung. Ohne diese Einstellung verfällt die Aufgabe.", "t_ddc") +
    item("Signalverlust", "Ohne GPS oder Internet warnt die App nach etwa 20&nbsp;s. Ausscheiden muss deshalb nur, wer die Disqualifikation eingeschaltet hat: Dann nach 60&nbsp;s ohne Signal.") +
    item("Balancing", "Die Standardwerte passen für 2 Hunter gegen 4 Hider. Für jede andere Besetzung rechnet die App Zone, Pings, Boni und Aufgaben so um, dass beide Seiten etwa gleich oft gewinnen.")
))

K = "Karte, Vorbereitung, Werte"
V.append(page("c-map", K, "Kartensymbole",
    symgrid([("hider", "Hider", "Kreis, Farbe und Buchstabe"), ("hunter", "Hunter", "Dreieck"),
             ("me", "Du", "blauer Ring"), ("pingme", "Dein letzter Ping", "so sahen dich die Hunter"),
             ("live", "Live sichtbar", "pulsierender Ring"), ("immun", "Immun", "goldener Ring"),
             ("xping", "Extra-Ping", "Doppelring"), ("stale", "Nicht aktuell", "grau gestrichelt"),
             ("next", "Nächste Zone", "grau gestrichelt"), ("catch", "Fangort", "Handschellen"),
             ("t_sh", "Aufgabe", "lila Quadrat"), ("t_ddc", "Kompromittiert", "magenta"),
             ("radar", "Radar", "nur für dich"), ("zombie", "Zombie", "grüner Punkt")]) +
    note("Ein Ping sieht aus wie der Hider-Marker. Im Spiel zeigt der Knopf ⓘ genau die Symbole, die gerade vorkommen.")
))

V.append(page("c-start", K, "Vor dem Spiel",
    checklist([
        "<b>Android:</b> Blown-Cover-App. Der Bildschirm darf aus sein, Meldungen kommen als Benachrichtigung.",
        "<b>iPhone und Browser:</b> Seite offen und Bildschirm an lassen. Gesperrt bleibt das Spiel stehen.",
        "WLAN aus, mobile Daten an",
        "Energiesparmodus aus, Standort auf „genau“",
        "Akku voll, Powerbank einpacken",
        "Draußen spielen. In Gebäuden ist GPS ungenau.",
    ]) +
    '<h3 class="mini">Sicherheit</h3>' +
    dash(["Laufen ist erlaubt, Straßen blind überqueren nicht.",
          "Nur öffentliche Wege, keine Privatgrundstücke oder gesperrten Bereiche."])
))

V.append(page("c-values", K, "Standardwerte",
    '<p class="small">Für 60&nbsp;Min und 2 Hunter gegen 4 Hider. Alle Werte lassen sich in der Lobby ändern; kürzere Runden haben kleinere Zonen und kürzere Abstände.</p>' +
    kv([("Startzone", "900&nbsp;m Radius, mindestens 400&nbsp;m"),
        ("Schrumpfen", "alle 4&nbsp;Min um 55&nbsp;m"),
        ("Vorsprung", "5&nbsp;Min"),
        ("Ping", "alle 3&nbsp;Min"),
        ("Außerhalb", "höchstens 5&nbsp;Min, danach 2&nbsp;Min sichtbar"),
        ("Aufgaben", "Dead Drop ab Minute 8, Meeting ab 15, Safehouse ab 20"),
        ("Immunität", "3&nbsp;Min (Safehouse, erster Platz)"),
        ("Fang", "höchstens 40&nbsp;m, Bestätigung 30&nbsp;s"),
        ("Hunter-Boni", "Wartezeit 1:30&nbsp;Min, Live-Standort 70&nbsp;s"),
        ("Radar", "180&nbsp;m, 3&nbsp;Min lang")])
))
