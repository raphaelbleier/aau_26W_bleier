# Übungsblatt 05: TCP, Netzwerkleistung und Wireshark

Raphael Bleier, Gruppe 1 (Devis, Fabio, Raphael). Abgabe laut beiden Moodle-Gruppen: 01.12.2026, 08:00. Es wurde nichts auf Moodle eingereicht.

[Lösung als PDF](loesung_blatt05.pdf), [Erklärung als PDF](erklaerung_blatt05.pdf), [gemeinsame LaTeX-Quelle](blatt05.tex), [KI-Kennzeichnung](KI_NUTZUNG.md).

Die korrigierte Angabe behandelt sieben Aufgaben. 5.1 untersucht den Handshake, 5.2 den Byte-Stream mit Framing und 5.3 die Bytezählung. In 5.4 kommen Paketverluste dazu. 5.5 und 5.6 vergleichen Verzögerungen, TCP-Durchsatz und hohe UDP-Last. 5.7 zeigt einen tatsächlich aufgezeichneten Flow als Sequenzdiagramm. Die PDFs enthalten die Aufgabenstellung jeweils knapp vor der Lösung.

## Starten

Die Programme brauchen Python 3. Für das vollständige Netzexperiment werden außerdem Mininet, iproute2, ethtool, tcpdump, tshark und iperf3 gebraucht, weil die Messung echte Netzwerk-Namespaces anlegt und den Datenverkehr auf dem Clientinterface aufzeichnet. Getestet wurde unter Linux mit iperf3 3.18. Mininet muss mit einem Python gestartet werden, in dem das Paket installiert ist, hier `/usr/bin/python3`. Root-Rechte und Netzwerk-Namespaces sind nötig. Die neue Moodle-Seite „Virtual Machine“ bietet dafür eine x86-VM an; eine lokale Linux-Installation geht ebenfalls.

Im Blattordner starten:

```sh
python3 -m unittest -v test_framing.py
sudo /usr/bin/python3 measure.py --output eigene_messungen
python3 analyze.py eigene_messungen
```

`measure.py` führt die zwölf TCP-Konfigurationen und sechs UDP-Konfigurationen aus. Erfolgreiche Versuche laufen jeweils sechs Sekunden. Es gibt keine ausgelassene Anlaufphase. Scheitert ein iperf-Steuerkanal, versucht das Programm diese Konfiguration erneut (höchstens drei Versuche). Solche Fehlversuche werden nicht als erfolgreiche Datenmessung gezählt. `--capture-only` erneuert nur die drei TCP-Messungen bei 20 ms und den Python-Flow; dazu braucht es eine bestehende `results.json` im Zielordner.

Die mitgelieferten Messdaten bleiben bei einem eigenen Lauf unverändert, wenn man wie oben einen anderen Ausgabeordner verwendet. Die Zufallsverluste sind nicht mit einem festen Seed erzeugt. Ein neuer Lauf darf daher andere Werte liefern.

Die vorgegebene interaktive Umgebung bleibt nutzbar:

```sh
sudo env LINK_DELAY=20ms LINK_LOSS=5 /usr/bin/python3 start_lab.py
```

`start_lab.py` ist unverändert aus dem offiziellen ZIP übernommen. Die Struktur bleibt `client -- router -- server`, mit Client 10.0.1.2 und Server 10.0.2.2. In `topology.py` sind Delay und Verlust parametriert. Zusätzlich haben beide Links für den Lastvergleich eine Bandbreite von 10 Mbit/s. Das ist eine eigene Versuchsbedingung, kein Wert aus der Angabe. Delay und Verlust gelten je Link und Richtung. 20 ms pro Link bedeuten deshalb 80 ms zusätzliche RTT über den Hin- und Rückweg, ohne Warteschlangen.

## Client, Server und Framing

Im Server-Terminal:

```sh
python3 tcp_server.py --recv-size 8
```

Im Client-Terminal:

```sh
python3 tcp_client.py --large 256
```

Der Client hält eine Verbindung offen und vergleicht jedes Echo bytegenau, statt aus der Anzahl empfangener TCP-Pakete auf die Anzahl der Anwendungsnachrichten zu schließen. Die vier kurzen Nachrichten enthalten zusammen 31 Nutzbytes. `--large 256` ergänzt 256 Wiederholungen aller Bytewerte, also 65536 Nutzbytes. Vor jeder Nachricht stehen vier Byte Länge in Netzwerk-Bytefolge. `framing.py` liest zuerst den vollständigen Header und dann die angegebene Nutzlast. Teilstücke aus mehreren `recv()`-Aufrufen werden gesammelt. Mehrere Frames in einem TCP-Paket sind genauso erlaubt.

Das Präfix zählt die Länge der codierten Bytes. Ein leerer Frame hat Länge null; EOF vor dem nächsten Header wird dagegen als `None` zurückgegeben. EOF mitten im Frame ist ein Fehler. Frames über 4 MiB werden abgelehnt, bevor die Nutzlast gelesen wird.

Für den Versuch ohne Framing setzt man auf beiden Seiten `--mode raw`. Der Server kann mit `--recv-size 1`, `8` oder `1024` laufen. Er protokolliert die tatsächlich empfangenen Teilstücke. Der Client sendet seine vier Nachrichten ohne dazwischen auf ein Echo zu warten und prüft danach den gesamten zurückgelesenen Byte-Stream. Damit hängt der Vergleich nicht davon ab, ob einzelne Schreibaufrufe zufällig getrennt ankommen.

## Messdaten lesen

`messungen/results.json` enthält die Empfänger-Durchsätze, die TCP-Sender-Retransmissions und die UDP-Verluste. Die einzelnen iperf-JSON-Dateien enthalten die Zeitfenster und Intervallwerte. Interne iperf-Cookies und Hostinformationen wurden vor dem Speichern entfernt; die Messfelder sind unverändert. Die UDP-Verlustquote in `results.json` ist aus den Empfängerzählern `lost_packets/packets` berechnet. Das Prozentfeld von iperf3 ist bei einigen Läufen geringfügig inkonsistent; sein Originalwert bleibt zusätzlich als `reported_lost_percent` erhalten.

`handshake.pcap` enthält nur den eigenen Python-Testflow. Die zugehörigen Headerdaten stehen in `handshake-packets.tsv`. Die drei `tcp-d20-p*-packets.tsv` enthalten die ausgewerteten Headerfelder der Verlustversuche. Deren vollständige PCAPs bleiben lokal und werden nicht veröffentlicht, weil sie auch den iperf-Steuerkanal enthalten. Bei einem eigenen Lauf erzeugt `measure.py` sie erneut. `analyze.py` exportiert mit tshark die Felder und prüft für fünf große Segmente, welches spätere kumulative ACK ihren Bytebereich bestätigt. Die Ergebnisse stehen in `tcp_summary.json`.

Die `raw-recv-*.log` zeigen die Empfangsgrößen ohne Framing. Das Client- und Serverprotokoll des gerahmten Tests steht in `framed-client.log` und `framed-server.log`. Die beiden PDFs verwenden diese Messungen für Tabellen, Diagramme und die einzelnen Antworten. Ein einzelner kurzer Versuch reicht nicht für statistische Aussagen über die genaue Reihenfolge der Durchsätze. Er zeigt aber das Verhalten unter den gewählten Bedingungen.

Die vier Nachrichten des Clients können bereits beim ersten `recv()`-Aufruf vollständig im Empfangspuffer liegen, obwohl er sie mit vier getrennten Aufrufen geschrieben hat; genau deshalb vergleicht der Versuch zusätzlich die empfangenen Bytefolgen und nicht nur deren Längen.

## Tests und Quellen

Die sieben Testmethoden prüfen fragmentierte Header und Nutzdaten, gebündelte Frames, leere Nachrichten, UTF-8, unvollständige Frames, Überlänge sowie echte TCP-Prozesse. Die Prozessfälle laufen mit beiden Betriebsarten und drei Empfangsgrößen. Ein zusätzlicher Socketpair-Test überträgt eine große Binärnachricht. Ein Test für kleine Fragmente darf nicht nur prüfen, ob dieselbe Implementierung ihr eigenes Format versteht; deshalb enthält der Test auch von Hand vorgegebene Headerbytes.

Die Originalangabe ist Moodle-Ressource [1535103](https://moodle.aau.at/mod/resource/view.php?id=1535103), das Starter-ZIP Ressource [1506949](https://moodle.aau.at/mod/resource/view.php?id=1506949). Die Aufnahmefolien verlangen auf Seite 18 die KI-Kennzeichnung; sie bleibt deshalb in den Dateien erhalten. Die TCP-Begriffe folgen [RFC 9293, Abschnitte 3.4 und 3.5](https://www.rfc-editor.org/rfc/rfc9293.html).
