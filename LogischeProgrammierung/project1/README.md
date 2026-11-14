# Project 1: Starlight

ASP-Encoding für das Starlight-Puzzle aus der LV 621.315. Auf einem quadratischen Gitter kommen pro Zeile und Spalte genau ein Stern und genau eine Wolke hin, Planeten bleiben frei. Leuchtende Planetenhälften brauchen einen sichtbaren Stern auf der passenden Seite, dunkle Viertel dürfen keinen ungeblockten Stern sehen. Die Angabe liegt in Moodle (project01.pdf), das Framework mit vierzehn Beispielinstanzen als starlight.zip.

Abgabe: Dienstag, 8. Dezember 2026, 23:59 über Moodle. Vorher ist ein Zwischenstand gefragt: am 11. November nach der Kurs-Session hochladen, damit es früh Feedback gibt. Der finale Upload braucht die Testtabelle in den Kommentaren, ausgefüllt mit Models und Conflicts von `clingo instanceXX.lp starlight.lp 0 --stats`.

## Die Lösung

[starlight.lp](starlight.lp) hält die struktur vom template, die task-beschreibungen bleiben drin, darunter jeweils unser code:

1. `cell(X,Y)` = alle gitterpunkte ohne planet, über `index` und `not planet(X,Y,_,_,_)`.
2. zwei choice rules `1 = { assign(X,Y,V) : cell(X,Y) } :- index(X), value(V).` (und gleich für spalten). `value/1` aus dem template spart die vier einzelnen regeln. ein integrity constraint verbietet stern + wolke auf einer zelle.
3. `reach/7` in zwei regeln: start an der nachbarzelle vom planet, dann weiter solange auf der aktuellen zelle keine wolke liegt. planeten und rand stoppen automatisch weil dort kein `cell/2` existiert.
4. dunkle seiten: constraint gegen jeden sichtbaren stern. helle seiten: hilfsprädikat `lit/4` + constraint `not lit(...)`.

warum so: generate (choice rules) und test (constraints) sind sauber getrennt. die erste version hatte bei task 4 eine choice rule `1 { assign(..,1) : reach(..) }`, die hätte selbst sterne erzeugen können und war nur wegen der kardinalitäten trotzdem richtig. drei varianten (alt, `lit/4`, `#count`-aggregat) auf allen 14 instanzen verglichen: alle lösen praktisch ohne suche (0-7 conflicts), also hab ich die lesbarste genommen.

## Ausführen

clingo installieren (Version 5.8.x, etwa über conda-forge oder pip), dann die Instanzen aus starlight.zip dazulegen:

```sh
clingo instance08.lp starlight.lp 0 --stats
```

Erwartung: genau ein Answer Set pro Instanz. Für instance08 kommt damit genau die Belegung aus Abbildung 1 der Angabe heraus.

## Test-Report

alle 14 instanzen haben genau ein model und stimmen zelle für zelle mit den referenzlösungen in den instanz-kommentaren überein. conflicts in der tabelle sind von clingo 5.8.3 (python bindings), auf einer anderen version können die minimal anders sein, die models nicht.

## Anmerkungen

- gruppe: raphael bleier, fabio schmickl, devis mele, alle drei stehen im header von starlight.lp und starlight_draft.lp. jeder von uns muss selber eine kopie hochladen
- vorabversion = [starlight_draft.lp](starlight_draft.lp), nur task 1 + 2 (cell/2 und die choice rules). vor dem upload in starlight.lp umbenennen, moodle will genau den namen. war eigentlich am 11.11. nach der session fällig
- Die vierzehn Instanzen aus starlight.zip liegen nicht im Repo, sie gehören zum Framework der LV. Für eigene Tests: Zip entpacken und wie oben aufrufen.
