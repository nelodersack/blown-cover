# Blown Cover – Android-App (Version 0.2.5)

Die App ist eine Hülle um die Website. Sie lädt die Seite in einem eingebetteten Browser und kann zusätzlich:
- den Standort im Hintergrund weiterlesen (Vordergrunddienst mit Benachrichtigung „Blown Cover läuft“), auch bei ausgeschaltetem Display,
- die CPU wach halten (Wake Lock),
- Spielmeldungen als Android-Benachrichtigung zeigen (nur mit der App-fähigen Testseite, siehe Stufe 2),
- ein Diagnose-Protokoll führen (Dienst, GPS-Fixes, Display an/aus, Akku, Doze, Zustand der Seite).

Spiellogik, Oberfläche und Datenbank bleiben in der Website. iPhones nutzen weiter die Website im Browser.

## 1. Wo die App liegt
Im Website-Repo `blown-cover`, Zweig `android-app`, Ordner `android/`. Der Zweig `main` (Live-Seite) bleibt davon unberührt.
Der Build-Workflow liegt in `.github/workflows/apk.yml` (im Zweig `android-app`).

### Signaturschlüssel (einmalig)
Der Schlüssel `sideload.jks` liegt **nicht** im Repo, sondern als GitHub-Secret. Unter
Settings → Secrets and variables → Actions → „New repository secret“ müssen zwei Secrets angelegt sein:
- `BC_KEYSTORE_B64`: der Schlüssel als Base64-Text
- `BC_KEYSTORE_PASSWORD`: das Schlüssel-Passwort
Eine Kopie von `sideload.jks` privat aufbewahren (z. B. Drive). Geht der Schlüssel verloren, lassen sich keine Updates mehr drüberinstallieren.

## 2. APK bauen lassen
1. Jeder Push auf den Zweig `android-app` startet den Bau automatisch (zum reinen Neustart genügt ein leerer Commit).
   (Der Knopf „Run workflow“ erscheint erst, wenn `apk.yml` auch auf `main` liegt.)
2. Nach 3 bis 6 Minuten ist der Lauf unter **Actions** grün. Den Lauf öffnen → unten unter **Artifacts** `BlownCover-APK` herunterladen (ZIP) → entpacken → `app-release.apk`.
3. Schlägt der Bau fehl (roter Haken): den Lauf öffnen, den roten Schritt aufklappen und Claude den Text (oder einen Screenshot) schicken.

## 3. Installieren
1. APK aufs Handy bringen (Mail, Drive, USB …) und öffnen. Android fragt einmalig, ob dieser Quelle die Installation erlaubt ist → erlauben.
2. Play Protect kann warnen („unbekannte App“) → „Trotzdem installieren“.
3. Spätere Versionen lassen sich einfach drüberinstallieren (gleiche Signatur).

## 4. Erster Start
Die App öffnet direkt das Spiel. Fehlt noch etwas, erscheint vorher der Dialog **„Bereit machen“**:
- **Standort** (Pflicht): erlauben, und zwar den *genauen* Standort („Bei Nutzung der App“ genügt).
- **GPS** (Pflicht): muss an sein.
- **Benachrichtigungen** (empfohlen): für Pings und Meldungen bei ausgeschaltetem Display.
- **Akku-Optimierung** (empfohlen, aber wichtig): „Ausnehmen“ bestätigen, damit Hersteller (Samsung, Xiaomi …) die App nicht beenden.
Solange ein Pflichtpunkt fehlt, ist „Spielen“ gesperrt. Ist alles grün, startet die App künftig ohne diesen Dialog.

Mit der Zurück-Taste geht die App in den Hintergrund (sie läuft weiter). Beenden: Benachrichtigung „Blown Cover läuft“ → „Beenden“, oder die App aus der Übersicht wischen (in der Lobby tritt man dabei automatisch aus der Lobby aus; außerhalb eines laufenden Spiels beendet das alles; im laufenden Spiel wartet die App 5 Minuten auf die Rückkehr).

## 5. Diagnose und Log
**Lange auf das App-Icon drücken → „Diagnose“.** Dort: Dienst-Status, Bereitschaft (mit „Beheben“), Protokoll, **„Log teilen (Datei)“**, „Dienst beenden“, „Zurück zum Spiel“.
Die App lädt immer die Live-Seite; die App-Anbindung steckt seit v0.2.6 direkt in `index.html` (im Browser ohne Wirkung).

## 6. Mischen mit Browser-Spielern
App und Browser nutzen dieselbe Datenbank: App-Spieler und Browser-Spieler (auch iPhone) können in derselben Lobby spielen. Klappt die App bei jemandem nicht, einfach im Browser mit demselben Code beitreten.

## Was zu beachten ist
- Chrome-Fernzugriff zur Fehlersuche: In der App ist das WebView-Debugging an (`chrome://inspect` am PC, Handy per USB).
- Der Signaturschlüssel liegt nur als GitHub-Secret vor, nicht im (öffentlichen) Repo.
- Android 8 oder neuer wird benötigt.
