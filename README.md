# Rikas Farbenzauber

Eine selbst gehostete Kreativwerkstatt für Kinder. Die Anwendung bietet Figuren, Räume/Häuser, Orte und einfache Szenen mit deutscher, responsiver Oberfläche und eigener SVG-Grafik. Kein Spiel, keine fremden Markenfiguren, keine externen Fonts, Tracker oder Cloud-Dienste.

## Was funktioniert?

- Anmeldung mit individuellen Konten; Eltern verwalten Zugänge und Rechte in der eigenen Verwaltungsoberfläche.
- Persönliches Dashboard mit getrennten Bereichen für Figuren, Räume/Häuser, Orte/Welten und Szenen, Vorschauen, Öffnen und Löschen nach Bestätigung.
- Raum-/Ortseditor mit 900 × 650 Arbeitsfläche, 32 eigenen SVG-Gegenständen aus Möbeln, Deko, Bauen, Natur, Musik und Spielzeug sowie Zimmer-, Haus-, Garten- und Schlossvorlagen.
- Bis zu 100 Objekte pro Raum/Ort/Szene: antippen oder aus der Bibliothek ziehen, auswählen (auch per Liste), verschieben, skalieren, drehen, spiegeln, kopieren, löschen und eine Ebene nach vorne/hinten bewegen. Auf Touch-Geräten ist Antippen immer möglich; senkrechtes Wischen in der Bibliothek scrollt.
- Drei Farben pro Bauobjekt, Hintergrund-/Bodenfarbe, Rückgängig/Wiederholen (60 Schritte während der aktuellen Editorsitzung). Vorlagenwechsel und Löschen fragen nach Bestätigung.
- Gespeicherte Figuren und Projekte als unabhängige Kopien einfügen; Räume/Orte mit „als Grundlage“ einschließlich Hintergrund übernehmen. Die Grundlage ersetzt nach Bestätigung die Arbeitsfläche. Originale bleiben unverändert.
- Umfangreiche Figurenwerkstatt: 23 unabhängige Auswahlfelder mit insgesamt 111 Optionen (einschließlich „Ohne“), 5 Körperregler und 6 Startideen.
- Neue Figuren: 12 Farbregionen, 16 Palettenfarben einschließlich verschiedener Hauttöne, eigener Farbwähler; Flächen direkt antippen. Alte Figuren behalten ihre sieben bisherigen Regionen.
- Verschieben mit Touch, Stift, Maus oder Pfeiltasten; Größe, Drehung und Spiegelung über große Buttons.
- Benannte Figuren serverseitig speichern und auf anderen Geräten erneut bearbeiten.
- Konflikterkennung bei zwischenzeitlichen Änderungen auf einem anderen Gerät; eigene Dialoge vor Verlassen über App-Links/Abmelden mit ungespeicherten Änderungen.
- Farbiges Bild oder schwarze Konturen mit weißen Ausmalflächen.
- PNG (Figuren: 1200 × 1300, Räume/Orte/Szenen: 1800 × 1300), SVG und A4-Druckansicht. PDF über „Als PDF speichern“ im Druckdialog des Browsers.
- App-Manifest als PWA-Vorbereitung. Kein Service Worker, kein Offline-Modus und keine Offline-Speicherwarteschlange; die Installierbarkeit hängt vom Browser ab.

Noch offen sind zusätzliche individuelle Kleidungsstücke, komplexe mehrstöckige Häuser, Zoom/Schwenken, Mehrfachauswahl, Freihandmalen, Autosave und teilweise ausgemalte Bereiche. Undo/Redo ist in beiden Editoren verfügbar (60 Schritte je aktueller Sitzung). Bestätigungen verwenden eigene barrierearme HTML-Dialoge mit Fokusbindung, Escape und großen Buttons. Es gibt keine Browser-Bestätigungs-Popups. Neuladen, Browser-Zurück und Tab-Schließen lassen sich nicht mit einem eigenen asynchronen Dialog abfangen und verwerfen ungespeicherte Änderungen ohne Warnung. Nicht gespeicherte Änderungen liegen nur im Arbeitsspeicher des aktuellen Tabs; mobile Betriebssysteme können Tabs ohne Verlassen-Warnung schließen. Regelmäßig „Speichern“ antippen.

## Erweiterte Figurenwerkstatt

Neue Figuren starten mit `avatar-v2`. Oben stehen die Startvorlagen **Junge**, **Mädchen** und **Frei gestalten** bereit. Sie stellen lediglich veränderbare Bausteine und Proportionen ein, erhalten die gewählten Farben und können über Undo rückgängig gemacht werden. Es wird kein Geschlecht als Konten- oder Figurenattribut gespeichert. Im Menü **Was möchtest du gestalten?** zwischen Körper, Gesicht, Haare, Kleidung, Accessoires und Fantasie wechseln. Körpergröße, Körperbreite, Kopfgröße, Beinlänge und Schulterbreite sind innerhalb sinnvoller Grenzen frei regelbar. Kopfform und Haltung (entspannt, winkend, Hände an den Hüften) sind ebenfalls wählbar. Körper- und Kleidungsgeometrie teilen dieselben Ansatzpunkte.

Kombinierbar sind 10 Frisuren mit 4 Ponyvarianten, 6 Augenstile, Augenbrauen, Nase, Mund, Ohren und Gesichtsdetails; 8 Oberteile, 6 Unterteile, 5 Schuhe und 6 Motive. Accessoires umfassen Kopfschmuck, Brillen, Ohrringe, Halsschmuck, Taschen, Dinge in der Hand, Kopfhörer, Flügel und Schweife. „Ideen zum Starten“ bietet Alltag, Sternenbühne, Waldzauber, Straßenstil, Wolkenfee und Abenteuer. „Überrasch mich“ mischt die Bausteine; es ist keine KI-Generierung. Alle Kombinationen sind unabhängig von Geschlechtsvorgaben möglich.

Bestehende `sprout-v1`-Figuren bleiben im bisherigen Stil darstellbar, färbbar und exportierbar. **Mehr Möglichkeiten** übernimmt eine Figur nach eigenem Bestätigungsdialog in die neue Werkstatt und erhält die Farben. Die neue Geometrie entspricht nicht exakt dem alten Aussehen; Undo bringt die Originalfigur während der Sitzung zurück. Erst Speichern ersetzt den gespeicherten Stand. Bereits als Kopie in Szenen eingefügte Figuren bleiben unverändert.

`static/studio/avatar-catalog.json` ist der gemeinsame Optionskatalog für Servervalidierung und Figuren-UI. `avatar.js` zeichnet die eigene modulare SVG-Figur, `figure.js` unterstützt alte und neue Assets nebeneinander. Dokumentversion 1 bleibt für Figuren gültig, Version 2 für Szenen. Der Renderer funktioniert ebenso in Vorschauen, Szenen und Ausmal-/Exportausgaben. Neue Optionen nur zusammen mit einer passenden Zeichnung ergänzen; bestehende Asset-IDs und Optionen nicht still umdeuten.

## Eigene Fotos und Bilderrahmen

In Räumen, Orten und Szenen links **Eigene Fotos** öffnen. **Foto auswählen** lädt ein Bild vom Gerät; **Foto aufnehmen** öffnet auf unterstützten Mobilgeräten die Kamera-Dateiauswahl. Je nach Browser wird stattdessen die normale Dateiauswahl angeboten. Es gibt keine eigene Live-Kameravorschau und keine Cloud-Verarbeitung.

Im eigenen Dialog Namen vergeben, Ränder mit vier Schiebereglern zuschneiden und **Als Foto-Gegenstand** oder **Mit Bilderrahmen** wählen. Das gespeicherte Foto wird eingesetzt. Danach das **Projekt speichern**. Mit **Meine Fotos anzeigen** lassen sich Fotos erneut einfügen. Ein ausgewähltes Foto hat Buttons für Rahmen an/aus sowie Foto ersetzen oder neue Aufnahme; Rahmenfarbe über die vorhandene Palette ändern. Verschieben, Drehen, Skalieren, Spiegeln und Kopieren funktionieren wie bei anderen Gegenständen.

Das Foto bleibt ein rechteckiges Bild seiner ursprünglichen Ansicht. Kein automatisches Freistellen, Nachzeichnen, 3D-Modellieren oder Umfärben einzelner Fotobereiche. Im Ausmalmodus bleibt die Fotofläche weiß. Farbige PNG-/SVG-Exporte enthalten die Bilddaten vollständig, sodass sie ohne Anmeldung oder Serververbindung geöffnet werden können. Ein exportiertes Bild kann entsprechend wie jede lokale Bilddatei weitergegeben werden.

Uploads: JPG, PNG, WebP; maximal 12 MB und 24 Megapixel. HEIC/HEIF wird noch nicht unterstützt und muss vorher als JPG exportiert werden. Server korrigiert EXIF-Ausrichtung, schneidet zu und verkleinert auf maximal 1600 × 1600 Pixel. Nur ein neu erzeugtes JPEG ohne EXIF/GPS-/Originalmetadaten wird gespeichert. Transparenz wird weiß; Animationen werden auf das erste Bild reduziert. Maximal 100 Fotos pro Benutzer, jeweils höchstens 1 MB normalisierte Daten. Bibliotheksfotos bleiben auch beim Löschen eines Projekts erhalten, damit andere Projekte sie weiterhin verwenden können; mit „Foto löschen“ können ungenutzte Fotos nach eigener Bestätigung dauerhaft entfernt werden. Bei Verwendung in gespeicherten Projekten nennt die Meldung deren Namen. Zuerst dort entfernen und speichern. Auf der aktuellen Arbeitsfläche verwendete Fotos sind ebenfalls geschützt. Enthält der Undo-Verlauf ein gelöschtes Foto, wird dieser geleert, damit keine ungültigen Fotoreferenzen wiederhergestellt werden.

Fotos liegen mit Eigentümer-ID als Binärdaten in SQLite und sind im vorhandenen Datenbankbackup enthalten. Es gibt kein öffentliches Media-Verzeichnis. `/api/photos/` listet eigene Fotos oder nimmt Multipart-Uploads mit `photo`, `name`, `crop` entgegen. `/api/photos/<uuid>/image/` liefert ausschließlich eigene Fotos mit `private, no-store`. Projekt-Speicherung prüft Besitzer und Abmessungen jeder Fotoreferenz. Bilder werden nicht als Data-URLs im Projektdokument gespeichert, sondern über stabile private IDs referenziert.

Beim Produktionsupdate die neue Nginx-Location für `/api/photos/` übernehmen: Nur dort gilt ein Request-Limit von 13 MB einschließlich Multipart-Daten; die übrigen API-Anfragen behalten 100 KB. App und Proxy begrenzen Uploads, Pillow prüft Format/Pixelzahl. Die Serververarbeitung ist CPU-basiert, eine GPU ist nicht nötig.

## Technologie und Entscheidung

Python 3.12+ (hier mit 3.13 getestet), Django 5.2 LTS, SQLite, Gunicorn und Pillow für Bildverarbeitung. Abhängigkeiten sind in `requirements.txt` exakt fixiert. Django liefert Authentifizierung, sichere Passwort-Hashes, Sessions, CSRF-Schutz, ORM und Migrationen aus einem gepflegten Framework. Die LTS-Reihe ist für einen kleinen wartbaren Server geeignet: [Django 5.2 Release Notes](https://docs.djangoproject.com/en/5.2/releases/5.2/).

Der gemeinsame Renderer (`figure.js` + `objects.js`) und die Exportfunktion (`export.js`) werden für Vorschauen und beide Editoren verwendet. `space.js` enthält die Mehrfachobjekt-Bedienung. Stabile Asset-IDs sind in `studio/schema.py` erlaubt; neue Bibliotheksobjekte dort und in `objects.js` ergänzen.

Das Frontend nutzt HTML-Templates, CSS und native JavaScript-Module. Ein Framework oder Node-Build ist für diesen Umfang nicht nötig. SVG erhält einzeln benannte Farbregionen und dieselbe Darstellung für Vorschau, Bearbeitung und Export. Alle Figurenpfade wurden für dieses Projekt erstellt. SQLite erleichtert Installation und Backups für wenige gleichzeitige Familienkonten; bei deutlich mehr parallelen Schreibzugriffen kann das Django-Datenbankbackend auf PostgreSQL umgestellt werden.

## Struktur

```text
config/                 Django-Konfiguration, URLs, WSGI
studio/                 Modelle, API, Login, Validierung, Tests, Migrationen
static/studio/          SVG-Renderer, Editor, Dashboard, CSS, App-Manifest
templates/              Login, Dashboard, Editor
data/                   SQLite-Datenbank (nicht im Repository)
deploy/                 systemd- und Nginx-Beispiele
scripts/build.sh        Produktionsassets und Python-Prüfung
scripts/backup.py       Konsistentes Online-Backup
scripts/browser_test.py Isolierter Chromium-End-to-End-Test
```

## Installation und Entwicklungsstart

Auf Debian/Ubuntu im LXC werden `python3`, `python3-venv`, `python3-pip` benötigt. Für Produktion zusätzlich Nginx sowie ein HTTPS-Zertifikat; `sqlite3` ist für manuelle Datenbankprüfungen hilfreich.

```bash
cd /home/ben/RikasFarbenzauber
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export DJANGO_DEBUG=true
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Öffne `http://127.0.0.1:8000`. Beim ersten Öffnen führt die Anwendung automatisch zu `/setup/`. Dort legst du dein Admin-Konto an und wirst direkt zur Benutzerverwaltung weitergeleitet. Es gibt kein Standardpasswort und keinen vorinstallierten Benutzer. Die virtuelle Umgebung und eine leere migrierte Datenbank sind im aktuellen Arbeitsordner bereits angelegt.

Für diesen LXC kannst du den LAN-Test mit `./scripts/start-lan.sh` starten und anschließend `http://192.168.2.131:8000` öffnen. Das Terminal muss dabei geöffnet bleiben; der Testserver startet nach einem Neustart nicht automatisch. Eine andere IP kann als Argument übergeben werden: `./scripts/start-lan.sh 192.168.1.50`.

Alternativ für einen Test vom Tablet im vertrauenswürdigen LAN:

```bash
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.50
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Die IP muss durch die LXC-IP ersetzt werden. Der Entwicklungsserver ist nur für Tests gedacht. Über das Internet ausschließlich die unten beschriebene HTTPS-Produktion verwenden.

## Benutzerverwaltung und Anmeldung

Unter **Verwaltung → Benutzer** (`/verwaltung/benutzer/`) legen Administratoren Konten an, ändern Passwörter und vergeben Rechte für Figuren, Räume/Häuser, Orte/Welten, Szenen, eigene Fotos und Löschen. Die Rechte werden auch serverseitig geprüft. Bestehende Konten behalten alle Kreativfunktionen. Administratoren haben sämtliche Rechte; nur sie dürfen Benutzer und Updates verwalten. `/admin/` führt zur neuen Verwaltung im App-Design.

Konten lassen sich deaktivieren; ihre Projekte bleiben erhalten. Der eigene Administrator kann sich hier nicht deaktivieren oder herabstufen. Neue Administratoren werden ausschließlich durch einen angemeldeten Administrator angelegt. Die Ersteinrichtung bleibt nach dem ersten Admin dauerhaft gesperrt. Bei verlorenem Zugang helfen lokal `manage.py createsuperuser` oder `changepassword`.

**Auf diesem Gerät angemeldet bleiben** ist beim Login vorausgewählt. Das geschützte Session-Cookie gilt ein Jahr und wird bei Nutzung erneuert. Abmelden beendet die Sitzung serverseitig. Ohne Häkchen gilt eine Browser-Sitzung. Gelöschte Cookies, privates Surfen, Browserbereinigung und Passwortänderungen können eine erneute Anmeldung erfordern. In Produktion werden Cookies ausschließlich über HTTPS übertragen.

### Als Benutzer anmelden

Unter **Verwaltung → Benutzer → Als … anmelden** kannst du ein aktives Konto ohne dessen Passwort öffnen. Der Hinweis oben zeigt, als wer du arbeitest. **Zurück zum Admin** bringt dich zu deinem ursprünglichen Administratorkonto zurück. Bearbeitungen und Löschungen betreffen tatsächlich das gewählte Konto. In dieser Ansicht ist die Verwaltung gesperrt; zuerst zurückkehren, um erneut das Konto zu wechseln.

Der Wechsel gilt für alle Tabs desselben Browserprofils. Vorher offene Bearbeitungen speichern. Abmelden beendet beide Zugänge in dieser Sitzung. Wird das ursprüngliche Administratorkonto deaktiviert, herabgestuft oder sein Passwort geändert, verfällt die Rückkehrberechtigung.

## Installation mit Git Clone

Voraussetzung: frischer Debian-/Ubuntu-LXC mit systemd, Python 3.12 oder neuer und ein HTTPS-Reverse-Proxy. Bei einem privaten Repository benötigt Git einen autorisierten SSH-Schlüssel oder eine GitHub-Anmeldung; Zugangstokens nicht in URLs schreiben.

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-venv
git clone https://github.com/BenAhrdt/RikasFarbenzauber.git
cd RikasFarbenzauber
git checkout v0.5.1
sudo sh scripts/install.sh --install-packages \
  --host farben.example.org --proxy-ip 192.168.2.10 \
  --manifest-url https://github.com/BenAhrdt/RikasFarbenzauber/releases/latest/download/latest.json
```

Domain und Proxy-IP anpassen. Den HTTPS-Proxy auf `http://LXC-IP:8080` zeigen lassen und danach die Domain öffnen, um den ersten Admin einzurichten. Mit `--manifest-url ""` lassen sich Update-Prüfungen deaktivieren. Private GitHub-Releases sind vom derzeitigen Updater ohne zusätzliche Download-Infrastruktur nicht abrufbar; dafür eine zugängliche eigene HTTPS-Release-Quelle verwenden.

Der Git-Checkout dient als Installationsquelle. Der Installer kopiert die Anwendung in versionierte Verzeichnisse. Spätere Produktionsupdates erfolgen über **Verwaltung → Updates** oder `sudo sh scripts/update.sh`; ein `git pull` im Quellordner verändert die laufende Produktionsversion nicht.

Für Entwicklung nach `git clone`: die Befehle unter „Installation und Entwicklungsstart“ verwenden. Zum Aktualisieren dieses Entwicklungs-Checkouts: `git pull --ff-only`, Abhängigkeiten installieren, `manage.py migrate` und den Build ausführen, anschließend den Entwicklungsserver neu starten.

## Automatische LXC-Installation und Updates

Für einen frischen Debian-/Ubuntu-LXC mit systemd und Python 3.12+ den Projektquellcode kopieren oder ein Release-ZIP entpacken. Ein vorhandener HTTPS-Reverse-Proxy übernimmt das Zertifikat:

```bash
sudo sh scripts/install.sh --install-packages --host farben.example.org --proxy-ip 192.168.2.10
```

`--host` ist der öffentliche Hostname, `--proxy-ip` die tatsächliche Quell-IP des Reverse-Proxys. Dessen Ziel ist `http://LXC-IP:8080`. Der interne Nginx lässt nur diese Proxy-IP zu. Optional bereits bei Installation `--manifest-url https://downloads.example.org/rika/latest.json` angeben. Die Beispieladressen müssen durch eigene ersetzt werden.

Das Skript installiert den Benutzer `rikas`, Python-Umgebung, Datenbank, Assets, Nginx, App-Dienst und Updater-Dienst. Es erzeugt das Secret selbst. Bereits vorhandene Installationspfade werden nicht überschrieben. Es migriert keine bestehende Entwicklungsinstallation automatisch.

- Releases: `/opt/rikas-farbenzauber/releases/`; `current` zeigt auf die aktive Version.
- Datenbank und Fotos: `/var/lib/rikas-farbenzauber/data/db.sqlite3`.
- Sicherungen: `/var/lib/rikas-farbenzauber/backups/` (vor jedem Update, separat regelmäßig sichern).
- App-Konfiguration: `/etc/rikas-farbenzauber.env`; Updater-Konfiguration: `/etc/rikas-updater.json`, beide nur für root.
- Dienste: `rikas-farbenzauber.service`, `rikas-updater.path`, `rikas-updater.service`.

**Verwaltung → Updates** zeigt die installierte Version und bietet **Nach Updates suchen** sowie **Update installieren**. Die Fortschrittsanzeige meldet Download, Vorbereitung, Sicherung, Migration und Neustart. Nach erfolgreicher Gesundheitsprüfung lädt die Seite neu. Updates werden zuerst in einem separaten Release-Verzeichnis vorbereitet; erst danach wird die Anwendung kurz gestoppt. Bei Fehlern nach der Sicherung stellt der Updater Datenbank und vorherige Version wieder her. Das neue Release wird mit eigenem Python-Environment aufgebaut; Paketdownloads brauchen Internetzugriff. Vorher alle Projekte speichern.

Alternativ startet `sudo sh scripts/update.sh` ein Update über denselben Dienst. Diagnose: `sudo journalctl -u rikas-updater.service` und `/var/log/rikas-updater.log`. Alte Releases und Sicherungen bleiben zur Wiederherstellung erhalten und sollten bei Bedarf bewusst bereinigt werden. Bei Stromausfall während eines Updates können manuelle Wiederherstellung und Entfernen einer verwaisten `updates/active`-Markierung nötig sein; vorher Dienstzustand, Datenbank und Sicherung prüfen.

### Eigene Releases veröffentlichen

Als Standard ist das öffentliche GitHub-Release-Manifest unter `https://github.com/BenAhrdt/RikasFarbenzauber/releases/latest/download/latest.json` hinterlegt. Ohne konfigurierte Quelle zeigt die Verwaltung einen entsprechenden Hinweis. Die Datei `VERSION` verwendet `MAJOR.MINOR.PATCH`. Für eine neue Veröffentlichung Version erhöhen, Tests und Build ausführen und dann beispielsweise:

```bash
python3 scripts/package_release.py --url https://downloads.example.org/rika/rikas-farbenzauber-0.5.1.zip --notes 'Neue Verwaltung, Rechte und LXC-Updater'
```

Das erzeugt `dist/rikas-farbenzauber-0.5.1.zip` und `dist/latest.json`. Zuerst das ZIP und danach das Manifest unter den passenden HTTPS-Adressen veröffentlichen. ZIPs enthalten weder Datenbank noch lokale Secrets. Das Manifest enthält Version, Download-URL, SHA-256 und Hinweise. Nur höhere Versionsnummern werden angeboten. HTTPS und Prüfsumme werden vor der Installation geprüft; die Release-Quelle muss vertrauenswürdig sein, da sie Anwendungscode liefert.

Eine nachträglich eingerichtete Manifest-Adresse muss sowohl als `UPDATE_MANIFEST_URL` in `/etc/rikas-farbenzauber.env` als auch als `manifest_url` in `/etc/rikas-updater.json` gesetzt werden. Danach `sudo systemctl restart rikas-farbenzauber`. Der root-eigene Updater selbst wird nicht durch heruntergeladenen Anwendungscode ersetzt. Im bisherigen Entwicklungsbetrieb ist die automatische Installation deaktiviert; sie benötigt die vom Installer angelegte Dienststruktur.

## Datenmodell und API

`Project`: UUID, Besitzer-Fremdschlüssel, Name, Typ (`character`, `room`, `world`, `scene`), Dokument als JSON, Revision, Erstellungs- und Änderungszeit. Dokumentversion 1 enthält Canvas-Größe/Hintergrund und eine geordnete Objektliste. Objekte haben stabile Asset-ID, Instanz-ID, Position, Maßstab, Rotation, Spiegelung, Variante und eine Map benannter Farben. Listenreihenfolge entspricht Ebenenreihenfolge. Bestehende Figuren bleiben in Dokumentversion 1 (600 × 650, maximal 20 Figurenobjekte). Räume, Häuser, Orte und Szenen verwenden Version 2 (900 × 650, zusätzliche Bodenfarbe `ground`, 0–100 Objekte). Häuser werden unter `room` gespeichert. Die Figuren-UI bearbeitet weiterhin eine Figur; der neue Editor unterstützt die ganze Objektliste. Typ und Dokumentversion werden gemeinsam serverseitig validiert. SVG-Bauobjekte verwenden die Farbregionen `main`, `detail` und `accent`; Alte Figuren behalten ihre sieben benannten Regionen; `avatar-v2` hat zwölf Farbregionen und zusätzlich `appearance` mit `choices` und `body`. Es werden keine fremden Projekt-IDs oder beliebige SVG-Fragmente vom Client aufgelöst. Einfügen erfolgt aus der geschützten Liste eigener Dokumente als eigenständige Kopie. Neue Asset-Typen müssen in Validator und Renderer ergänzt werden.

- `GET/POST /api/projects/`: eigene Projekte auflisten bzw. Figur erstellen.
- `GET/PUT/DELETE /api/projects/<uuid>/`: eigenes Projekt lesen, ändern, löschen.
- POST benötigt `name`, `document` und bei neuen Raum-/Ortsprojekten `kind` (Standard `character`); PUT benötigt `name`, `document` und zusätzlich die zuletzt gelesene `revision`.
- 400: ungültige Daten; 403: CSRF fehlt; 404: fehlt oder gehört jemand anderem; 409: neuere Revision vorhanden.
- Anonyme Anfragen werden zur Anmeldung umgeleitet. Das Frontend erkennt abgelaufene Sitzungen, bewahrt den Editorinhalt im Tab und ermöglicht weiterhin Export.

Keine benutzergelieferten SVG-/HTML-Fragmente werden gespeichert oder ausgeführt. Der Server akzeptiert nur bekannte Assets und streng validierte Farb- und Zahlenwerte. Erweiterungen erhalten neue Dokumentversionen und eine explizite Konvertierung; bestehende `sprout-v1`-Assets sollten visuell stabil bleiben.

## Umgebungsvariablen

Die Anwendung liest Prozessvariablen. `.env` wird **nicht automatisch geladen**; systemd liest sie über `EnvironmentFile`, in der Shell wird sie explizit geladen.

| Variable | Bedeutung |
| --- | --- |
| `DJANGO_DEBUG` | Standard `false`; nur lokal `true` setzen |
| `DJANGO_SECRET_KEY` | In Produktion verpflichtend, zufällig und mindestens 50 Zeichen |
| `DJANGO_ALLOWED_HOSTS` | Kommagetrennte Hostnamen ohne Schema, keine Wildcards |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Kommagetrennte HTTPS-Origins, z. B. `https://farben.example.org` |
| `DATABASE_PATH` | Absoluter SQLite-Pfad; Standard `data/db.sqlite3` im Projekt |

Geheimnis erzeugen: `.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(64))'`. Den Wert ausschließlich in `.env` oder die eigene Secret-Verwaltung übernehmen. `.env`, Datenbank und virtuelle Umgebung sind ignoriert. Das Verzeichnis der Datenbank muss existieren und dem Dienstbenutzer gehören.

## Produktionsbuild und LXC-Betrieb

```bash
cp .env.example .env
chmod 600 .env
# .env editieren: Secret, Domain und Datenbankpfad setzen
set -a
. ./.env
set +a
.venv/bin/python manage.py migrate
./scripts/build.sh
.venv/bin/python manage.py check --deploy --fail-level WARNING
.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2
```

Der Produktionsbuild besteht aus Django-Prüfung, `collectstatic` mit Dateihashes und Python-Bytecode-Prüfung. Es gibt keinen zusätzlichen npm-Build. Der Build erzeugt zunächst `avatar-catalog.js` synchron aus `avatar-catalog.json`; der Browser braucht keinen separaten JSON-Abruf beim Start. Django versieht auch die importierten JavaScript-Module mit Dateihashes, damit jede veröffentlichte Version eine zusammenpassende Modulstruktur lädt. Gunicorn bedient die Anwendung, Nginx die statischen Dateien. Direkte HTTP-Anfragen an Gunicorn werden in Produktion zu HTTPS umgeleitet.

Für dauerhaften Betrieb `deploy/rikas-farbenzauber.service` an Pfad und Dienstbenutzer anpassen. Das Beispiel verwendet den vorhandenen Benutzer `ben`; ein eigener unprivilegierter Dienstbenutzer ist ebenfalls möglich. Danach:

```bash
sudo cp deploy/rikas-farbenzauber.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rikas-farbenzauber
sudo journalctl -u rikas-farbenzauber -f
```

Der Dienst benötigt Schreibzugriff nur auf `data/`. Keine Migrationen oder Builds im gestarteten systemd-Dienst ausführen; diese erfolgen beim Update über die Shell.

## Reverse Proxy und HTTPS

`deploy/nginx.conf` enthält HTTP-zu-HTTPS-Umleitung, TLS-Pfade, statische Dateien, Header und Login-Ratenbegrenzung. Domain und Zertifikatspfade anpassen. Die Zertifikate müssen vor Aktivierung der TLS-Konfiguration vorhanden sein, beispielsweise über die vorhandene Reverse-Proxy-Verwaltung oder ACME. Nginx muss nicht auf das private Home-Verzeichnis zugreifen:

```bash
sudo mkdir -p /var/www/rikas-static
sudo cp -a staticfiles/. /var/www/rikas-static/
sudo chmod -R a+rX /var/www/rikas-static
sudo cp deploy/nginx.conf /etc/nginx/sites-available/rikas-farbenzauber
sudo ln -s /etc/nginx/sites-available/rikas-farbenzauber /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Das Beispiel nimmt Nginx im selben LXC an. Bei externem Proxy Gunicorn ausschließlich auf der privaten LXC-IP binden und Port 8000 per Firewall auf den Proxy beschränken. Der Proxy muss `Host`, `X-Forwarded-Proto` und `X-Real-IP` **selbst überschreiben**, nicht ungeprüft Clientwerte durchreichen. Diese Vertrauensgrenze ist nötig, weil Django den HTTPS-Status und die Login-IP daraus liest. Der Proxy muss auch `/static/` bedienen oder an einen internen Static-Server weiterleiten.

Produktionscookies sind Secure, HttpOnly (Session) und SameSite=Lax. CSRF ist für schreibende Anfragen aktiv. Zusätzlich: CSP, Frame-Verbot, sichere Passwort-Hashes, parametrisierte ORM-Abfragen, beschränkte Dokumentgröße und Login-Drosselung (10 Versuche pro IP in 15 Minuten; zusätzlicher Nginx-Limiter). Auch `/admin/login/` verwendet denselben geschützten Login. HSTS inklusive Subdomains/Preload ist konfiguriert; die verwendete Domain und ihre Subdomains müssen daher für dauerhaften HTTPS-Betrieb geeignet sein. Details: [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).

## Backup und Wiederherstellung

Das Backup-Skript verwendet die SQLite-Backup-API und kann während des Betriebs eine konsistente Kopie erzeugen. Nicht einfach eine laufende SQLite-Datei mit `cp` kopieren.

```bash
# Falls ein abweichender DATABASE_PATH genutzt wird: zuvor .env laden
.venv/bin/python scripts/backup.py /tmp/rikas-backup.sqlite3
```

Das Ziel darf noch nicht existieren. Für regelmäßige Sicherungen einen datierten Dateinamen und einen geschützten Backup-Ordner verwenden. Datenbankkopien enthalten auch Passwort-Hashes und Sitzungen: geschützt und möglichst verschlüsselt auf einem anderen Gerät aufbewahren. Zusätzlich `.env` sicher sichern und den zugehörigen Quellcodestand dokumentieren. Vektorgrafiken sind im Quellcode enthalten; normalisierte Foto-Uploads liegen direkt in SQLite und werden mitgesichert. Es gibt kein zusätzlich zu sicherndes Upload-Verzeichnis.

Wiederherstellen: Dienst stoppen, aktuelle Datenbank sichern, Backup an den konfigurierten `DATABASE_PATH` kopieren, Besitzer/Dateirechte korrigieren, ggf. Migrationen ausführen und Dienst starten. Backups regelmäßig testweise in eine separate Umgebung zurückspielen.

## Updates und Wartung

1. Backup erstellen und Dienst stoppen.
2. Neuen Quellcodestand einspielen und `.venv/bin/pip install -r requirements.txt` ausführen.
3. `.env` laden, `migrate`, `scripts/build.sh` und `check --deploy` ausführen.
4. `staticfiles/` erneut nach `/var/www/rikas-static/` kopieren, Dienst starten und Anmeldung/Speicherung prüfen.
5. Bei Rollback auch passende Datenbanksicherung verwenden, falls Migrationen nicht rückwärtskompatibel sind.

Regelmäßig unterstützte Django-Sicherheitsversionen prüfen, Lockdatei bewusst aktualisieren und Tests erneut ausführen. Alte Sitzungen mit `manage.py clearsessions` entfernen. Login-Drosselungsdatensätze enthalten nur IP-Hashes, Zähler und Zeitstempel; sie können periodisch über das ORM gelöscht werden, wenn `started_at` älter als einen Tag ist.

## Tests

```bash
DJANGO_DEBUG=true .venv/bin/python manage.py test
.venv/bin/python scripts/setup_race_test.py
DJANGO_DEBUG=true ./scripts/build.sh
# Optionaler Browser-Test:
.venv/bin/pip install -r requirements-dev.txt
PLAYWRIGHT_BROWSERS_PATH=/tmp/rika-browsers .venv/bin/python -m playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=/tmp/rika-browsers .venv/bin/python scripts/browser_test.py
```

Der Browser-Test legt eine temporäre Datenbank und ein Testkonto an, startet einen lokalen Testserver und entfernt beides danach. Er prüft Ersteinrichtung, Login, Varianten, Farben, Touch-Eingaben, Speichern/Öffnen, zweites Gerät, PNG/SVG/PDF, schmale Bildschirmbreite und Löschen sowie Räume, Kopieren, Ebenen, Undo/Redo, Vorlagen und Szenen aus gespeicherten Werken sowie Foto-Upload, Zuschneiden, Bilderrahmen und vollständig eingebettete Foto-Exporte. Die Kamera-Dateiauswahl muss zusätzlich auf einem echten Mobilgerät geprüft werden. Screenshots landen in `/tmp/rika-*.png`. Die Backend-Tests decken Besitzertrennung, Validierung, CSRF, Konflikte, Login-Drosselung und Escaping ab. Für Chromium können je nach LXC Systembibliotheken nötig sein (`playwright install-deps chromium`). Echte iPad-/Android-Geräte und deren Druckdialoge sollten vor dem Familienbetrieb zusätzlich ausprobiert werden.

## Zuverlässiger Seitenstart im Entwicklungsbetrieb

Der eigene `runserver`-Befehl liefert im DEBUG-Modus HTML und Assets mit `Cache-Control: no-store` aus und ignoriert bedingte Cache-Anfragen. Templates werden ohne Template-Cache geladen, auch wenn `--noreload` verwendet wird. Nach Python-/Konfigurationsänderungen muss der Dev-Server weiterhin neu gestartet werden; Änderungen an HTML/CSS/JS werden nach normalem Neuladen sichtbar. Änderungen am Figurenkatalog benötigen `scripts/sync_assets.py` bzw. den Build.

`bootstrap.js` startet Dashboard und Editoren, hält die Bedienung bis zur vollständigen Initialisierung gesperrt und zeigt bei Fehlern eine eigene Meldung mit „Erneut laden“. Gespeicherte Projektnamen stehen bereits im serverseitigen HTML. Ohne JavaScript erscheint ein Hinweis. Die Browserprüfung simuliert auch fehlende Module und eine veraltete HTML-Struktur und prüft anschließend die Wiederherstellung aller Vorlagen ohne zusätzliche Interaktion.

## Git-Tags und GitHub-Releases

`VERSION` ist die Anwendungs-Version; der Git-Tag lautet entsprechend `v0.5.1`. Für weitere Veröffentlichungen die Version erhöhen und Änderungen im Changelog dokumentieren. Danach Tests und Build prüfen, committen und taggen:

```bash
git add .
git commit -m "Release 0.5.1"
git tag -a v0.5.1 -m "Rikas Farbenzauber 0.5.1"
git push origin main
git push origin v0.5.1
python3 scripts/package_release.py \
  --url https://github.com/BenAhrdt/RikasFarbenzauber/releases/download/v0.5.1/rikas-farbenzauber-0.5.1.zip \
  --notes 'Benutzerwechsel, eigene Verwaltung, Rechte und LXC-Updater'
gh release create v0.5.1 dist/rikas-farbenzauber-0.5.1.zip dist/latest.json \
  --verify-tag --title 'Rikas Farbenzauber 0.5.1' --notes-file CHANGELOG.md
```

Für jede weitere Version sämtliche Versionsangaben anpassen. Das selbst erzeugte ZIP und `latest.json` müssen als Release-Anhänge hochgeladen werden; GitHubs automatisch erzeugtes Quellcode-ZIP ersetzt dieses Paket nicht. `releases/latest/download/latest.json` liefert das Manifest des neuesten regulären Releases. Datenbank, Fotos, `.env`, Logs und virtuelle Umgebung werden weder eingecheckt noch ins Release gepackt.
