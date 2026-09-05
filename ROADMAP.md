# Entwicklungsplan

## Phase 1 – Figuren (erweiterte Werkstatt umgesetzt)

Login, persönliche serverseitige Projekte, drei eigene SVG-Varianten, färbbare Regionen, Touch-Verschieben, Größenänderung, Drehung, Spiegeln, Wiederöffnen, PNG/SVG und einfache Ausmal-/Druckansicht sind vorhanden.

Bereits ergänzt: 23 unabhängige Auswahlfelder, 5 Körperregler, 12 Farben, Startideen, Zufallsfunktion und Undo/Redo; alte Figuren bleiben kompatibel.

Nächste Iteration: mehr konkrete Kleidungsstücke und grafische Auswahlkacheln je Kategorie; Tests auf echten Tablets; bessere Figurenkomposition und Barrierefreiheit. Autosave mit sichtbarem Speicherzustand, Wiederherstellung und Umgang mit Versionskonflikten ergänzen. Keine unbemerkte Überschreibung auf anderen Geräten.

## Phase 2 – Räume und Häuser (erste Version umgesetzt)

Bereits vorhanden: 32 eigene SVG-Assets, Raum-/Hausvorlagen, Objektliste, Ebenen, Farbregionen, Touch-/Maus-Verschieben, Kopieren/Löschen und Undo/Redo.

Weiter ausbauen: Versionierte Bibliothek eigener SVG-Möbel, Fenster, Türen und Dekoration. Mehrfachobjekte auswählen, ziehen, skalieren, drehen, spiegeln, duplizieren und nach Bestätigung löschen. Ebenenreihenfolge, Zoom, Schwenken und große Touch-Griffe. Raum- und Hausvorlagen als eigene Projektarten speichern.

## Phase 3 – Orte und Welten (erste Version umgesetzt)

Bereits vorhanden: Garten- und Schlossvorlagen, Naturbibliothek, Hintergrund/Boden und eigene gespeicherte Orte.

Weiter ausbauen: Wald, Strand, Stadt und Fantasieorte. Hintergrundregionen und größere Arbeitsflächen, Pflanzen und Architektur. Bibliothekskategorien und Vorschau-Caching für viele Objekte. Dokumentmigrationen und Performance-Budgets festlegen.

## Phase 4 – Szenen (erste Version umgesetzt)

Bereits vorhanden: eigene Figuren und gespeicherte Orte als unabhängige Kopien kombinieren; vollständige Projekte als Grundlage übernehmen.

Weiter ausbauen: Beim Einfügen zunächst eine versionierte Kopie verwenden, damit spätere Änderungen am Original bestehende Szenen nicht unbemerkt verändern. Später optional verknüpfte Instanzen mit ausdrücklich angebotener Aktualisierung. Besitzerprüfung auch für alle referenzierten Projekte.

## Phase 5 – Malen und Ausmalen

Teilweise farbige Druckausgabe über gespeicherte Auswahl pro Objekt und Farbregion. Favoritenfarben, zuletzt verwendete Farben, Stift-/Freihandebenen, Radierer und Füllwerkzeuge. Alle Werkzeuge mit Undo/Redo, klarer Trennung von Konturen und Füllungen und nachvollziehbarem Export.

## Phase 6 – Export und Komfort

Mehrseitige A4-Ausgabe, Querformat, wählbare PNG-Auflösung, standardisierte PDF-Erzeugung, Druckvorschau und Schnittmarken. PWA mit geprüfter Installation und optionalem Offline-Editor samt expliziter Synchronisationswarteschlange. Keine privaten API-Antworten in gemeinsamem Service-Worker-Cache. Projektarchiv, Suche, Papierkorb und Backup-Oberfläche für Eltern.

## Durchgehend

Sicherheitsupdates, Tests gegen unberechtigte Zugriffe, Datenbankmigrationen, Backup-Wiederherstellung und Tests auf iPad/Android. Neue Assets ausschließlich selbst erstellen oder klar passend lizenzieren. Bei wachsender Nutzerzahl PostgreSQL, Pagination, Nutzungsgrenzen und Monitoring ergänzen.

## Foto-Erweiterung (erste Version umgesetzt)

Eigene Foto-Gegenstände und Bilderrahmen, Galerie-/Kamera-Dateiauswahl, Zuschneiden, private serverseitige Fotobibliothek, Ersetzen, Rahmenfarbe und eingebettete PNG-/SVG-Exporte sind vorhanden. Ausmalbilder lassen Fotoflächen weiß. Nächste Schritte: Fotoverwaltung mit sicherem Löschen ungenutzter Fotos, manuelles Freistellen, HEIC-Unterstützung und später optional eine lokal betriebene Umwandlung in gezeichnete Gegenstände.
