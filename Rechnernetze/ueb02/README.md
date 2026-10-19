# Rechnernetze: Übungsblatt 02

[Lösung zum Abgeben](loesung_blatt02.pdf) · [Erklärung](erklaerung_blatt02.pdf) · [gemeinsame LaTeX-Quelle](blatt02.tex)

Das Blatt behandelt Internetarchitektur, OSI und TCP/IP, Transportprotokolle, einen Bankautomatenentwurf, ein geplantes WLAN, Streaming sowie HTTP, Mail und DNS. Die Aufgaben 2.10 bis 2.12 werten die drei Moodle-Mitschnitte aus. Die Nummerierung bleibt wie in der Angabe: 2.1, 2.2 und 2.4 bis 2.12. Eine Aufgabe 2.3 steht dort nicht.

Die Lösung enthält die geforderten Antworten und die beiden verlangten Grafiken, während das Erklär-PDF direkt an den passenden Stellen Hinweise zur Methode und zu typischen Verwechslungen ergänzt. Beide PDFs entstehen aus derselben Quelle; zusätzliche Erklärungen werden über `explainmode` zugeschaltet, damit die Zahlen und Ergebnisse beim Überarbeiten nicht zwischen zwei getrennten Dokumenten auseinanderlaufen.

## Ergebnisse der Aufzeichnungen

In `dump_protocols.pcap` sind 39 Ethernet-Frames enthalten. Zehn tragen ARP, 29 IPv4. Die IPv4-Frames teilen sich auf vier ICMP-, neun UDP- und 16 TCP-Frames auf. Über UDP laufen DHCP und DNS, über TCP ein HTTP-Dialog.

`dump_http.pcap` enthält drei TCP-Verbindungen für das HTML-Dokument und zwei Bilder. Insgesamt wurden 37475 Framebytes gezählt. Die drei Verbindungen dauern 0,301299, 0,301248 und 0,502194 Sekunden, jeweils vom ersten bis zum letzten aufgezeichneten Frame. Diese Zeiten dürfen wegen Überlappungen nicht einfach addiert werden. Der zusätzliche persistente Mitschnitt verwendet eine Verbindung für alle drei Objekte.

Framebytes, TCP-Nutzdaten und Dateiinhalte sind verschiedene Größen. Die Tabelle in der Lösung nennt die Zählweise ausdrücklich. Ein eigener PCAP-Parser und TShark 4.4.5 liefern dieselben Framezahlen, Bytezahlen und Zeitdifferenzen. Der Protokollmitschnitt wurde außerdem in Wireshark geöffnet: Mit dem Display-Filter `http` bleiben zwei von 39 Paketen sichtbar. Für die eigene Aufzeichnung wurden drei selbst erzeugte UDP-Testdatagramme auf Loopback erfasst. Fremder Verkehr wurde nicht mitgeschnitten.

## Nachvollziehen

Die Original-PDFs und PCAP-Dateien bleiben im Moodle-Kurs. Nach dem Herunterladen der Mitschnitte lassen sich die zentralen Auswertungen mit Wireshark beziehungsweise TShark wiederholen:

```bash
tshark -r dump_protocols.pcap -q -z io,phs -z conv,tcp
tshark -r dump_http.pcap -Y http.request -T fields -e tcp.stream -e http.request.uri
tshark -r dump_http.pcap -q -z conv,tcp
tshark -r dump_http_persistent.pcap -q -z conv,tcp
```

Die Conversations-Ausgabe kann Bytezahlen und Zeiten gerundet anzeigen. Für exakte Werte pro Frame:

```bash
tshark -r dump_http.pcap -T fields -e frame.time_epoch -e frame.len -e tcp.stream -e tcp.len
```

Pro TCP-Stream werden `frame.len` und `tcp.len` summiert. Die Dauer ist letzter minus erster Zeitstempel. `tcp.len` enthält hier auch HTTP-Header. Die detaillierten Zwischenwerte und Messprüfungen bleiben lokal; sie sind keine zusätzlichen Abgabedateien.

Zum Bauen braucht es pdfLaTeX mit TikZ und tcolorbox:

```bash
pdflatex -halt-on-error -jobname=loesung_blatt02 '\def\explainmode{0}\input{blatt02.tex}'
pdflatex -halt-on-error -jobname=erklaerung_blatt02 '\def\explainmode{1}\input{blatt02.tex}'
```

Jeden Befehl zweimal ausführen, damit Verweise und Seitenumbrüche feststehen.

## Abgabe und Annahmen

Für Gruppe Horvath zeigt Moodle am 19.10.2026 den 10.11.2026 um 08:00 Uhr. Die Abgabe für Gruppe Alkhateeb nennt dagegen noch 23.10.2025, 13:00 Uhr. Das ist kein bestätigter Termin für das aktuelle Semester und wurde nicht eigenmächtig geändert. Quellen sind die beiden [Horvath-](https://moodle.aau.at/mod/assign/view.php?id=1489875) und [Alkhateeb-Abgaben](https://moodle.aau.at/mod/assign/view.php?id=1489876).

Die Gruppennummer fehlt weiterhin und steht deshalb als `YY` im Dokument. Für ein Abgabearchiv wäre laut Aufnahmefolien `ueb02-gruppeYY.zip` mit der tatsächlichen Nummer zu verwenden. Es wurde nichts auf Moodle eingereicht. Das Haus in 2.7 ist eine ausdrücklich fiktive Planung mit vorhandenem Internetanschluss und LAN-Verkabelung. Preise sind recherchierte Beispiele, keine Kaufzusage. Bankprotokoll und SMTP-Dialog sind Entwürfe, keine behaupteten Praxistransaktionen.

## KI-Kennzeichnung

Die Aufnahmefolien der LV verlangen bei KI-Nutzung Tool, Version und Datum; deshalb steht in der README und in beiden PDFs, dass Hermes Agent v0.21.5 mit dem OpenAI-Modell `gpt-6.1-sol` am 19.10.2026 für Ausarbeitung und Prüfung verwendet wurde. Separat übernommener Programmcode wird hier nicht abgegeben. Quellen, Messungen und Beispiele sind im Dokument voneinander getrennt.
