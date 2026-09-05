# Entwicklung und technische Referenz

Die Installation für den LXC steht in der [README](README.md#installation).

## Installation und Entwicklungsstart

Auf Debian/Ubuntu im LXC werden `python3`, `python3-venv`, `python3-pip` benötigt. Für Produktion zusätzlich Nginx sowie ein HTTPS-Zertifikat; `sqlite3` ist für manuelle Datenbankprüfungen hilfreich.

```bash
cd /pfad/zu/RikasFarbenzauber
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export DJANGO_DEBUG=true
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Öffne `http://127.0.0.1:8000`. Beim ersten Öffnen führt die Anwendung automatisch zu `/setup/`. Dort legst du dein Admin-Konto an und wirst direkt zur Benutzerverwaltung weitergeleitet. Es gibt kein Standardpasswort und keinen vorinstallierten Benutzer.

Für diesen LXC kannst du den LAN-Test mit `./scripts/start-lan.sh` starten und anschließend `http://192.168.2.131:8000` öffnen. Das Terminal muss dabei geöffnet bleiben; der Testserver startet nach einem Neustart nicht automatisch. Eine andere IP kann als Argument übergeben werden: `./scripts/start-lan.sh 192.168.1.50`.

Alternativ für einen Test vom Tablet im vertrauenswürdigen LAN:

```bash
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.50
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Die IP muss durch die LXC-IP ersetzt werden. Der Entwicklungsserver ist nur für Tests gedacht. Über das Internet ausschließlich die unten beschriebene HTTPS-Produktion verwenden.

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

`VERSION` ist die Anwendungs-Version; der Git-Tag lautet entsprechend `v0.5.2`. Für weitere Veröffentlichungen die Version erhöhen und Änderungen im Changelog dokumentieren. Danach Tests und Build prüfen, committen und taggen:

```bash
git add .
git commit -m "Release 0.5.2"
git tag -a v0.5.2 -m "Rikas Farbenzauber 0.5.2"
git push origin main
git push origin v0.5.2
python3 scripts/package_release.py \
  --url https://github.com/BenAhrdt/RikasFarbenzauber/releases/download/v0.5.2/rikas-farbenzauber-0.5.2.zip \
  --notes 'Benutzerwechsel, eigene Verwaltung, Rechte und LXC-Updater'
gh release create v0.5.2 dist/rikas-farbenzauber-0.5.2.zip dist/latest.json \
  --verify-tag --title 'Rikas Farbenzauber 0.5.2' --notes-file CHANGELOG.md
```

Für jede weitere Version sämtliche Versionsangaben anpassen. Das selbst erzeugte ZIP und `latest.json` müssen als Release-Anhänge hochgeladen werden; GitHubs automatisch erzeugtes Quellcode-ZIP ersetzt dieses Paket nicht. `releases/latest/download/latest.json` liefert das Manifest des neuesten regulären Releases. Datenbank, Fotos, `.env`, Logs und virtuelle Umgebung werden weder eingecheckt noch ins Release gepackt.
