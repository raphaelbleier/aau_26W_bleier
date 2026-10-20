# Homework sheet 1

Homework sheet 1 aus Logische Programmierung (621.315). Die Aufgabennummern 1.1 bis 1.4 bleiben wie auf dem Originalblatt. Der Ordner ueb02 bezeichnet das zweite veröffentlichte Dokument, nicht Homework 2.

[Lösung](loesung_blatt02.pdf) · [Erklärung](erklaerung_blatt02.pdf) · [LaTeX-Quelle](blatt02.tex)

Besprechung/Korrektur am 28.10.2026. Auf dem Blatt steht keine Uhrzeit und keine separate Uploadfrist. Ich habe nichts in Moodle abgegeben.

In 1.1 wird die kleinste abgeschlossene Atom-Menge aufgebaut. Jede Regel wird erst verwendet, wenn ihre Voraussetzungen schon hergeleitet sind. Die zweite Aufgabe prüft die vorgegebenen Kandidaten über den Gelfond-Lifschitz-Redukt. Für 1.3 schränken Fallunterscheidungen die möglichen Answer Sets ein, ohne alle Interpretationen durchzugehen. In 1.4 geht es um gegenseitige Default-Negation und Regeln, die bestimmte Kombinationen ausschließen.

Die Lösung enthält die Aufgabenprogramme, vollständige Redukte und die einzelnen Herleitungsschritte. Die deutsche Erklärung steht direkt neben den jeweiligen Schritten. Beide PDFs stammen aus derselben Quelle. Jede Kandidatenprüfung vergleicht die Ausgangsmenge mit dem kleinsten Modell des Redukts; bloß alle Regeln zu erfüllen reicht dafür nicht. Alle zwölf Programme beider Dokumente wurden zusätzlich mit zwei getrennten Verfahren geprüft: vollständige Redukt-Auswertung und clingo. Die Ergebnismengen stimmen überein. Bei der Probe wird für jede Kandidatenmenge zuerst das gesamte Redukt gebildet und anschließend jede neu ableitbare Aussage einzeln hinzugefügt, bis keine Regel aus dem aktuell gebildeten positiven Redukt mehr ein weiteres Atom liefert. Das ist die Abbruchbedingung.

Als fachliche Grundlage dienen die Kursunterlagen „Notes on positive and normal logic programs“, insbesondere die Definitionen von Modell, Konsequenzmenge und Redukt. Das Originalblatt bleibt in Moodle: https://moodle.aau.at/mod/resource/view.php?id=1509282. Die Notizen sind über die [Kursseite](https://moodle.aau.at/course/view.php?id=47556) zugänglich.

Zum Bauen mit einer TeX-Installation mit amsmath, TikZ und tcolorbox:

```sh
pdflatex -halt-on-error -jobname=loesung_blatt02 '\def\explainmode{0}\input{blatt02.tex}'
pdflatex -halt-on-error -jobname=erklaerung_blatt02 '\def\explainmode{1}\input{blatt02.tex}'
```
