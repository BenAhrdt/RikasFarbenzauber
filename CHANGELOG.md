# Änderungen

## 0.5.7 – 7. September 2026

- Vier neue K-Pop-/Anime-inspirierte Figurenideen und 16 kombinierbare Optionen für Frisuren, Kleidung, magische Accessoires und Bühnenausstattung.
- Zwölf neue Raumobjekte: Anime-Poster, Lightstick, Bühnenpodest, Scheinwerfer, Keyboard, Kopfhörer, Papierlaterne, Ramen-Schale, Katzen-Plüschtier, Gamecontroller, Schminkspiegel und Sternen-Lichterkette.
- Figuren-Vorschau überlagert beim Scrollen auf Handy und Tablet nicht mehr das Druckmenü.
- Drucken / PDF erzeugt eine fertige, einseitige A4-PDF in Hoch- oder Querformat mit proportional eingepasstem Bild, statt die Editor-Webseite durch den Browser umbrechen zu lassen.

- PDF-Download als Ersatz bei gesperrten Vorschaufenstern, auch wenn der Browser das Öffnen mit einem Fehler ablehnt.
- Geprüft: Speichern und Wiederöffnen, bestehende Figuren, Touch-Bedienung, mobile Layouts, Bild-/PDF-Export sowie Update und Rücknahme bei Fehlern.

## 0.5.6

- Schreibrecht der App-Gruppe im Update-Verzeichnis explizit gesetzt; umask darf Update-Anforderungen nicht verhindern.
- Sofortige sichtbare Rückmeldung nach Update-Bestätigung und Hinweis bei wartendem Update-Dienst.
- Fehler beim Anlegen der Update-Anforderung werden im Dienstprotokoll aufgezeichnet.

## 0.5.5

- Hoch-/Querformat direkt im Editor wählbar; Räume, Orte und Szenen starten im Querformat.
- Druckfläche passt vollständig und proportional auf eine A4-Seite.

## 0.5.4

- Lokaler Zugang bleibt immer über die LXC-IP auf Port 8080 erreichbar.
- Installation fragt optional nach HTTPS-Freigabe, ohne Proxy-IP oder eigene Zertifikatsverwaltung.
- HTTPS-Adressen unter Verwaltung → Zugangsadressen sofort ändern; eigener Reverse-Proxy übernimmt TLS.
- Separate Secure-Cookies für HTTPS und lokale HTTP-Sitzungen.

## 0.5.3

- Standardinstallation richtet Caddy und HTTPS automatisch ein; nur die Domain wird abgefragt.
- Externer Reverse-Proxy ist optional statt Voraussetzung.

## 0.5.2

- Installation direkt nach Git Clone mit `./install.sh`; Domain und Proxy-IP werden abgefragt.
- `./update.sh` für manuelle Updates und als gemeinsamer Einstieg des automatischen Update-Dienstes.
- README auf Installation und Betrieb konzentriert; Entwicklungsdetails nach DEVELOPMENT.md verschoben.

## 0.5.1

- Als ausgewählter Benutzer anmelden und sicher zum ursprünglichen Admin zurückkehren.
- Eigene Verwaltung im Design der Kreativwerkstatt mit individuellen Benutzerrechten.
- Dauerhafte Anmeldung auf vertrauten Geräten.
- Versionierte LXC-Installation, Update-Prüfung, Fortschritt und Datenbank-Rollback.
- Installation per Git Clone sowie Veröffentlichung von Tags und Release-Paketen dokumentiert.
- Figuren, Räume, Orte, Szenen und eigene Fotos mit geschützten persönlichen Projekten.
