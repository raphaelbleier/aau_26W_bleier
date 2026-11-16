# Blatt 07

Abgabe und Kreuzeln: 23.11.2026, 12:00. Das Kreuzeln erfolgt zusätzlich zum PDF-Upload im Assignment Administration System.

[Lösung](loesung_blatt07.pdf) · [Erklärung](erklaerung_blatt07.pdf) · [LaTeX-Quelle](blatt07.tex)

## Exercise 7.1

Ich rechne die Simplex-Pivots von Hand durch und wähle nach Bland immer den kleinsten zulässigen Variablenindex, auch beim Gleichstand im Quotiententest. Die ersten sechs Pivots bewegen die Ecke nicht. Erst der siebte erhöht den Zielfunktionswert auf 1 und liefert die Optimallösung (1, 0, 1, 0, 3/2, 0, 0). In der Angabe heißen zwei Basiszeilen x5. Ich behandle die zweite als x6, damit die Basis drei verschiedene Variablen enthält; alle Koeffizienten bleiben dabei unverändert.

## Exercise 7.2

Die drei primalen Punkte liefern 7, 10 und 4, die dualen 12, 16 und 16. Jede Gleichung und Ungleichung wird einzeln geprüft. Alle neun Punktpaare erfüllen die schwache Dualität.

## Exercise 7.3

Aus einem terminierenden Simplex-Dictionary konstruiere ich die duale Lösung. Ihre Zulässigkeit folgt aus den reduzierten Kosten, ihre Optimalität aus der Wertgleichheit und schwacher Dualität. Abhängige Gleichungszeilen werden gesondert behandelt.

Die Classroom-Aufgabe steht nur im Erklär-PDF. Für den Upload verwende ich Bleier_sheet_7.pdf, das denselben Inhalt wie die schlichte Lösung enthält und damit die im Kursablauf verlangte Benennung erfüllt. Beide PDFs entstehen aus derselben Quelle; dafür blatt07.tex mit explainmode=0 beziehungsweise explainmode=1 mit pdflatex bauen. Die englischen Rechenschritte stehen in beiden PDFs, deutsche Erklärkästen und die Verlaufsgrafik nur in der Erklärung.
