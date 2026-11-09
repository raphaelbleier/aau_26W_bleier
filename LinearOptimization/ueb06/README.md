# Exercise sheet 6

Auf diesem Blatt wird der Simplex-Schritt selbst zum Gegenstand: Aufgabe 6.1 beweist, dass ein Pivot eine Basis wieder in eine Basis überführt, Aufgabe 6.2 baut mit künstlichen Variablen eine zulässige Startbasis (Two-Phase-Simplex), und Aufgabe 6.3 verpackt Dictionary, Entering/Leaving und Pivot in eine Simplex-Schleife für Example 2.2. Abgabe und Kreuzeln sind am 16.11.2026 um 12:00. Die Classroom-Aufgabe (Bland's Rule) bleibt wie auf Blatt 5 draußen und steht als Lernzusatz im Erklär-PDF.

Für die Abgabe liegen [Bleier_sheet_6.pdf](Bleier_sheet_6.pdf) und [Bleier_sheet_6.py](Bleier_sheet_6.py) unter den verlangten Dateinamen bereit. Das PDF ist eine Kopie von [loesung_blatt06.pdf](loesung_blatt06.pdf). In [erklaerung_blatt06.pdf](erklaerung_blatt06.pdf) stehen dieselben Rechenschritte, dazu deutsche Erklärkästen. Beide Fassungen entstehen aus [blatt06.tex](blatt06.tex). Hochgeladen wurde nichts. Gekreuzelt auch nicht.

## Exercise 6.1

Ein Pivot löst die Zeile der austretenden Variablen nach der eintretenden auf und setzt das Ergebnis in die übrigen Zeilen ein. Das ist bloßes Umformen, ändert die Lösungsmenge also nicht: Altes Dictionary, neues Dictionary und `Ax = b` beschreiben dieselben Vektoren. Zu festem `x_N` legt das neue Dictionary `x_B` deshalb eindeutig fest, und jedes Paar aus dem Dictionary erfüllt `A_B x_B + A_N x_N = b`.

Daraus folgt die Invertierbarkeit von `A_B`: Gäbe es einen nonzero-Vektor `y` mit `A_B y = 0`, könnte man ihn zu jeder Lösung dazuzählen und bekäme eine zweite für dieselbe rechte Seite. Widerspruch zur Eindeutigkeit. Der Kern ist also nur `{0}`, die Matrix invertierbar, `B` eine Basis. Für diese Aussage reicht `a(i0,q0) ≠ 0`; die Positivität aus dem Quotiententest braucht erst die Zulässigkeit der neuen Ecke.

## Exercise 6.2

Beide Nebenbedingungen sind `>`-Ungleichungen, der Ursprung verletzt sie, also gibt es keine zulässige Schlupfbasis. Künstliche Variablen `x5`, `x6` machen die Startbasis `{5, 6}` mit `x5 = x6 = 3` zulässig; minimiert wird `w = x5 + x6`.

Erster Pivot: `x1` tritt ein (reduzierte Kosten 3, Gleichstand mit `x2` geht an den früheren Index), Quotienten 3/2 gegen 3, `x5` tritt aus. Zweiter Pivot: `x2` tritt ein (3/2 gegen 1/2), Quotienten 3 gegen 1, `x6` tritt aus. Danach sind beide künstlichen Variablen Nichtbasisvariablen und `w = 0` ist optimal, also ist das Original-LP zulässig.

Die Startlösung für den Simplex auf dem Originalproblem ist `x = (1, 1, 0, 0)` mit Basis `{1, 2}`. Die reduzierten Kosten `-1/3` und `-1/3` sind beide negativ, die Ecke ist sogar schon optimal mit `z = -2`.

## Exercise 6.3

`initial_simplex_dictionary` heißt jetzt `create_simplex_dictionary`. Der Name passt besser, weil Exercise 6.1 zeigt, dass ein Pivot äquivalent zum Neu-Zerlegen von `Ax = b` ist, und genau das macht die Funktion. Der Tausch ersetzt den austretenden Index an seiner Position in `B`, dann kommt ein frischer Aufruf.

`solve_simplex` läuft so lange, bis `choose_entering_variable_index` `None` liefert (alle reduzierten Kosten höchstens 0, Abbruchkriterium laut Blatt). Liefert `choose_leaving_variable_index` `None`, ist das LP unbeschränkt. Ein Start mit negativem `b_bar` wird vorher abgelehnt, der Iterationszähler begrenzt die Schleife.

Für Example 2.2 braucht es zwei Pivots: `x3` tritt ein, `x5` aus (`z = 24` auf der Ecke `(0, 0, 4)`), dann `x2` ein, `x6` aus. Ende bei `x = (0, 1, 4, 7, 0, 0)` mit `z = 26` und reduzierten Kosten `(-9/2, -5/2, -1)`.

## Ausführen

Benötigt werden Python 3 und NumPy. Aus diesem Ordner:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy pytest
python Bleier_sheet_6.py
python -m pytest test_sheet6.py -q
```

Die Tests prüfen die Startwerte vom Blatt 5, beide Pivot-Entscheidungen, das Endergebnis `z = 26` nach genau zwei Iterationen, den sofortigen Abbruch an einer optimalen Basis, die Unbeschränktheits-Erkennung und die Zurückweisung einer unzulässigen Startbasis.
