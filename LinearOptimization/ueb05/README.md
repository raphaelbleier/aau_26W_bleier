# Exercise sheet 5

Auf diesem Blatt geht es um den nächsten Simplex-Schritt nach dem Dictionary von Blatt 4. Aufgabe 5.1 hat zwei optimale Ecken, Aufgabe 5.2 ist ein Beweis für eine rechte Seite aus lauter Nullen, und Aufgabe 5.3 wählt in Python die eintretende und die austretende Variable. Abgabe und Kreuzeln sind am 09.11.2026 um 12:00. Die Classroom-Aufgabe bleibt draußen.

Für die Abgabe liegen [Bleier_sheet_5.pdf](Bleier_sheet_5.pdf) und [Bleier_sheet_5.py](Bleier_sheet_5.py) unter den verlangten Dateinamen bereit. Das PDF ist eine Kopie von [loesung_blatt05.pdf](loesung_blatt05.pdf). In [erklaerung_blatt05.pdf](erklaerung_blatt05.pdf) stehen dieselben Rechenschritte, dazu deutsche Erklärkästen und eine Skizze der beiden Pivotwege. Beide Fassungen entstehen aus [blatt05.tex](blatt05.tex). Hochgeladen wurde nichts. Gekreuzelt auch nicht.

## 5.1

Im Startdictionary haben `x1` und `x2` beide reduzierte Kosten 1, weil die Zielfunktion in beide Richtungen gleich steil ist. Die Regel mit dem größten Wert nimmt bei Gleichstand den kleineren Index, also `x1`. Der erste Pivot läuft entlang der `x1`-Achse nach `(8, 0)`, der zweite auf die Ecke `(26/3, 4/3)`. Dort ist der Wert 10.

Wählt man am Anfang stattdessen `x2`, läuft der erste Schritt nach `(0, 5)` und der zweite nach `(5/2, 15/2)`. Wieder 10. Der Punkt ist ein anderer, also ist die Optimallösung nicht eindeutig.

Grafisch liegt die Niveaulinie `x1 + x2 = 10` genau auf der dritten Nebenbedingung, deshalb ist die ganze Kante zwischen den beiden Ecken optimal und nicht bloß ein einzelner Eckpunkt. Im optimalen Dictionary sieht man denselben Sachverhalt: eine Nichtbasisvariable hat reduzierte Kosten 0, und der Quotiententest erlaubt einen positiven Schritt. Sind alle reduzierten Kosten strikt negativ, gibt es keine zweite Lösung.

## 5.2

Der Nullvektor ist immer zulässig, weil `A` mal 0 die Null liefert und die Vorzeichen passen. Gibt es einen zulässigen Punkt mit positivem Zielfunktionswert, darf man ihn mit jedem `t` größer oder gleich 0 strecken. Der Strahl bleibt in der zulässigen Menge, und der Wert geht nach unendlich. Sonst ist 0 optimal. Ein positiver Kostenkoeffizient allein beweist die Unbeschränktheit nicht, wenn die zugehörige Richtung sofort eine Zeile verletzt.

## 5.3

`choose_entering_variable_index` nimmt die Nichtbasisvariable mit den größten reduzierten Kosten. Sind alle höchstens 0, mit Toleranz `1e-9`, kommt `None` zurück. `choose_leaving_variable_index` macht den Quotiententest auf den positiven Einträgen der Spalte. Kein positiver Eintrag heißt, dass das LP in dieser Richtung unbeschränkt ist, und die Funktion gibt `None` zurück. Bei Gleichstand gewinnt der erste Index in der aktuellen Reihenfolge von `N` bzw. `B`.

Für Example 2.2 tritt `x3` ein (Index 2) und `x5` aus (Index 4). Das ist derselbe erste Pivot wie in Lecture 4, mit Zielfunktionswert 24 nach dem Tausch. Die Datei enthält auch `initial_simplex_dictionary` aus Blatt 4, weil die Abgabe alle drei Funktionen in einer einzigen Python-Datei verlangt.

## Ausführen

Benötigt werden Python 3 und NumPy. Aus diesem Ordner:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy
python Bleier_sheet_5.py
python -m unittest -v test_sheet5.py
```

Die Tests prüfen Example 2.2 gegen die beiden Vorlesungspivots bis `z = 26`, außerdem ein optimales Dictionary, eine unbeschränkte Spalte, beide Gleichstandsregeln und die Toleranz `1e-9`. Die beiden Funktionen führen selbst keinen Pivot aus. Den Tausch rechnet nur der Test nach, als Gegenprobe zur Vorlesung.
