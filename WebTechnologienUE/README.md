# 621.901 Web-Technologien UE

Meine Lösungen zu den Übungsblättern 1 bis 8 (WS 2026/27, AAU Klagenfurt). Jedes Blatt hat einen eigenen Ordner, darin pro Aufgabe ein `exN`-Ordner. Textantworten, Erklärungen und Testausgaben stehen in `Antworten_AssignmentXX.pdf` im jeweiligen Ordner.

## Blätter

Alle acht Blätter sind gelöst; offen ist nur die Projekt-Präsentation (Gruppe). Zu jedem Blatt gibt es eine eigene README.

| Blatt | Thema | Inhalt |
|---|---|---|
| [Assignment01](Assignment01) | HTTP, HTML, CSS | DevTools-Messungen, Apache, HTML-Seiten, Tabelle, Formular, CSS-Selektoren, Flexbox-Layout, Responsive |
| [Assignment02](Assignment02) | JS, DOM | Quiz-Screenshot, Zahlenraten mit prompt/alert, DOM-Baum (Mermaid), Glaspreis, Event Bubbling, Galerie prev/next |
| [Assignment03](Assignment03) | JS, DOM, Events | Zahlenraten im DOM, editierbare Seite, Galerie mit Slideshow, Puzzle |
| [Assignment04](Assignment04) | Closures, Prototypes, Klassen | Warenkorb (shopA/B/C), Higher-Order, Closure, Currying, Image/Video mit Prototypes und Klassen |
| [Assignment05](Assignment05) | Async | Callbacks, Promises, async/await, XMLHttpRequest, fetch |
| [Assignment06](Assignment06) | Node.js, Express, PostgreSQL | Routen, Produkt-API, DB-Anbindung, Session-Login |
| [Assignment07](Assignment07) | JWT, REST | JWT-Login, REST-Service mit Tags/Likes/Suche, REST-Spezifikation (OpenAPI) |
| [Assignment08](Assignment08) | Angular 22 | Lernzettel, Homes-App aus dem offiziellen Tutorial |

## Ausführen

**Blatt 1 bis 5** sind statische Seiten. Die meisten gehen direkt im Browser. Für A1 Ex2 und A5 Ex4/5 braucht es einen Webserver (bei mir Apache, DocumentRoot `/var/www/html`), weil XHR/fetch über `file://` nicht gehen. A4 Ex3–5 laufen mit `node datei.js`.

**Blatt 6 und 7** brauchen Node und PostgreSQL:

```bash
cd Assignment06/ex3/db_import
psql -d postgres -f createDB.sql   # siehe PDF: \connect muss kleingeschrieben sein
cd ..
npm install
node server.js                     # http://localhost:3000
```

Die `config.json` verbindet sich über den Unix-Socket (`/var/run/postgresql`) mit meinem Linux-User ohne Passwort. Auf einem anderen Rechner `host`, `user` und `password` anpassen. Zum Testen liegt in jedem ex-Ordner eine `postman_collection.json`.

**Blatt 8** braucht Node 22.22.3 oder neuer:

```bash
cd Assignment08/ex2/homes-app
npm install
npm run api     # json-server auf :3000
npm start       # zweites Terminal, App auf :4200
```

`node_modules` ist nicht im Repo, also überall zuerst `npm install`.
