# Rikas Farbenzauber

Eine selbst gehostete Kreativwerkstatt für Kinder. Die Anwendung bietet Figuren, Räume/Häuser, Orte und einfache Szenen mit deutscher, responsiver Oberfläche und eigener SVG-Grafik. Kein Spiel, keine fremden Markenfiguren, keine externen Fonts, Tracker oder Cloud-Dienste.

## Installation

Für einen frischen Debian-/Ubuntu-LXC mit systemd, Python 3.12 oder neuer . In der LXC-Konsole als **root** ausführen:

```bash
apt-get update
apt-get install -y git
git clone https://github.com/BenAhrdt/RikasFarbenzauber.git
cd RikasFarbenzauber
./install.sh
```

Das Skript fragt nach **Domain** (ohne `https://`). Es installiert die benötigten Pakete, richtet Datenbank, Caddy mit automatischem HTTPS, Anwendung und Update-Dienst ein und erzeugt das Secret. Als normaler Benutzer `sudo ./install.sh` verwenden.

Danach die Domain öffnen. DNS (A/AAAA) und die Router-/Firewall-Freigaben für TCP 80 und 443 müssen auf den LXC zeigen. Diese Einstellungen außerhalb des LXC kann das Skript nicht selbst ändern. Caddy beschafft und erneuert das Zertifikat automatisch; ein zusätzlicher Reverse-Proxy ist nicht erforderlich. [Hinweise zu automatischem HTTPS](https://caddyserver.com/docs/automatic-https). Beim ersten Aufruf legst du dein Administratorkonto an. Es gibt kein Standardpasswort. Die Dienste starten beim Neustart des LXC automatisch.

Für eine unbeaufsichtigte Installation können die Angaben auch mitgegeben werden:

```bash
./install.sh --host farben.example.org
```

Nur wenn bewusst ein vorhandener externer HTTPS-Proxy verwendet werden soll, zusätzlich `--proxy-ip IP` angeben; dann wird der bisherige Nginx-Betrieb auf Port 8080 verwendet.

Vorhandene Installationen werden nicht überschrieben. Eine Entwicklungsinstallation wird nicht automatisch übernommen. Der Git-Ordner dient als Installationsquelle; die laufende Anwendung liegt unter `/opt/rikas-farbenzauber/current`.

## Updates

In **Verwaltung → Updates** zuerst **Nach Updates suchen**, dann **Update installieren** wählen. Die GitHub-Release-Quelle ist bereits eingestellt. Der Fortschritt wird angezeigt; nach erfolgreichem Update lädt die Seite neu. Vorher offene Projekte speichern.

Manuell in der LXC-Konsole als root:

```bash
cd /opt/rikas-farbenzauber/current
./update.sh
```

Alternativ funktioniert `./update.sh` auch aus dem geklonten Projektordner. Als normaler Benutzer `sudo ./update.sh` verwenden. Der Aufruf startet das Update im Hintergrund; den Fortschritt siehst du in der Verwaltung oder mit:

```bash
journalctl -u rikas-updater.service -f
```

Beide Wege verwenden denselben Dienst. Bei neuen Installationen ruft dieser eine root-eigene Kopie von `update.sh --worker` auf. Diese führt den installierten Updater aus. Er prüft Version und SHA-256, bereitet ein separates Release vor, sichert die Datenbank und startet die Anwendung neu. Bei Fehlern nach der Sicherung wird der vorherige Stand wiederhergestellt. Ein `git pull` alleine aktualisiert die laufende Anwendung nicht.

Installationen aus 0.5.1 behalten ihren vorhandenen Update-Dienst und können darüber weiterhin aktualisieren. Der bisherige Dienst ruft den gleichen Python-Updater direkt auf. Root-eigene Dienstdateien werden aus Sicherheitsgründen nicht automatisch durch Release-Code überschrieben.

## Betrieb und Sicherungen

- Datenbank einschließlich Fotos: `/var/lib/rikas-farbenzauber/data/db.sqlite3`.
- Update-Sicherungen: `/var/lib/rikas-farbenzauber/backups/`.
- App-Konfiguration: `/etc/rikas-farbenzauber.env`.
- Updater-Konfiguration: `/etc/rikas-updater.json`.
- Update-Protokoll: `/var/log/rikas-updater.log`.

Datenbank und Konfiguration zusätzlich regelmäßig geschützt auf einem anderen Gerät sichern. Alte Releases und Sicherungen bleiben erhalten; den Speicherplatz gelegentlich prüfen. Bei einem Stromausfall während des Updates kann eine manuelle Wiederherstellung nötig sein.

Eine eigene HTTPS-Update-Quelle lässt sich bei der Installation mit `--manifest-url URL` setzen. Später muss ihre Adresse sowohl in `UPDATE_MANIFEST_URL` der App-Konfiguration als auch in `manifest_url` der Updater-Konfiguration geändert werden; danach den App-Dienst neu starten. Mit `--manifest-url ""` wird die Update-Prüfung deaktiviert.

## Benutzerverwaltung und Anmeldung

Unter **Verwaltung → Benutzer** (`/verwaltung/benutzer/`) legen Administratoren Konten an, ändern Passwörter und vergeben Rechte für Figuren, Räume/Häuser, Orte/Welten, Szenen, eigene Fotos und Löschen. Die Rechte werden auch serverseitig geprüft. Bestehende Konten behalten alle Kreativfunktionen. Administratoren haben sämtliche Rechte; nur sie dürfen Benutzer und Updates verwalten. `/admin/` führt zur neuen Verwaltung im App-Design.

Konten lassen sich deaktivieren; ihre Projekte bleiben erhalten. Der eigene Administrator kann sich hier nicht deaktivieren oder herabstufen. Neue Administratoren werden ausschließlich durch einen angemeldeten Administrator angelegt. Die Ersteinrichtung bleibt nach dem ersten Admin dauerhaft gesperrt. Bei verlorenem Zugang helfen lokal `manage.py createsuperuser` oder `changepassword`.

**Auf diesem Gerät angemeldet bleiben** ist beim Login vorausgewählt. Das geschützte Session-Cookie gilt ein Jahr und wird bei Nutzung erneuert. Abmelden beendet die Sitzung serverseitig. Ohne Häkchen gilt eine Browser-Sitzung. Gelöschte Cookies, privates Surfen, Browserbereinigung und Passwortänderungen können eine erneute Anmeldung erfordern. In Produktion werden Cookies ausschließlich über HTTPS übertragen.

### Als Benutzer anmelden

Unter **Verwaltung → Benutzer → Als … anmelden** kannst du ein aktives Konto ohne dessen Passwort öffnen. Der Hinweis oben zeigt, als wer du arbeitest. **Zurück zum Admin** bringt dich zu deinem ursprünglichen Administratorkonto zurück. Bearbeitungen und Löschungen betreffen tatsächlich das gewählte Konto. In dieser Ansicht ist die Verwaltung gesperrt; zuerst zurückkehren, um erneut das Konto zu wechseln.

Der Wechsel gilt für alle Tabs desselben Browserprofils. Vorher offene Bearbeitungen speichern. Abmelden beendet beide Zugänge in dieser Sitzung. Wird das ursprüngliche Administratorkonto deaktiviert, herabgestuft oder sein Passwort geändert, verfällt die Rückkehrberechtigung.

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

## Entwicklung

Technische Details, Entwicklungsstart, Tests und Release-Erstellung stehen in [DEVELOPMENT.md](DEVELOPMENT.md).
