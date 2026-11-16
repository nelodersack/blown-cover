# Blown Cover – Arbeitsanleitung für Claude

IRL-Versteckspiel (Hunter gegen Hider, schrumpfende GPS-Zone, Pings, Aufgaben). Die gesamte Web-App steckt in **`index.html`** (≈210 KB, Leaflet + Firebase Realtime DB europe-west1). `main` ist über GitHub Pages live unter der eigenen Domain **https://blowncover.app/** (Namecheap-DNS, Datei `CNAME` in `main` nicht löschen; die alte Adresse https://nelodersack.github.io/blown-cover/ leitet dorthin weiter). Die Android-App (Zweig `android-app`) ist eine WebView-Hülle und lädt die Live-Seite. Website-Änderungen brauchen deshalb keine neue APK, außer die Bridge `BlownNative` oder Java-Code ändert sich.
Mit Manuel auf Deutsch sprechen, knapp und direkt.

## Sparsam lesen (wichtig)
- **`index.html` nie ganz lesen.** Erst `grep -n "§" index.html` ausführen (Abschnittsmarken mit Zeilennummern), dann mit `Read` und `offset`/`limit` nur den Abschnitt lesen.
- Funktionen findest du mit `grep -n "function name\|const name=" index.html`. Viele Zeilen sind lang und dicht: lieber `grep -o ".\{80\}stichwort.\{120\}"` als ganze Zeilen.
- Historie und Begründungen stehen in `CHANGELOG.md`. Nur lesen, wenn es nötig ist.
- Der Projektstand für andere Chats liegt im claude.ai-Projekt „Blown Cover“: `claude/UEBERGABE_App.md` (kurz). Konzepte: `claude/KONZEPT_Hacking.md`, `KONZEPT_Balancing.md`, `KONZEPT_Zombie.md`.

## Codekarte (`grep -n "§" index.html`)
CSS: `§CSS-BASIS` (Tokens `--ac` Aktionsfarbe nur für Hauptknöpfe/Logo, `--task` lila, `--cmp` magenta = kompromittierte Aufgabe, `--danger`, `--ok`, `--xping`), `§CSS-ELEMENTE`, `§CSS-KOMPONENTEN` (card, chip, acc, `.fl`/`.fl.sub`, num, sw), `§CSS-OVERLAYS`, `§CSS-CHAT`, `§CSS-DIALOG`, `§CSS-REPLAY`, `§CSS-KNOEPFE`, `§CSS-SPIEL-PANEL`, `§CSS-TIPPEN` (Tipp-Rückmeldung: kein Browser-Aufleuchten, Knöpfe drücken sich ein), `§CSS-FANG` (Fang-Raster `.cgt`, Fang-Alarm `#fa`), `§CSS-FANG-STARTEN` („Festsetzen“: `.fsb`, `.fzh`, `#fz`), `§CSS-BEWEGUNG` (Einblenden von Fenstern/Alarmen/Meldungen; nur der bleibende Rahmen wird animiert), `§CSS-ZUSCHAUER` (`.zr`, `.zs` Aufgabe, `.zc` Bonus), `§CSS-EINST-SEITEN` (Klassen `mz*`), `§CSS-UPDATE` (`#upb`), `§CSS-REPLAY-LISTE` (`.rlr`), `§CSS-KLAR` (Designkonzept „Klar“ vom 15.11., überschreibt ältere Regeln: Reiter mit Unterstrich, Leisten `.seg`/`.pre`/`.tiles.t3`, Listenzeilen `.lrw`, Lobby `.lhd`/`.lp`, Start `.logo2`; eine Aktionsfarbe `--ac`, keine Code-Schrift, Überschriften normal geschrieben). `§HTML` Grundgerüst.
JS in Dateireihenfolge:
| Marke | Inhalt / wichtige Namen |
|---|---|
| §INIT | Firebase-Config, `NB` (App-Bridge), `TEST` (`#test` im URL-Hash), `LS` |
| §ANALYSE / §ANALYSE-DATEI | Protokoll `lg()`, `AL`; Analyse-JSON `anBuild`, `anDl`, `wfHarmless` |
| §APP | Sichtbarkeit, Fehler-Hooks, `bcSetHidden` |
| §STATE | globale `let`s (G, uid, code, pos, ping, …), `now()` (Serverzeit), `$`, `esc`, `D` (Distanz m), `P()` (Spieler), `gwE`, `dqOn`, `hpOn`, `evW`, `note` |
| §ERGEBNIS | `CW`, `catchWhy`, `buildRes` (inkl. `tk` Aufgabenbilanz, Spielerfarben), `resHTML` (Kacheln, zwei Spalten), `rpView` (Replay direkt aus dem Endscreen; solange `RV` läuft, ruhen `panel`/`draw`/HUD/`resSync`), `resSync` |
| §ZONE-AUFGABEN-RECHNUNG | `rs` (Ende Headstart), `Rad(g,t)`, `zoneSeq`, `md(g)` (Modus: survive|mission|zombie), `zmb(g)`, `HN`/`HNP` (Hunter/Zombie), `zx(html)` (ersetzt im Zombie-Modus übrige „Hunter“-Texte an den Ausgabestellen Panel/Anzeige/Meldung/Fenster/Legende/Popup; body-Klassen `zm`/`zmh` färben grün), Ping `zIv`/`pgK`, `ddPlan` (Kompromittierung `s.tsol`: Partner gefangen → `sol` + `cmp` = Ort für Hunter sichtbar, `cmpIds`; Belohnung allein `solRw`), Boni `hb*`, `myTk`, `myItems`, Orte `ovPts`/`randPts`/`mkPts` |
| §UI-BASIS | `toast` (stapelt höchstens zwei Meldungen in `#toast`), Icons `SV`/`ic()`, Farben `PAL`/`colOf`, Markerformen `shape`/`shape0`, `TH`, Wake Lock |
| §KARTE, §KARTE-DREHEN, §AUSRICHTUNG, §GESTEN, §KOMPASS | `map`, `rotSize`, `fitZ`, `FM`/`FA`, `nbTap`, `nbFit` (Kompass aus, solange das Panel ihn verdeckt), Gesten `g*` (Finger in `tps`; Geisterfinger-Schutz `gReset`/`gTouch`, weil iOS pointerup verliert), Blickrichtung `HD`, `crs` |
| §KARTENSTIL | Vorschau `?kartenstil=1…5` (Positron, Untergrundflächen um `KSU` dunkler, Nebenstraßen/Wege weiß, fünf Gebäudefarben): `KST`, `KSN`, `KSD` (Name `n`, Gebäude `b`), `KSL` (betroffene Ebenen), `ksDk`, `ksApply(style,T)`, `KZ` (Zonenfarben, Maske außerhalb der Zone möglich über `mo`), `ksBadge` (Schild `#ksb`, CSS `§CSS-KARTENSTIL`) |
| §REPLAY-AUFNAHME | `RP`, `rpLog`, `rpSnap`, `rpBuild`, `rpDl` |
| §REPLAY-LISTE | Liste der Replays. App (Bridge `NB.replays()`/`NB.readReplay(id)` ab v0.3.7): gespeicherte Dateien, je Code+Runde nur die neueste; Browser: „Zuletzt abgespielt“ in IndexedDB (`rlDb`, `rlReq`, `rlIdbPut`, DB `blowncover` mit `meta`/`data`, `RLMAX` 30; nie in der App). `RL` (on, items, src app/idb), `rlCan`, `rlIdbOk`, `rlOpen` (ohne beides → `rvPick`), `rlSum`, `rlFill` (App: liest nacheinander, Cache `LS.rlS`), `rlRow` (Gewinnerform, sonst „Abgebrochen“/„Beendet“; Dauer gespielt / geplant)/`rlHTML`, `rlPlay`. Speichern nach der Runde: `rpSave(f,hand)` (Datei per `rpDl` – App Dokumente, Browser Downloads – nur bei mehr Wegen, Merker `LS rpS:<code>_<rn>`; Browser zusätzlich IndexedDB), aufgerufen von `rpView` und dem Knopf „Als Datei speichern“. CSS `§CSS-REPLAY-LISTE` |
| §REPLAY | `rv*`: `rvFit(anim)`/`rvFocus(…,anim)` (Karte gleitet beim Öffnen zur Zone; `rvPre` lädt die Vektorkacheln am Ziel vor, `#map.fly` blendet Markierungen während des Flugs aus), Zonenstriche der Zeitleiste `.rvzs` (nicht `.zs`, das ist Zuschauer), `rvConv`, `rvScan` (Ereignisse), `rvStats`, `rvDraw`, `rvTaskShow`, `rvPanel`; Zeitleiste „Lupe“: `rvWin`/`rvWA` (Ausschnitt), `rvDrag` (Detailspur, Schwung `RV.fl`; Spurbreite gecacht in `RV.cw` – in `rvDraw` nie Layout lesen), `rvScrub` (Übersicht), Filter `rvHide`/`rvVis`; Radar-Kreise `rvBm`; Spuren `RV.tr` short/all über `rvTr` (`RVTR` = 5 Min); Rolle zur Zeit t `rvRole(p,t)` (Zombie), `RV.zt` |
| §GPS | `startGPS` (Sprungfilter `onFix0`/`jf` vor `onFix`: > 10 m/s erst nach Bestätigung, Protokoll `gj`), `write` |
| §JOIN | `mk` (Spiel erstellen), `jn`, `join` (Lobby → Hider; läuft schon → Zuschauer mit `role:'spec'`/`state:'spec'`, schreibt keinen Standort; vorbei → „Lobby ist bereits geschlossen“), `appReady`. Einladungslink `blowncover.app/CODE`: `404.html` leitet auf `?c=CODE`, `LINKC` (in §STATE gelesen) zeigt den Einladungs-Startbildschirm; `LINK(code)` für Teilen/Kopieren |
| §DIALOG | `dlg({t,x,…})` – alle Dialoge im App-Design, nie `alert/confirm`; Zusatzknöpfe `btns:[{l,v,bad,ic}]` (Ergebnis `v`), `ok:null` = nur Abbrechen |
| §FARBWAHL, §MARKER | Spielerfarbe; eigene Kartenmarker `mk*`, `drawMarks` |
| §LOBBY-AKTIONEN | `setRole`, `setS(k,v,min,max)` (rundet auf den Feldschritt), Spieler-Menü des Hosts `plMenu`/`kick`/`toHost`, `setMode` (`zoneFit`), Auslosen `rndOn`/`rndH`/`setRnd`, `giveUp`, `leaveGame`, `newRound`, Spielstart `st` |
| §FANG | Zombie: `zInf` (Verwandlung schreiben), `zTick`/`ZV`/`zLock` (Wartezeit am Fangort, `ZR` 30 m), `zLast`; `cc`, `rq` (keine Doppelmeldung, Hunter-Karte „Warte auf …“ im Panel), `ok`, `no`, Fang-Alarm `faSync` (Vollbild beim Hider), `fin`, `endNow` |
| §FANG-STARTEN | „Festsetzen“ (früher „Fang starten“, `s.fs`): Hunter `fsBtn`/`fsGo`/`fsCand`, Wartezeit `fsMine`/`fsWait`, Karte `fsHunterH`; Hider `fsTick` (stille Prüfung, `FSH`, Ergebnis nur in LS + `fzp/<code>/<uid>`), Vollbild `fsOv` (`#fz`, unter `#fa`), `fsStand`, Alarm `fsAlarm` (Vibration/Ton), Entkommen `FSX` (Hunter live) + Ping-Ausfall `fsSkip`/`pS`; Panel-Signatur `fsSig` |
| §AUFGABEN | Hunter-Boni `hb*` (Ortbarkeit `locatable`, Grund `locWhy`/`locMsg`), Meeting `mt*`, `chk`, Evakuierung `rv*`-Lock, `useImm`, `hTasks`, Zuschauer `specView` (Zeilen, `ui.specX`), Radar, `hInv` |
| §RADAR | Bonus Radar (Konzept `KONZEPT_Bewegungsmelder.md`): Hider `type:'bm'` = Hunter-Radar, Hunter `k:'bm'` = Hider-Radar (Zeitbonus). `bmRv`/`bmTv` (Radius/Dauer, 0 = auto), `ddBm` (Dead-Drop-Verteilung per Hash), `ITN` (Item-Name), `bmMine` (eigenes laufendes Radar; Hider-Start in `LS[bmKey(id)]`), `bmCount` (Hysterese +15 m), `bmTick` (HUD/Meldungen), `bmOv` (Sonar-Kreis als `L.svgOverlay`, CSS `.bmr`), Zustand `BM`. Der alte Hider-Bonus heißt in Texten „Satellitenbild“ (intern weiter `radar`/`rad`/`useRadar`) |
| §CHAT, §PANEL-ZIEHEN | Chat `ch*` (Lobby: nur Kanal `all` für alle, `chLobby()`, keine Privatnachrichten, Rolle neben dem Namen außer bei Auslosen; ab Spielstart Team + Privat), Schnellnachrichten `chQR` (passend zu laufenden Aufgaben, nur Team/Privat) + `chQSync`; Panel-Geste mit Stufen voll / Mitte `m` (Replay-Karte und Lobby-Einstellungen, Anker `pAnc`, `pMid`/`pMidSet`, CSS-Variablen `--mid` Versatz und `--pad` Scroll-Abstand am Ende von `#ps`, damit das Menü in der Mitte scrollbar bleibt; `pRO`/`pObs` vermessen bei späteren Größenänderungen neu) / eingeklappt `c`; `pVis` = sichtbare Panelhöhe |
| §EINSTELLUNGEN | `ui`, `DEF`, **`FD`** (Feld-Definitionen), `PRE` (je Dauer nur, was das Balancing nicht bestimmt), `preOf(d)` (Voreinstellung = Balancing für 2 Hunter/4 Hider, auch für ein neues Spiel), `setPre`, `setHk` |
| §BALANCING | `balCalc(s,H,X,k,pure)` (Konstanten und Begründung im Kommentar; Regler `BAL` Ping, `BALR` Radius), `balAcc`, `balGo` |
| §LOBBY-UI | `nf(k,sub)`, `swt(k,on,label,sub,sub?)`, `acc(id,icon,titel,zusammenfassung,inhalt,kurzwert?)` (Listenzeile; Antippen öffnet die Unterseite: `ui.sub`, `SUBP`, `subGo`), `grp(überschrift,sub,zeilen)`, `shCode`, `mmss` (Sekunden als m:ss), `lobbyUI` (Kopf mit Operationsname, Spieler als Zeilen `.lp` mit Form `SHP`, Einstellungsliste) |
| §BONI | Lobby-Bereich „Boni“: `bnDefs(g)` (alle Boni mit Seite, Herkunft, Wert, aktiv, Feldern), `bnAcc` (Kacheln), Fenster `#bnd` über `bnShow(k)`/`bnSync()` (aus `panel()` aufgerufen)/`bnClose`, `nfl(k,label,sub)` = `nf` mit eigener Beschriftung |
| §EINST-SEITEN | Unterseiten der Einstellungen: `pgZone`, `pgZeit`, `pgTasks`, `pgBon`, `pgZmb` (Balancing in `balAcc`); Bausteine `chp(k)` (antippbarer Wert, offen in `ui.ed`), `pop(k,hinweis,immer)` (großer Regler mit Eingabe), `big(k)`, `card`, `fv` (Wert mit Einheit), `sv_`. **Neue Einstellung:** hier einen Platz geben; Test `einstellungen_vollstaendig` prüft das |
| §SPIEL-PANEL | Panel im Spiel: Hider `gBonH` (Bonus-Knöpfe aus `gItems`) + `gTaskH` (Auftragszeilen aus `gTasks`, `gRow`), Hunter `gBonHu`; Fenster `#gd` mit `gdShow(k)`/`gdSync()` (aus `panel()`)/`gdClose`, Schlüssel `bi:<item>`, `t:<task>`, `hk:<token>`, `hi:<hb-id>`, `hr`; Meeting-Wahl `gdMeet` (`mtSel`) |
| §RUN-UI, §PANEL | `LOGO`, `SHP(hunter,farbe)` (Form wie auf der Karte), `runUI`, `panel(force)` (Hülle um `panel0`: Höhenwechsel gleiten 0,25 s, Zielhöhe in `#panel._h1`, die `pMid` nutzt; `panel0` rendert nur bei geänderter Signatur `lastSig`; keine Zeit-Takte in die Signatur – Countdowns mit `cdT(ende,präfix)`, aktualisiert von `cdTick`, sonst springt am iPhone das Scrollen). Aufbau: `#panel` > `#ph` (Griff) + `#ps` (Scrollbereich) > `#pb` (Inhalt) + `#pf` (Knöpfe, scrollen mit) |
| §BRIEFING | Missionsbriefing: `bfName(code,rn)` (Operationsname), `bfData(g,code)` (beide Fassungen, feste Texte; nur der Name kommt deterministisch aus code+rn über `bfRng`), `bfShow`/`bfClose`/`bfAuto` (Dialog `#bfd`, Merker `LS[bfKey()]`), `bfRes` (Zeile im Endscreen), Knopf `.bfb` im Panel |
| §HACKING | (in Texten „Terminal“) `hkDef`, `hkSt`, `hkAct`, `hkProg`, `hkTick`, `hkJoin/Leave`, `hkCmUse`, `oz*`, `liveNow`, `hkHCard`, `hkHunterCard`, `hkDraw`, `hkSig` |
| §ZEICHNEN | `draw()` (alle Karten-Layer), `mkr` (Marker mit Popup), `tkInfo` (Aufgaben-Popup: Name + Belohnung, auch im Replay), Legende `LG` |
| §ONDATA | `onData()` nach jeder DB-Änderung |
| §TICK | `setInterval` 1 s: HUD, GPS-/Netz-Warnung, Zone, Pings, Fänge, Spielende |
| §UPDATE | App-Update über GitHub Releases: `APK` (feste Adresse `releases/latest/download/BlownCover.apk`), `REL` (API), `updCheck` (höchstens alle 3 h, Cache `LS.updC`; Release zählt nur mit Asset `BlownCover.apk`, Tag `vX.Y.Z` = versionName), `appVer()` (aus `NB.info()`), `verLt`, `updNew`, `updSync` (Kartenknopf `#upb` am Platz des Chat-Knopfs, nur Startbildschirm: App alt → mit orangem Punkt `.new`; Android-Browser → ohne Punkt; aus `panel()` aufgerufen), `updIn`/`updGo` (Bridge `NB.update(url)` lädt und installiert in der App selbst; Android-Browser → Intent-Link `updIntent()`: App öffnen, sonst APK laden); Dialog beim Öffnen der App nur auf dem Startbildschirm. `UPD` steht in §STATE. CSS `§CSS-UPDATE` |
| §BOOT | Anmeldung, Wiedereinstieg |

Eine neue Marke bekommt eine eigene Zeile `// §NAME kurze Beschreibung` (CSS: `/* §CSS-NAME */`). Die Tabelle oben dann mitpflegen.

## Datenmodell (Firebase)
- `games/$code`: `host`, `status` (lobby|running|over), `startAt`, `winner`, `c` {lat,lng} (Zonenmitte), `rn` (Rundennummer), `prev`, `chk`
  - `s` Einstellungen (siehe unten). `players/$uid`: name, role (hunter|hider|spec = Zuschauer per Link, nur im laufenden Spiel; neue Runde macht ihn zum Hider; `isPl(p)` = echte Spieler), state (alive|caught|dq|safe|…), lat, lng, ts, j, col, out, revealUntil, immUntil, used, sT, lf, w, oa; Zombie: zt (verwandelt), zs, zb (von wem), zl (Fangort), zd (Wartezeit fertig); pS (ausfallender Ping nach missglücktem „Fang starten“)
  - `catches/$hider` {hunter,t,status,why}, `hb/$hunter/$bonus`, `live/$hider/$hunter`, `xp/$id` (Extra-Ping), `fz/$hider` {h,t} („Fang starten“), `ev/$id` {t,x,u} (Meldungen an alle; `u:'hk'` = Hacking-System)
  - `tasks/$tid`: `sh` (Safehouse), `ev` (Evakuierung), Dead Drops/Meetings (`isDd(id)`; `sol` allein, `ex` verfallen, `cmp` Ort verraten), `hk` (Hacking: `t0`, `loc`, `rr:0`, `at/<n>` Versuche, `res`, `cm`, `oz`; `a` ist bei Dead Drop belegt, darum heißt der Versuchsknoten `at`)
- `fzp/$code/$uid` {t,ok,a}: Ergebnis „Fang starten“, nur für den Hider selbst lesbar
- `chats/…`, `marks/…`, `analysis/$code` (Analyse-Protokolle), `rp/$code/$uid` (Replay-Wege)
- **Regeln:** `database.rules.json` liegt im Zweig `db-rules` (`git show db-rules:database.rules.json`). Unter `s`, `players/$pid` usw. gilt `$o: false`: **jede neue Einstellung bzw. jedes neue Feld braucht eine Regel**, sonst schlägt das Schreiben fehl. Claude liefert Manuel immer die komplette Datei, Manuel lädt sie selbst hoch. Danach den Zweig `db-rules` aktualisieren.

## Einstellungen (`G.s`)
Zahlen stehen in `FD` als `key:[Label,min,max,Schritt,Einheit]`: rH, zT, zR, zC (Zombie, Menü `zAcc`), fsR, fsT (Fang starten), r0, rMin, shrink, step, ot, head, dur, ping, pen, gw, gd, shT, imm, ddN, ddT, mtN, mtT, taskR, evT, hbN, hbC, hbL, hbT, bmR, bmT, sbT, hkS, hkZ, hkT, hkR, hkN, ozR. Schalter: mode (survive|mission|zombie), rnd (Teams auslosen, Anzahl `rH`), zP, zB (Zombie), fs (Festsetzen), tsol (Kompromittierung), shOn, bon, hbOn, an (Analyse), dq, hp, rp, hk.
Eine neue Einstellung braucht: `FD` (oder Schalter), Standardwert (`DEF`/`PRE`/`hkDef`), Platz auf einer Unterseite in `§EINST-SEITEN` (`chp`/`pop`, `big` oder `swt`), DB-Regel `s/<key>`, ggf. `balCalc`.

## Konventionen
- Zeit immer über `now()` (Serverzeit-Offset), nicht `Date.now()` für Spielzeit.
- Jeder Client prüft gemeinsame Ereignisse selbst (Spielende, Fang-Timeout, Hacking-Versuchsende); das erste gültige Schreiben gewinnt, Locks wie `endLock` verhindern Doppel-Schreiben.
- `panel()` rendert nur bei geänderter Signatur neu. Neue Zustände, die das Panel ändern, gehören in die Signatur (z. B. `hkSig`).
- Aufgaben sind lila (`var(--task)` #7c6cff), Fang rot, Boni blau, Sichtbarkeit/Strafe orange (pulsierend).
- Testmodus `#test`: Positionen per Kartenklick, `sessionStorage`, keine Signal-DQ durch andere.

## Testen
- `sh dev/check.sh` prüft die JS-Syntax und führt alle Tests in `dev/tests/` aus. `sh dev/check.sh syntax` prüft nur die Syntax, `sh dev/check.sh replay` führt nur passende Tests aus.
- Die Tests laufen mit Playwright/Chromium (vorinstalliert) und `dev/memdb.js` als Firebase-Ersatz: `__T` ist die Datenbank, `notify()` löst die Listener aus. Vorlage für neue Tests: `dev/tests/hacking_mit_helfer.py` (Spiel in `__T.games` anlegen, `uid`/`pos` setzen, `join(code)`). Screenshots landen in `dev/out/` (nicht im Repo).
- **Regeln prüfen ohne Firebase:** `sh dev/rules.sh` (nimmt `db-rules`, oder eine Datei als Argument; `schnell` = nur feste Fälle). Wertet `database.rules.json` offline aus (targaryen): feste Fälle in `dev/rules/faelle.js` plus alle Schreibvorgänge, die die App in den Tests macht (`WLOG`-Protokoll aus `dev/memdb.js`, `dev/rules/replay.js`). Bei neuen Feldern/Regeln dort einen Fall ergänzen und vor dem Liefern laufen lassen.
- **Manuels Vorgabe (16.11.):** Vor einem Push nach `main` nicht alle Tests laufen lassen, nur die, die die Änderung betrifft (`sh dev/check.sh <stichwort>` oder einzelne Dateien in `dev/tests/`), plus `sh dev/check.sh syntax`. Den ganzen Lauf nur bei großen, querliegenden Änderungen.
- `dev/check.sh` endet mit „ALLE TESTS OK“; jeder Test muss mit der Zeile `errors: []` enden und Exit-Code 0 liefern.
- Firebase, github.io und blowncover.app sind aus der Cloud-Umgebung nicht erreichbar. Echte Tests macht Manuel auf dem Handy und schickt Analyse-JSON bzw. App-Logs.

## Regeln von Manuel
- **Nichts nach `main` ohne sein ausdrückliches Wort.** Erst auf einen Zweig pushen (mit `-u`), nach „Go“ per Fast-Forward auf `main`. Zweige löscht Manuel selbst.
- „Go“ vor Konzept-Features. Alle Dialoge im App-Design. Mockups aus echtem App-CSS. Das Design nur ändern, wenn er es will.
- **Nach jeder Repo-Änderung:** einen Eintrag in `CHANGELOG.md` anhängen und sofort `claude/UEBERGABE_App.md` im Projekt aktualisieren (Commit-Stand, Offen). Vorher die aktuelle Fassung lesen, weil andere Chats die Datei auch schreiben.
- APK bauen und auf dem Gerät testen macht Manuel. Kein Android-SDK in der Umgebung (javac gegen android.jar aus `Sable/android-platforms`).
- Commit-Nachrichten auf Deutsch.

## Website-Dateien
`404.html` (Einladungslink-Umleitung), `CNAME` (Domain), `_config.yml` (Jekyll: `dev/`, `CLAUDE.md`, `CHANGELOG.md` werden nicht veröffentlicht; `.well-known/` schon, für Android App Links). Neue Entwicklerdateien dort in `exclude` eintragen.

## Zweige
`main` (live), `android-app` (App, `android/`, Workflow baut APK als Artifact `BlownCover-APK`), `db-rules` (nur `database.rules.json`). Signaturschlüssel liegen nur in den GitHub-Secrets.
