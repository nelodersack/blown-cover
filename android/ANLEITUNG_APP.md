# Blown Cover – Android-App (Version 0.1.2)

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
Der Startbildschirm zeigt die Bereitschaft:
- **Standort**: erlauben („Bei Nutzung der App“ genügt).
- **GPS**: muss an sein.
- **Benachrichtigungen**: erlauben (sonst sieht man die Dienst-Anzeige und Meldungen nicht).
- **Akku-Ausnahme**: „Akku-Optimierung ausschalten“ bestätigen. Das ist der wichtigste Punkt, damit Hersteller (Samsung, Xiaomi …) den Dienst nicht beenden.
- Dann **Spiel öffnen**. Die Website erscheint; mit der Zurück-Taste geht die App in den Hintergrund (sie beendet sich nicht). Beenden: Benachrichtigung → „Beenden“ oder Startbildschirm → „Dienst beenden“.

## 5. Zwei Teststufen
**Stufe 1 – Live-Seite in der App** (Adresse: „Live-Seite“)
Die App lädt die normale Website. Die Website weiß noch nichts von der App und nutzt weiter den Browser-Standort. Getestet wird, ob der Dienst bei ausgeschaltetem Display weiterläuft (Diagnose unten am Startbildschirm: „Fixes“ steigen weiter, `♥`-Zeilen alle 30 s, „Seite: …“ zeigt, ob die Website noch antwortet).

**Stufe 2 – Testseite mit App-Anbindung** (Adresse: „Testseite“)
Dafür die Datei `index_app.html` ins Repo der Website `blown-cover` hochladen (neben `index.html`, nichts überschreiben). Die normale Seite bleibt dadurch unverändert. Die Testseite nimmt den Standort vom Hintergrunddienst und zeigt Meldungen als Android-Benachrichtigung, wenn der Bildschirm aus ist. Spielt dort in einer eigenen Lobby.

## 6. Diagnose weitergeben
Startbildschirm → ganz unten **Log teilen** → an Claude schicken (z. B. per Mail/Messenger). Das Protokoll enthält Zeiten, Fixes, Display an/aus, Akkustand, Doze- und Sparmodus-Zustand und Fehler.

## Was zu beachten ist
- Chrome-Fernzugriff zur Fehlersuche: In der App ist das WebView-Debugging an (`chrome://inspect` am PC, Handy per USB).
- Der Signaturschlüssel liegt nur als GitHub-Secret vor, nicht im (öffentlichen) Repo.
- Android 8 oder neuer wird benötigt.
