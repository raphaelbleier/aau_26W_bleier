# Blatt 08

Abgabe und Kreuzeln: 30.11.2026, 12:00. Das Kreuzeln erfolgt zusätzlich zum PDF-Upload im Assignment Administration System.

[Lösung](loesung_blatt08.pdf) · [Erklärung](erklaerung_blatt08.pdf) · [LaTeX-Quelle](blatt08.tex)

## Exercise 8.1

Das LP scheitert schon an den ersten beiden Nebenbedingungen. Die verlangen x2 ≥ x1 − 1 und x2 ≤ x1 − 2, also zwei parallele Geraden, deren Halbebenen voneinander wegzeigen. Damit ist das Primale unzulässig. Das duale Problem hat denselben Widerspruch, nur mit vertauschten Zahlen: 0 ≥ 1. Also ist auch das Duale unzulässig. Mit der Zusatznebenbedingung x1 ≤ −1 wird das Duale zulässig, und y3 kann entlang (0, 0, 2 + t) beliebig wachsen, während die Zielfunktion gegen −∞ fällt.

## Exercise 8.2

Das Rezept für Minimierungsprobleme entsteht aus dem Maximierungsrezept über min = −max(−·) und die Substitution y = −z. Gegenüber dem Maximieren drehen sich alle Ungleichungszeichen um: Eine ≥-Nebenbedingung wird zur nichtnegativen dualen Variable, eine nichtnegative Variable zur ≤-Dualnebenbedingung.

## Exercise 8.3

Zweimaliges Dualisieren hebt sich auf: Aus A wird über Aᵀ wieder A, die Zeichen drehen sich zweimal und landen wieder bei ≤. Die schwache Dualität bleibt dabei dieselbe Ungleichung cᵀx ≤ bᵀy, nur von der anderen Seite gelesen.

Die Classroom-Aufgabe steht nur im Erklär-PDF. Für den Upload verwende ich Bleier_sheet_8.pdf, das denselben Inhalt wie die schlichte Lösung enthält und damit die im Kursablauf verlangte Benennung erfüllt. Beide PDFs entstehen aus derselben Quelle; dafür blatt08.tex mit explainmode=0 beziehungsweise explainmode=1 mit pdflatex bauen. Die englischen Rechenschritte und die geforderte Grafik zur Unzulässigkeit stehen in beiden PDFs, die deutschen Erklärkästen nur in der Erklärung.
