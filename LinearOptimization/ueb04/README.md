# Exercise sheet 4

Die Aufgaben 4.1 und 4.2 führen einen zulässigen Punkt schrittweise zu einer Basislösung. Aufgabe 4.3 baut das Anfangs-Dictionary eines LP in Python auf. Abgabe und Kreuzeln sind am 02.11.2026 um 12:00. Die Classroom-Aufgabe steht als Lernzusatz nur in der Erklärung, nicht in der schriftlichen Lösung.

Für die Abgabe liegen [Bleier_sheet_4.pdf](Bleier_sheet_4.pdf) und [Bleier_sheet_4.py](Bleier_sheet_4.py) unter den verlangten Dateinamen bereit. Das PDF ist eine Kopie von [loesung_blatt04.pdf](loesung_blatt04.pdf). [erklaerung_blatt04.pdf](erklaerung_blatt04.pdf) enthält dieselben Rechenschritte mit deutschen Erklärkästen und einer Übersicht zu den beiden Richtungsänderungen. Beide Fassungen entstehen aus [blatt04.tex](blatt04.tex). Es wurde nichts auf Moodle hochgeladen und nichts gekreuzelt.

## 4.1

Zuerst prüfen wir den Punkt in beiden Gleichungen und kontrollieren seine Vorzeichen. Die Matrix hat Rang zwei. Eine Basis enthält deshalb zwei unabhängige Spalten; alle übrigen Variablen sind bei einer Basislösung null. Der gegebene Punkt hat vier positive Komponenten und ist somit zulässig, aber nicht basic.

Die vorgegebene Richtung erfüllt `Ay = 0`. Wenn wir ein Vielfaches davon abziehen, bleibt `Ax = b` erhalten. Die Nichtnegativität begrenzt die Schrittlänge. Für einen positiven Schritt schrumpfen hier nur die dritte und vierte Komponente. Das kleinere Verhältnis liefert `alpha = 1/4` und damit `x_tilde = (15/4, 3/2, 0, 3/4)`.

## 4.2

Für den zweiten Schritt verwenden wir nur noch die Spalten mit positivem Eintrag im neuen Punkt. Eine passende Richtung ist `(7, -2, 0, 3)`. Die dritte Komponente bleibt dadurch null. Mit `epsilon = 1/4` wird zusätzlich die vierte Komponente null, und es bleibt `(2, 2, 0, 0)`. Die Spalten eins und zwei sind unabhängig, also ist dieser Punkt basic feasible. Der Zwischenpunkt mit drei positiven Komponenten ist es noch nicht.

## 4.3

Die Funktion speichert das Dictionary in der Form `x_B = b_bar - A_bar @ x_N`. Das Minus gehört zur Gleichung, nicht zur gespeicherten Matrix. Für die Zielfunktion gilt `z = z_bar + c_bar_N @ x_N`.

Die Basis aus den drei Schlupfvariablen ist die Einheitsmatrix. Deshalb bleiben die rechte Seite und die ersten drei Spalten bei der Transformation unverändert. Die Basiskosten sind null. Der konstante Zielfunktionswert ist ebenfalls null, die reduzierten Kosten sind `(-1, 2, 6)`. Der vollständige Startpunkt lautet `(0, 0, 0, 10, 8, 6)` und ist zulässig.

Im Python-Aufruf sind die Indizes nullbasiert: Die mathematische Basis `(4, 5, 6)` wird als `[3, 4, 5]` übergeben. `np.linalg.solve` löst die beiden Systeme direkt, statt eine Inverse zu bilden. Bevor die Funktion das Dictionary berechnet, prüft sie, ob die Dimensionen der Eingaben zusammenpassen und die Basis genau die benötigte Anzahl verschiedener gültiger Spaltenindizes enthält. Eine singuläre Basis löst einen Fehler aus; eine invertierbare Basis mit negativen Basiswerten liefert dagegen ein Dictionary mit `is_feasible=False`.

## Ausführen

Benötigt werden Python 3 und NumPy. Aus diesem Ordner:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy
python Bleier_sheet_4.py
python -m unittest -v test_sheet4.py
```

Die neun Tests prüfen das Beispiel, eine anders geordnete Nichtidentitätsbasis, die Gleichungen und die Zielfunktion nach Rekonstruktion, unzulässige und degenerierte Basislösungen sowie fehlerhafte Eingaben. Die Tests prüfen außerdem, dass die Eingabedaten unverändert bleiben, während die Gegenprobe mit einer anderen Basis sicherstellt, dass die Funktion nicht bloß den einfachen Fall mit der Einheitsmatrix nachbildet, sondern auch bei nichtverschwindenden Basiskosten die rechte Seite, die Matrix und die reduzierten Kosten richtig transformiert. Die Funktion baut nur das Anfangs-Dictionary. Sie führt keine Pivotfolge und keine Optimierung aus.
