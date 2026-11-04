# Preparation for Minitest 1

Ausgearbeitete Vorbereitung für den ersten Minitest in Logische Programmierung (621.315). Das Original ist eine handschriftlich besprochene Folie in Moodle; hier stehen beide Übungen als saubere Schritt-für-Schritt-Lösung.

[Lösung](loesung_blatt03.pdf) · [Erklärung](erklaerung_blatt03.pdf) · [LaTeX-Quelle](blatt03.tex)

Exercise 1 sucht alle Answer Sets eines Programms mit zwei gegenseitig streuenden Regelpaaren. Die Fallanalyse über dress/shirt und sneakers/sandals erzwingt drei Kandidaten, jeder wird über den Gelfond-Lifschitz-Redukt bestätigt: {dress, sandals}, {shirt, sandals, skirt}, {shirt, sneakers, pants}.

Exercise 2 prüft drei vorgegebene Mengen auf Stabilität: {b, c, d, h} scheitert an g (im Redukt ein Fact, im Kandidaten fehlend), {a, f} ist stabil, {b, d, e, g, h} scheitert, weil d und e sich nicht selbst begründen können.

Beide PDFs stammen aus derselben LaTeX-Quelle. Alle drei Answer Sets aus Exercise 1 und alle drei Verdicts aus Exercise 2 wurden mit zwei getrennten Verfahren geprüft: vollständige Redukt-Auswertung über alle Teilmengen und clingo. Beide Verfahren liefern dieselben Mengen.

Originalblatt in Moodle: https://moodle.aau.at/mod/resource/view.php?id=1531035.

Zum Bauen mit einer TeX-Installation mit amsmath, TikZ und tcolorbox:

```sh
pdflatex -halt-on-error -jobname=loesung_blatt03 '\def\explainmode{0}\input{blatt03.tex}'
pdflatex -halt-on-error -jobname=erklaerung_blatt03 '\def\explainmode{1}\input{blatt03.tex}'
```
