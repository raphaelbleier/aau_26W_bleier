# Project 1: Starlight

ASP-Encoding für das Starlight-Puzzle aus der LV 621.315. Auf einem quadratischen Gitter kommen pro Zeile und Spalte genau ein Stern und genau eine Wolke hin, Planeten bleiben frei. Leuchtende Planetenhälften brauchen einen sichtbaren Stern auf der passenden Seite, dunkle Viertel dürfen keinen ungeblockten Stern sehen. Die Angabe liegt in Moodle (project01.pdf), das Framework mit vierzehn Beispielinstanzen als starlight.zip.

Abgabe: Dienstag, 8. Dezember 2026, 23:59 über Moodle. Vorher ist ein Zwischenstand gefragt: am 11. November nach der Kurs-Session hochladen, damit es früh Feedback gibt. Der finale Upload braucht die Testtabelle in den Kommentaren, ausgefüllt mit Models und Conflicts von `clingo instanceXX.lp starlight.lp 0 --stats`.

## Die Lösung

[starlight.lp](starlight.lp) hält die Struktur des Templates bei und füllt die vier Implementierungsaufgaben:

1. `cell(X,Y)` sind alle Gitterpunkte ohne Planet, abgeleitet über `index` und negative Prüfung gegen `planet(X,Y,_,_,_)`.
2. Vier Choice Rules mit Kardinalität 1: pro Zeile und pro Spalte je genau eine Wolke und genau ein Stern, alles nur auf leeren Zellen. Ein Integrity Constraint verbietet Stern und Wolke auf derselben Zelle.
3. `reach/7` wächst in zwei Regeln vom Planeten aus: die erste leitet die Nachbarzelle in Richtung `(DX,DY)` ab, die zweite läuft weiter, solange die vorhergehende Zelle keine Wolke enthält. Nur leere Zellen werden betreten, Planeten und der Rand stoppen die Sichtlinie zusätzlich.
4. Zwei Constraints: dunkle Seiten (`S = -1`) vertragen keinen sichtbaren Stern, leuchtende Seiten (`S = 1`) brauchen mindestens einen Stern in den erreichten Zellen.

Am Ende steht `#show assign/3.`, damit clingo nur die Belegung ausgibt.

## Ausführen

clingo installieren (Version 5.8.x, etwa über conda-forge oder pip), dann die Instanzen aus starlight.zip dazulegen:

```sh
clingo instance08.lp starlight.lp 0 --stats
```

Erwartung: genau ein Answer Set pro Instanz. Für instance08 kommt damit genau die Belegung aus Abbildung 1 der Angabe heraus.

## Test-Report

Alle vierzehn Instanzen laufen mit genau einem Modell durch. Die Tabelle in starlight.lp ist ausgefüllt; die Conflicts-Zahlen stammen von clingo 5.8.3 (Python-Bindings, Standardkonfiguration, `0` = alle Modelle). Auf einer anderen clingo-Version können sie minimal abweichen, die Modelle nicht.

## Anmerkungen

- Die Lösung ist als Einzelarbeit eingetragen (Raphael Bleier im Kommentar-Header). Falls eine Gruppe bis zur Abgabe gebildet wird, die Namen dort ergänzen.
- Die vierzehn Instanzen aus starlight.zip liegen nicht im Repo, sie gehören zum Framework der LV. Für eigene Tests: Zip entpacken und wie oben aufrufen.
- Alle Instanzen wurden zusätzlich gegen die offiziellen Referenzlösungen geprüft, die als Kommentare in den Instanzdateien stecken: der eindeutige Answer Set stimmt in allen vierzehn Fällen Zelle für Zelle überein.
