# Hitori

Im Tutorium war ein ASP-Encoding für Hitori gefragt. Die Eingabe enthält für jede Zelle einen Fakt `cell(Zeile, Spalte, Wert)`. Gesucht ist eine Färbung: Gleiche Werte dürfen in einer Zeile oder Spalte nicht zweimal weiß bleiben, schwarze Zellen dürfen keine gemeinsame Kante haben, und alle weißen Zellen müssen über Kanten verbunden sein. Für die Aufgabe ist in Moodle kein Abgabetermin genannt.

## Lösung

In [hitori.lp](hitori.lp) entscheidet eine Choice Rule für jede Zelle, ob sie schwarz (`shaded/2`) ist. Alles, was nicht schwarz gewählt wurde, ist weiß. Der Test auf schwarze Nachbarn schaut nur nach rechts und unten. Das reicht, weil beispielsweise die obere Zelle eines senkrechten Paars die untere schon prüft. Diagonalen zählen hier nicht als Nachbarn.

Für die Zahlen vergleiche ich in jeder Zeile die weißen Zellen mit gleichem Wert paarweise. `C1 < C2` verhindert, dass eine Zelle mit sich selbst verglichen oder dasselbe Paar zweimal geprüft wird. In einer Spalte bleiben die Spaltenkoordinaten gleich, und `R1 < R2` ordnet die beiden Zeilen. Schwarze Zellen sind bei beiden Vergleichen egal.

Für den Zusammenhang nehme ich die erste weiße Zelle, von oben nach unten und innerhalb einer Zeile von links nach rechts. `earlier/2` markiert dafür jede weiße Zelle, vor der schon eine andere weiße Zelle liegt. Es bleibt genau ein Start übrig (ganz ohne weiße Zelle wird die Färbung verworfen). Von dort geht `reach/2` in alle vier Richtungen, aber immer nur von einer schon erreichten auf eine weiße Zelle. Eine abgetrennte Gruppe weißer Zellen kann sich dadurch nicht selbst als erreichbar markieren. Bleibt eine weiße Zelle unerreicht, fällt die Färbung raus. `#show` gibt am Schluss nur die schwarzen Koordinaten aus.

## Ausführen und prüfen

Mit clingo 5.8.0 (`python -m pip install clingo==5.8.0`) im Blattordner ausführen. Die Instanzdateien aus dem [Moodle-Ordner Hitori](https://moodle.aau.at/mod/folder/view.php?id=1538187) separat dazulegen, sie sind nicht im Repo. Die `0` lässt clingo alle Lösungen ausgeben und nicht nach der ersten aufhören.

```sh
python -m clingo hitori.lp instance01.lp 0
python test_hitori.py instance*.lp
```

Alle fünf Moodle-Instanzen haben je ein Answer Set. Der Test vergleicht die schwarzen Koordinaten mit einer zweiten Suche in Python. Die geht die möglichen Färbungen durch, merkt sich belegte Werte je Zeile und Spalte und prüft am Schluss die weißen Wege. Ohne Instanzdateien geht `python test_hitori.py` auch: Dann laufen nur die selbst erzeugten kleinen Gitter und die einzelnen Randfälle.
