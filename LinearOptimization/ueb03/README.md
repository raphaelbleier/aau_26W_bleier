# Exercise sheet 3

Abgabe und Kreuzeln: 26.10.2026, 12:00. Die schriftlichen Aufgaben sind 3.1 bis 3.3. Die Nummerierung in 3.3 beginnt wie auf dem Blatt mit Punkt 4.

Die [Lösung](loesung_blatt03.pdf) enthält Angabe, Rechenschritte und Proben auf Englisch. Für den geforderten Uploadnamen liegt dieselbe Datei als [Bleier_sheet_3.pdf](Bleier_sheet_3.pdf) vor. Die [Erklärung](erklaerung_blatt03.pdf) ergänzt deutsche Erklärkästen und Skizzen. Beide Fassungen entstehen aus [blatt03.tex](blatt03.tex), damit die Rechnungen gleich bleiben.

## Aufgabe 3.1

Wir lesen die Koeffizienten der beiden Gleichungen zeilenweise in die Matrix ein. Als Basis wählen wir die Spalten 4 und 5. Die bilden schon die Einheitsmatrix. Die übrigen drei Spalten gehören zur Nichtbasis, deren Werte wir auf der rechten Seite einsetzen können, um die beiden Basisvariablen zu bestimmen, ohne dafür noch eine weitere Matrix invertieren zu müssen.

Damit ist `x4 = 4 - x1 - 2*x2 - x3` und `x5 = 5 - 2*x1 - x2 - 2*x3`. Das löst zunächst nur die Gleichungen. Für eine zulässige Lösung dürfen weder die gewählten Nichtbasiswerte noch die berechneten Basiswerte negativ sein. Die Wahl null für alle Nichtbasisvariablen liefert die zulässige Basislösung `(0, 0, 0, 4, 5)`.

## Aufgabe 3.2

Jede obere Schranke bekommt eine nichtnegative Schlupfvariable. Am Ursprung sind deren Werte `(3, 2, 7)`, der Zielfunktionswert ist null. Dann stellen wir jede Gleichung nach ihrer Schlupfvariable um und erhalten das erste Dictionary.

Wenn nur `x1` wächst, steigt `x4`, während `x5` und `x6` fallen. Entscheidend ist `x5`: Bei `x1 = 2` erreicht sie als erste den Wert null. Weiter dürfen wir in dieser Richtung nicht gehen, weil sonst die zweite Nebenbedingung verletzt würde. Eine Erhöhung nur von `x2` oder nur von `x3` wäre kein verbessernder Schritt. Beide haben negative Koeffizienten in der ursprünglichen Zielfunktion.

## Aufgabe 3.3

Beim Pivot tauschen wir `x1` und `x5`. Wir lösen die zweite Zeile nach `x1` auf und setzen diesen Ausdruck in die beiden anderen Basiszeilen ein. Die neue Zielfunktion lautet `z = 2 - x2 - x3 - x5`.

Hier steht die obere Schranke direkt. Keine zulässige Lösung kann mehr als 2 erreichen, weil alle drei abgezogenen Variablen nichtnegativ sind. Bei der Basislösung sind sie null. Damit ist `(x1, x2, x3) = (2, 0, 0)` optimal, mit Schlupfwerten `(5, 0, 3)` und Zielfunktionswert 2. Das Optimum ist eindeutig, da Gleichheit nur möglich ist, wenn alle drei abgezogenen Variablen null sind.

## Bauen und Abgeben

Die Quelle braucht pdfLaTeX mit AMS-Mathematik, Babel, TikZ und tcolorbox. Im Blattordner lassen sich die zwei Fassungen mit den folgenden Befehlen bauen, wobei der Modus null die Erklärkästen ausblendet und der Modus eins dieselben Rechnungen zusammen mit den zusätzlichen Kästen und Skizzen setzt:

```bash
pdflatex -jobname=loesung_blatt03 '\def\explainmode{0}\input{blatt03.tex}'
pdflatex -jobname=erklaerung_blatt03 '\def\explainmode{1}\input{blatt03.tex}'
cp loesung_blatt03.pdf Bleier_sheet_3.pdf
```

Die Rechnungen wurden symbolisch geprüft; eine getrennte Eckenaufzählung und ein LP-Solver bestätigen das Optimum. Classroom task 3.1 ist laut Kursworkflow nicht schriftlich abzugeben und steht deshalb nur als Lernzusatz im Erklär-PDF. Der geforderte Dateiname ist vorbereitet. Kreuzeln und Moodle-Upload sind damit noch nicht erledigt.

Grundlage: Exercise sheet 3 (Moodle, Exercise 03) und Lecture 3 vom 13.10.2026, Abschnitt 2.2 zur Dictionary-Schreibweise. Der Kursworkflow verlangt vor Montag 12:00 sowohl Kreuzeln als auch PDF-Upload. Hier werden keine Lehrunterlagen weiterveröffentlicht.
