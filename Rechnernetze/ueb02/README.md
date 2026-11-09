# Rechnernetze: Übungsblatt 02

[Lösung](loesung_blatt02.pdf) · [Erklärung](erklaerung_blatt02.pdf) · Kursvorgabe: KI-Nutzung ist zu kennzeichnen · [gemeinsame LaTeX-Quelle](blatt02.tex)

Die eigene UDP-Aufzeichnung aus Aufgabe 2.10 liegt als [PCAP-Datei](capture-own-udp.pcap) bei. Moodle-Mitschnitte sind nicht im Repository enthalten.

Das Blatt behandelt Internetarchitektur, OSI und TCP/IP, Transportprotokolle, einen Bankautomatenentwurf, ein geplantes WLAN, Streaming sowie HTTP, Mail und DNS. Die Aufgaben 2.10 bis 2.12 werten die drei Moodle-Mitschnitte aus; Aufgabe 2.10 enthält zusätzlich die eigene UDP-Aufzeichnung. Die Nummerierung bleibt wie in der Angabe: 2.1, 2.2 und 2.4 bis 2.12. Eine Aufgabe 2.3 steht dort nicht.

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

Moodle nennt für Gruppe Horvath den 10.11.2026 um 08:00 Uhr. Für Gruppe Alkhateeb steht jetzt der 11.11.2026 um 11:00 Uhr (Stand: 27.10.2026). Der alte Alkhateeb-Termin aus 2025 ist damit ersetzt. Die Termine gelten jeweils nur für die zugehörige Übungsgruppe. Quellen sind die beiden [Horvath-](https://moodle.aau.at/mod/assign/view.php?id=1489875) und [Alkhateeb-Abgaben](https://moodle.aau.at/mod/assign/view.php?id=1489876).

Raphael hat Gruppe 1 sowie die Teammitglieder Raphael Bleier, Devis und Fabio angegeben. Die tatsächliche Zuordnung zu einer der beiden Moodle-Abgabeaktivitäten wurde nicht geprüft. Das lokale Archiv `ueb02-gruppe01.zip` enthält die aktuellen Artefakte und Gruppeninfo. Eingereicht wurde nichts. Aufgabe 2.7 verwendet Raphaels Keller-Netz. Die genauen Modelle von Switch und Access-Point sind unbekannt; ob ein AP bereits vorhanden ist, wurde nicht bestätigt. Auch das Modell des vorhandenen Provider-5G-Routers ist nicht bekannt. Dafür sind keine zusätzlichen Hardwarekosten angesetzt; laufende Vertragsgebühren bleiben außen vor. Die genannten Preise sind Modellbeispiele und kein bestätigter Anschaffungspreis. Bankprotokoll und SMTP-Dialog sind Entwürfe, keine behaupteten Praxistransaktionen.
