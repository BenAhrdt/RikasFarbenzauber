# Änderungen

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
