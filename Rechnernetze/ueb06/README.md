# Rechnernetze: Übungsblatt 06

[Lösung](loesung_blatt06.pdf) · [Erklärung](erklaerung_blatt06.pdf) · [KI-Kennzeichnung](KI_NUTZUNG.md) · [Topologie](topology.py)

Gruppe 1, Raphael Bleier, Devis und Fabio. Welche der beiden Moodle-Abgaben das ist, habe ich nicht geprüft. Horvath ist Dienstag, 15.12.2026, 08:00, Alkhateeb Dienstag, 15.12.2026, 10:00. Nichts hochgeladen.

Gemessen am 30.10.2026 mit Mininet 2.3.0 und Python 3.13.3. `xterm` fehlt hier, also liefen `ip` und `ping` in den Namespaces, das ist dieselbe Sicht wie in einem Terminal auf dem Knoten. Aufgaben 6.1 bis 6.3 sind die Vorlage, bevor 6.7 die Topologie ändert.

## Was drin ist

6.1 listet die Interfaces. Zwischen Client und r1 liegt 10.0.1.0/24, zwischen den Routern 10.0.12.0/30, zwischen r2 und dem Server 10.0.2.0/24. Loopback ist je Namespace eigen und kein gemeinsames Netz.

6.2 erklärt den Weg von 10.0.1.2 nach 10.0.2.2: der Client schickt an 10.0.1.1, r1 an 10.0.12.2, und r2 liefert an 10.0.2.2 aus. TTL 62, also zwei Router.

6.3 löscht die beiden von Hand gesetzten Routen. Der Ping kommt dann mit Destination Net Unreachable von 10.0.1.1 zurück, 100% Verlust. Nach `ip route add` sind es wieder 3/3 bei TTL 62. Die späteren Pakete lagen bei 60,3 ms und 60,6 ms. Der Mittelwert 73,894 ms ist höher, weil das erste Paket 101 ms für ARP brauchte.

6.4 plant aus 10.10.0.0/23 vier Netze, und zwar 10.10.0.0/24 für 200 Endgeräte, 10.10.1.0/26 für 50 Server, 10.10.1.64/27 für 20 Management-Geräte und 10.10.1.96/30 für die Routerstrecke. /25, /27, /28 und /31 (klassisch gezählt) reichen jeweils nicht. Das Labor benutzt /30 auf der Routerstrecke aus demselben Grund.

6.5 ist Dijkstra ab A. Die Kosten sind B 1, C 3, G 4, F 6, D 8 und E 9. Nach F gibt es zwei Wege mit Kosten 6, der Vorgängerbaum behält A-B-F.

6.6 ist Distance-Vector an B. Das Netz stellt Kanten nach aufsteigenden Kosten zu, die billigste ist A-E mit 2, und bei B kommen die Vektoren deshalb in der Reihenfolge E, C, A an. Am Ende steht (A 5, B 0, C 7, D 11, E 3). Unterwegs meldet E für D einmal 17, C korrigiert das auf 11.

6.7 hängt client2 mit 10.0.1.3/24 über eine Bridge an r1. `start_lab.py` bleibt unverändert, und die Route 10.0.1.0/24 auf r2 gilt für beide Clients. Ping zum Server: 0% Verlust, TTL 62. Die späteren Pakete lagen bei 80,1 ms und 80,2 ms. Der Mittelwert 107,291 ms kommt vom ersten Paket, das wegen ARP 162 ms brauchte. Die unveränderten TCP-Programme haben die drei Testzeilen zurückgeschickt, der Server sah die Verbindung von 10.0.1.3.

## Starten

Strukturtest, ohne root und ohne Mininet:

```bash
python3 -m unittest discover -s tests -v
```

Am 30.10.2026 waren alle fünf Tests grün.

Die Laborvorlage `start_lab.py` bleibt außerhalb. `topology.py` aus diesem Ordner ersetzt die Vorlage. Danach startet das unveränderte `start_lab.py` die erweiterte Topologie, weil die Interface-Namen von client, r1, r2 und server gleich bleiben und client2 seine Adresse schon in `topology.py` bekommt, nicht erst in der Konfiguration.

Die Ping-Zahlen sind der Lauf vom 30.10.2026 und nicht aus dem Bauch gerundet: nach dem Neueintrag der beiden Routen kamen drei Antworten mit TTL 62 zurück, die späteren bei etwa 60 ms, und client2 hat über die Bridge dieselben drei TCP-Zeilen bekommen, die das unveränderte Serverprogramm zurückgeschickt hat.

Zum Bauen der PDFs, zweimal pro Variante:

```bash
pdflatex -halt-on-error -jobname=loesung_blatt06 '\def\explainmode{0}\input{blatt06.tex}'
pdflatex -halt-on-error -jobname=erklaerung_blatt06 '\def\explainmode{1}\input{blatt06.tex}'
```
