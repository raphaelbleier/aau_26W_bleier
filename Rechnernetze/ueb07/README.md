# Rechnernetze: Übungsblatt 07

[Lösung](loesung_blatt07.pdf) · [Erklärung](erklaerung_blatt07.pdf) · [KI-Kennzeichnung](KI_NUTZUNG.md) · [Topologie](topology.py) · [Fehler-Mitschnitt](fault-r3eth0.pcap)

Gruppe 1, Raphael Bleier, Devis und Fabio. Welche der beiden Abgaben das ist, habe ich nicht geprüft. Beide Moodle-Termine stehen auf Dienstag, 12.01.2027, 08:00. Nichts hochgeladen.

Gemessen am 30.10.2026 mit Mininet 2.3.0 und Python 3.13.3. `xterm` fehlt hier, also liefen `ip`, `ping` und `tracepath` in den Namespaces, und das ist dieselbe Sicht wie in einem Terminal auf dem Knoten. Der Knoten heißt in der Vorlage `client`, in der Angabe `client1`.

Die Angabe bricht im Satz zu den neuen Verbindungen ab. Ich lese ihn als neue Punkt-zu-Punkt-Netze für Router-zu-Router-Strecken, so wie 10.0.12.0/30 zwischen r1 und r2 schon in der Vorlage steht. Die Skizze kann man auch als direkten Anschluss von r3 an den Server lesen, das wäre aber keine Router-zu-Router-Verbindung, und der Server läge in zwei Netzen. Deshalb hängt r3 zwischen r1 und r2. Das Server-LAN bleibt an r2.

## Adressen

Die Vorlage bleibt: client-eth0 10.0.1.2/24 und r1-eth0 10.0.1.1/24 im Netz 10.0.1.0/24, r1-eth1 10.0.12.1/30 und r2-eth0 10.0.12.2/30 im Netz 10.0.12.0/30, r2-eth1 10.0.2.1/24 und server-eth0 10.0.2.2/24 im Netz 10.0.2.0/24.

Neu sind zwei /30 mit genau zwei nutzbaren Adressen: r1-eth2 10.0.13.1/30 mit r3-eth0 10.0.13.2/30 im Netz 10.0.13.0/30, und r3-eth1 10.0.23.1/30 mit r2-eth2 10.0.23.2/30 im Netz 10.0.23.0/30. Am 30.10.2026 waren alle neun Dateninterfaces `UP`, und jeder Router hatte `ip_forward = 1`. Loopback 127.0.0.1/8 ist in jedem Namespace eigen und kein gemeinsames Netz.

## 7.1 Pfad über r2

Jeder Router hat seine eigene Tabelle. Es gibt keine gemeinsame Tabelle für das Labor.

Der Client schickt 10.0.2.2 nicht ins lokale Netz, weil `ip route get 10.0.2.2` `via 10.0.1.1 dev client-eth0` lieferte und 10.0.2.2 nicht in 10.0.1.0/24 liegt. Die Default-Route reicht dafür. Deshalb braucht der Client keine Route pro Zielgerät: alles Fremde geht an r1, und r1 entscheidet weiter.

r1 nimmt das Paket auf r1-eth0 an. Die längste passende Route ist `10.0.2.0/24 via 10.0.12.2 dev r1-eth1`, der Next Hop ist r2, der Ausgang r1-eth1. r1 liefert nicht lokal aus.

r2 nimmt es auf r2-eth0 an. `ip route get 10.0.2.2` lieferte `dev r2-eth1 src 10.0.2.1`, ohne `via`, weil 10.0.2.2 im angeschlossenen Netz liegt. Dann ARP, und die Zustellung geht an server-eth0.

Rückweg: der Server hat `default via 10.0.2.1`, r2 schickt 10.0.1.0/24 über 10.0.12.1, und r1 stellt auf r1-eth0 zu. Ping von client nach 10.0.2.2: 5 von 5, TTL 62. Zwei Router haben die TTL von 64 auf 62 gesenkt. `tracepath -n` nannte 10.0.1.1, dann 10.0.12.2, dann 10.0.2.2.

## 7.2 Zweiter Pfad, nur einer aktiv

Pfad A ist die Vorlage. r1 hat `10.0.2.0/24 via 10.0.12.2 dev r1-eth1`, r2 hat `10.0.1.0/24 via 10.0.12.1 dev r2-eth0`.

Pfad B löscht diese beiden Einträge und setzt stattdessen `10.0.2.0/24 via 10.0.13.2 dev r1-eth2` sowie `10.0.1.0/24 via 10.0.23.1 dev r2-eth2`. r3 hat immer `10.0.2.0/24 via 10.0.23.2 dev r3-eth1` und `10.0.1.0/24 via 10.0.13.1 dev r3-eth0`, außer im absichtlichen Fehler. Es liegen nie beide Fernrouten gleichzeitig in r1 oder r2. Keine Metrik, kein ECMP.

Auf Pfad B lieferte `ip route get` auf r1 `via 10.0.13.2 dev r1-eth2`, auf r3 `via 10.0.23.2 dev r3-eth1` und auf r2 `dev r2-eth1`. Ping: 5 von 5, TTL 61, also drei Router. `tracepath` nannte 10.0.1.1 und 10.0.13.2, Hop 3 antwortete nicht, Hop 4 war 10.0.2.2. Der fehlende Hop ändert die TTL nicht. 61 bleibt 64 minus 3.

## 7.3 Zwei Verzögerungen

`tc qdisc` zeigte netem 10 ms auf client-eth0 und r2-eth1, 5 ms auf r1-eth1, 30 ms auf r1-eth2 und r3-eth1. Die Gegenrichtung hat denselben Wert, weil TCLink den Delay pro Richtung setzt.

Pfad A, eine Richtung: 10 + 5 + 10 = 25 ms. Hin und zurück sind das 50 ms, weil jede Richtung den Delay noch einmal drauflegt. Die fünf späteren Pings lagen bei 50,057 bis 50,087 ms, Mittel 50,071 ms. Der einzelne Ping davor brauchte 100,206 ms. Der ARP-Austausch steckt nicht in der Linksumme.

Pfad B, eine Richtung: 10 + 30 + 30 + 10 = 80 ms, hin und zurück 160 ms. Die fünf späteren Pings lagen bei 160,081 bis 160,186 ms, Mittel 160,143 ms. Der erste Ping brauchte 280,512 ms.

Die beobachtete RTT ist also nicht die Summe der in der Angabe genannten 5 ms und 30 ms. Ping zählt beide Richtungen, auf beiden Pfaden liegen noch die gemeinsamen 10-ms-Links, und Pfad B hat zwei Links mit 30 ms, nicht einen. Beim ersten Paket kommt ARP dazu. Die späteren Pakete liegen nah an 2 mal der Einwegsumme, der erste nicht.

## 7.4 Fehlende Route auf r3

Auf Pfad B habe ich nur `10.0.2.0/24` auf r3 gelöscht. Die Route zurück zum Client blieb.

Zuerst der Nachbar, nicht das entfernte Ziel. client erreichte 10.0.1.1 in 20,022 ms bei TTL 64, und r1 erreichte 10.0.13.2 in 60,129 ms, ebenfalls TTL 64. Das ist 2 mal 30 ms auf diesem einen Link. `ip -br addr` auf r3 zeigte beide Interfaces `UP`, die Adressen waren also da. `ip route` zeigte 10.0.13.0/30 und 10.0.23.0/30, aber kein 10.0.2.0/24. `ip route get 10.0.2.2` antwortete `Network is unreachable`.

Dann erst der Ping zum Server: `From 10.0.13.2 icmp_seq=1 Destination Net Unreachable`, 3 gesendet, 0 empfangen, 100 Prozent Verlust. 10.0.13.2 ist r3-eth0. Der Absender der Fehlermeldung ist der Router, dem die Route fehlt.

`tracepath` hat diesen Absender im Fehlerfall nicht als Hop angezeigt, nur `no reply` bis Hop 30. Genau dort hilft der Mitschnitt. Auf r3-eth0 kamen das Echo von 10.0.1.2 nach 10.0.2.2 (Typ 8, TTL 63, also schon über r1) und die Antwort von 10.0.13.2, ICMP Typ 3 Code 0, Network unreachable. Wireshark bzw. tshark zeigt, dass das Paket r3 erreicht und dort verworfen wird. `ip addr` sagt das nicht, und `tracepath` hat es hier auch nicht gesagt. Ping hat den Absender schon genannt. Der Mitschnitt bestätigt ihn am Interface.

Korrektur: `ip route replace 10.0.2.0/24 via 10.0.23.2 dev r3-eth1`. Danach 3 von 3, TTL 61, RTT 160,133 bis 160,686 ms.

## 7.5 CSMA

Die Folien bis Kapitel 3 enthalten diesen Stoff nicht. Die VO nennt Kurose/Ross, und die Antworten folgen der dort üblichen Darstellung, nicht einer Folie, die hier noch nicht liegt.

CSMA heißt Carrier Sense Multiple Access. Der Knoten hört den gemeinsamen Kanal ab, bevor er sendet. Ist der Kanal frei, sendet er. Ist er belegt, wartet er. Trotzdem kollidieren Rahmen, weil das Signal Laufzeit hat und zwei Knoten beide Stille hören können, bevor das Signal des anderen ankommt.

CSMA erkennt die Kollision nicht während des Sendens und schickt den Rahmen zu Ende. CSMA/CD hört beim Senden mit, bricht ab, wenn das Empfangene vom Gesendeten abweicht, schickt ein Jam-Signal und wartet eine zufällige Zeit (exponential backoff), bevor die Station es noch einmal versucht. Das Jam-Signal soll die anderen Empfänger den Rahmen verwerfen lassen.

CSMA/CD steckt im klassischen gemeinsamen Ethernet, IEEE 802.3, also Koax und Hubs, halbduplex. Auf einer geschalteten Vollduplex-Strecke gibt es diesen Wettbewerb nicht. CSMA/CA steckt in IEEE 802.11. Eine Funkstation kann beim Senden schlecht mithören, weil das eigene Signal den Kanal übertönt, sie wartet bis der Kanal frei ist, sendet den Rahmen ganz und erwartet eine Bestätigung. Bleibt die aus, nimmt sie eine Kollision an und wartet ebenfalls mit exponential backoff. RTS/CTS ist eine zusätzliche Absprache, kein Pflichtteil jeder Übertragung.

## Starten

Strukturtest, ohne root und ohne Mininet:

```bash
python3 -m unittest discover -s tests -v
```

Am 30.10.2026 waren alle vier Tests grün.

Labor, nur mit root:

```bash
sudo python3 start_lab.py --check
sudo python3 start_lab.py B --check
```

`start_lab.py` aus der Vorlage setzt die neuen Adressen nicht. Die Datei in diesem Ordner ersetzt sie für r3. Die Vorlage selbst habe ich nicht verändert und nicht mit ins Repo gelegt.

Die Ping-Zahlen sind der Lauf vom 30.10.2026. Pfad A: fünf Antworten, TTL 62, spätere RTT etwa 50,07 ms. Pfad B: fünf Antworten, TTL 61, spätere RTT etwa 160,14 ms. Nach dem Löschen der Serverroute auf r3 kam Destination Net Unreachable von 10.0.13.2, nach dem Wiedereintrag wieder 3 von 3.
