# Rechnernetze: Übungsblatt 03

[Lösung und Testbericht als PDF](loesung_blatt03.pdf) · [Erklärung als PDF](erklaerung_blatt03.pdf) · Kursvorgabe: KI-Nutzung ist zu kennzeichnen · [gemeinsame LaTeX-Quelle](blatt03.tex)

Das Blatt enthält die Aufgaben 3.1 bis 3.5. Während der POP3-Client direkt mit Sockets arbeitet und die empfangenen Zeilen selbst auswertet, greift der POP3-Server über die vorgegebene Schnittstelle auf die Nachrichten der bereitgestellten Datenbank zu. Der HTTP-Server hat zwei getrennte Betriebsarten: sequentielles HTTP/0.9 und paralleles HTTP/1.0 mit Keep-Alive. Alle Programme brauchen nur die Python-Standardbibliothek.

## Starten

Die Befehle gelten im Blattordner. Zuerst `SampleDataBase.py` und `document_root.zip` aus Moodle herunterladen, das ZIP in einen eigenen Ordner entpacken und beide außerhalb des Repos aufbewahren. Die Datenbank wird nicht nachgebaut oder als Lehrunterlage weiterveröffentlicht.

```bash
# Terminal 1: Original-Datenbank über einen frei gewählten lokalen Pfad laden.
python3 pop3_server.py --database "$HOME/Downloads/SampleDataBase.py" --port 11110

# Terminal 2: Passwort wird verdeckt abgefragt, nicht als Kommandozeilenargument.
python3 pop3_client.py 127.0.0.1 --port 11110 --user alice --message 1

# HTTP/0.9, genau ein Request-Handler gleichzeitig:
python3 http_server.py --mode 09 --port 8080 --root "$HOME/Downloads/documentRoot"

# HTTP/1.0 mit Request-Workern und zentralem Logger:
python3 http_server.py --mode 10 --port 8081 --root "$HOME/Downloads/documentRoot"

# Eigene Testdaten, keine Moodle-Dateien nötig:
python3 -m unittest discover -s tests -v
```

Beim HTTP-Server ist Port 80 der Vorgabewert. Für die lokalen Tests wurden unprivilegierte Ports verwendet. Als document root muss der Ordner gewählt werden, der direkt `index.html` und `images/` enthält. Die Standardadresse ist ausschließlich Loopback. Den unverschlüsselten POP3-Laborserver nicht ins öffentliche Netz stellen und keine echten Mailpasswörter verwenden.

## Aufgabe 3.1

Nach dem TCP-Verbindungsaufbau sendet der Server seine Begrüßung. In AUTHORIZATION meldet sich der Client mit `USER` und `PASS` an. Erst nach erfolgreicher Prüfung und exklusiver Sperre des Maildrops beginnt TRANSACTION. `STAT` nennt Anzahl und Gesamtgröße, `LIST` die einzelnen Nachrichtengrößen und `RETR n` den Inhalt einer Nachricht. `DELE n` markiert zunächst nur eine Nachricht. `RSET` entfernt diese Markierungen wieder. Ein `QUIT` in TRANSACTION führt nach UPDATE und übernimmt die Löschungen. Ein Verbindungsabbruch ohne dieses `QUIT` übernimmt sie nicht.

POP3 mit Klartext-Anmeldung verschlüsselt weder Passwort noch Nachrichten. Das ist für einen isolierten Labortest geeignet, nicht für einen echten Mailzugang. Für den Betrieb braucht es TLS, etwa implizites TLS auf Port 995 oder die passende TLS-Erweiterung mit Zertifikatsprüfung. APOP aus RFC 1939 verschlüsselt den Mailinhalt nicht und ersetzt TLS nicht. Die vorliegende Implementierung bietet bewusst kein TLS an.

Eine single-line response endet nach der Statuszeile `+OK ...` oder `-ERR ...`. Eine erfolgreiche multi-line response enthält danach mehrere Datenzeilen und eine einzelne Punktzeile als Abschluss. Beginnt eine Datenzeile mit einem Punkt, sendet der Server einen zusätzlichen Punkt. Der Client entfernt genau diesen zusätzlichen Punkt wieder. Ohne dieses Dot-Stuffing könnte eine Mailzeile mit nur einem Punkt den Abruf vorzeitig beenden. `LIST` ohne Argument ist mehrzeilig; `LIST 1` ist einzeilig.

IMAP verwendet nicht dieses allgemeine POP3-Punktformat. Antworten können ungetaggte Statusdaten und Literale mit angegebener Bytelänge enthalten. Ein Tag ordnet den Abschluss einer Anfrage zu. IMAP hält Ordner und Lesestatus auf dem Server und kann diese zwischen Geräten synchronisieren. POP3 dient vor allem dem Abruf. Nachrichten müssen dabei nicht zwingend nach dem Download gelöscht werden.

## Aufgabe 3.2

`pop3_client.py` öffnet die TCP-Verbindung und liest zunächst die Begrüßung. `makefile('rb')` puffert den Empfang, damit TCP-Fragmente und mehrere gleichzeitig eintreffende Zeilen korrekt verarbeitet werden. Ein `recv()` entspricht keiner vollständigen POP3-Zeile. Jede gelesene Zeile muss mit CRLF enden; bei EOF oder einer beschädigten Statuszeile bricht der Client mit einer Fehlermeldung ab.

Danach folgen `USER`, `PASS`, `LIST` und `RETR`. Der Client wartet bei jedem Kommando auf die positive Statusantwort. Bei mehrzeiligen Antworten liest er bis zur Punktzeile und entfernt das Dot-Stuffing. Beim normalen Verlassen des `with`-Blocks sendet er `QUIT`. Bei einem Fehler schließt er die Verbindung ohne Lösch-Commit. Auch ein fehlgeschlagenes `QUIT` schließt die lokalen Ressourcen. Die Größe einer Antwort ist auf 20 MiB und die Länge einer einzelnen empfangenen Zeile auf 65536 Bytes begrenzt. Das sind Laborgrenzen, keine allgemeine POP3-Vorgabe.

Als zusätzliche Gegenprobe lief der eigene Client gegen den im Blatt verlinkten [GoPop3Server](https://github.com/kurthorvath/GoPop3Server) in einem isolierten lokalen Netzwerk. Anmeldung, `LIST`, Abruf und `QUIT` funktionierten. Die Referenzimplementierung lieferte zwei Nachrichten mit 151 und 115 Bytes; die erste hatte den Betreff „Hello Alice“. Dieser Mailbestand ist ein anderer als jener der Python-Datenbank.

## Aufgabe 3.3

`pop3_server.py` lädt die originale Klasse `SampleDataBase`. Der Server ruft `authenticate(username, password)` und `get_messages(username)` auf. Für jede Verbindung startet `ThreadingTCPServer` einen eigenen Thread. Unterschiedliche Benutzer können deshalb gleichzeitig arbeiten. Zwei gleichzeitige Transaktionen desselben Maildrops werden dagegen durch einen Benutzer-Lock verhindert, weil sonst Löschungen und Nachrichtennummern auseinanderlaufen könnten.

Die Nachrichtennummern werden beim Öffnen des Maildrops vergeben und bleiben innerhalb der Sitzung unverändert, während die ursprüngliche Datenbank-ID getrennt gespeichert wird, damit eine spätere Löschung auch nach einer neuen Nummerierung noch die richtige Nachricht betrifft. Der Server berechnet Bytegrößen nach der CRLF-Normalisierung, bevor Dot-Stuffing und Abschlusszeile hinzukommen. Leere Schlusszeilen bleiben erhalten. Bei `DELE` speichert die Sitzung zunächst nur die markierte Nummer; `QUIT` übernimmt die zugehörige Datenbank-ID in den lokalen Löschstand. Bei Abbruch entfällt dieser Schritt. Die Originaldatei wird nicht verändert. Der Löschstand besteht nur bis zum Serverneustart, weil die bereitgestellte Datenbank keine dauerhafte Löschschnittstelle anbietet.

Zusätzlich zu den Mindestkommandos sind `CAPA`, `UIDL` und `TOP` vorhanden. `UIDL` bildet aus Original-ID und Nachricht einen stabilen Hash. `TOP` liefert Header und die gewünschte Zahl an Textzeilen. Diese Kommandos erleichtern die Zusammenarbeit mit einem echten Mailprogramm. Es werden nur tatsächlich implementierte Fähigkeiten angekündigt. Inaktive POP3-Verbindungen haben ein Timeout von 600 Sekunden.

Für den GUI-Test wurde Claws Mail 4.3.1 mit einem frischen lokalen Profil verwendet. Konto: POP3, Server Loopback, Port 11110, Benutzer aus der Original-Datenbank, keine Verschlüsselung und keine Löschung nach dem Abruf. Nach „Get Mail“ erschienen alle vier Mails im Posteingang. Die erste Mail wurde geöffnet; Header und Nachrichtentext sind im [Screenshot](screenshots/pop3-claws.png) sichtbar. Claws zeigt Größen von 158, 148, 179 und 173 B an (658 B gesamt); diese GUI-Werte weichen von den durch `LIST` gelieferten Octet-Zahlen ab und werden nicht als deren Nachweis verwendet. Es wurden keine echten Konten eingebunden. Unabhängig davon wurden Anmeldung, `LIST` und `RETR` mit dem eigenen Client sowie die zusätzlichen Kommandos mit `poplib` geprüft.

## Aufgabe 3.4

Im Modus `09` liest der Server nur `GET /pfad` mit CRLF. Ein Verzeichnis wird zu `index.html` ergänzt. Die Antwort enthält ausschließlich die Dateibytes, keine Statuszeile und keine Header. Danach wird die Verbindung geschlossen. Fehlende Dateien, ungültige Anfragen und verbotene Pfade führen wie verlangt zum Schließen ohne Antwort.

Vor dem Öffnen wird der URL-Pfad dekodiert und gegen das aufgelöste Basisverzeichnis geprüft. `..`, kodierte Traversal-Versuche, Nullbytes und Symlinks aus dem Basisverzeichnis werden abgefangen. Während des Betriebs dürfen nicht vertrauenswürdige Benutzer den document root nicht verändern, weil die Pfadprüfung kein Betriebssystem-Sandboxing ersetzt.

Die Dateien wurden mit Headless Chromium 145.0.0.0 und Firefox Nightly getestet. Beide Browser senden aktuelle HTTP-Anfragen statt des alten Zweitoken-Formats. Der strikte HTTP/0.9-Modus schließt diese Anfragen ohne Antwort; die Webseite wird deshalb nicht korrekt angezeigt. Chromium meldete `ERR_EMPTY_RESPONSE`, Firefox `NS_ERROR_NET_EMPTY_RESPONSE`. Die [Chromium-](screenshots/http09-chromium.png) und [Firefox-Aufnahmen](screenshots/http09-firefox.png) zeigen den Fehlschlag. Socket-Tests bestätigen dagegen die korrekten Dateibytes bei einer echten HTTP/0.9-Anfrage.

## Aufgabe 3.5

Im Modus `10` liest ein Verbindungsthread nacheinander Request-Zeile und Header. Für jede vollständige Anfrage startet er einen neuen Request-Worker und wartet auf dessen Antwort. Auf einer persistenten Verbindung werden Antworten damit nicht vermischt. Verschiedene Verbindungen werden unabhängig bearbeitet. `GET` liefert die Datei; `HEAD` liefert dieselben Größenangaben ohne Dateikörper.

Die Antwort trägt immer `HTTP/1.0`, `Content-Length`, `Content-Type` und `Connection`. Eine Verbindung bleibt nur dann offen, wenn der Client ausdrücklich `Connection: keep-alive` verlangt und nicht gleichzeitig `close` sendet, weil bei widersprüchlichen Angaben der Verbindungsabbau Vorrang hat und kein weiterer Request mehr gelesen werden darf. Die Bytelänge zeigt dem Client, wo die Antwort endet, obwohl die Verbindung weiterläuft; dafür zählt die Länge der tatsächlich gesendeten Bytes und nicht die Zahl der Zeichen, die nach einer späteren Textdekodierung am Bildschirm erscheinen. Nach spätestens 100 Anfragen oder fünf Sekunden Inaktivität endet die Verbindung. Moderne HTTP/1.1-Request-Zeilen werden für den Browsertest akzeptiert, aber mit HTTP/1.0 beantwortet; daraus wird kein vollständiger HTTP/1.1-Server.

Request-Bodies, Chunked-Encoding und doppelte Header werden abgelehnt. Fehlende Dateien erhalten 404, unzulässige Pfade 403 und nicht unterstützte Methoden 405. Diese bewusste Beschränkung vermeidet mehrdeutiges Framing auf einer persistenten Verbindung. Der Server ist ein Lehrbeispiel, kein produktiver Webserver mit vollständiger HTTP-Abdeckung oder Lastbegrenzung.

Der Request-Handler schreibt Zeitstempel, Methode, Clientadresse und Clientport in eine threadsichere `queue.Queue`, sobald die Request-Zeile syntaktisch gültig ist; auch bei danach abgelehnten Headern bleibt die Methode damit im Log. Den Ausgabestrom beschreibt nur der Logger-Thread, damit sich Einträge nicht vermischen. Er gibt sie alle fünf Sekunden gemeinsam aus und beim regulären Beenden auch den letzten Rest. Beim Schließen wartet der Server auf laufende Request-Handler und beendet erst danach den Logger. Passwörter, Header und URL-Parameter werden nicht geloggt.

Im HTTP/1.0-Modus zeigen beide getesteten Browser „It works...!“ und beide Originalbilder korrekt an. Die Bilder wurden zusätzlich über `naturalWidth > 0` auf erfolgreiches Laden geprüft. [Chromium](screenshots/http10-chromium.png) und [Firefox](screenshots/http10-firefox.png) sind als echte Browser-Screenshots abgelegt. Die Testfälle prüfen zwei aufeinanderfolgende Requests über dieselbe TCP-Verbindung und mehrere parallele Verbindungen.

## Prüfung und Abgabe

32 automatisierte Tests liefen mit Python 3.8.20 und 3.14.7 erfolgreich durch. Sie verwenden eigene Testdaten und unabhängige Protokollclients aus `poplib` und `http.client`. Geprüft sind unter anderem ungültige HTTP/0.9-Steuerzeichen, leere RETR-Antworten, TOP ohne Nachrichtenkörper, Headerfehler, `Connection: close` bei widersprüchlichem Keep-Alive, das Inaktivitätstimeout, Loggerausfälle vor und während des Serverstarts, das Warten auf laufende Handler beim Schließen, Parallelität, Dot-Stuffing, Maildrop-Lock auch nach Verbindungsabbruch, Lösch-Commit und Rollback. Mit der Originaldatenbank bestätigte ein separater Integrationstest vier Nachrichten mit 184, 185, 154 und 164 Octets; der erste Abruf stimmte bytegenau mit dem CRLF-normalisierten Original überein.

Beide Moodle-Abgaben nennen am 19.10.2026 den 17.11.2026, 08:00 Uhr: [Horvath](https://moodle.aau.at/mod/assign/view.php?id=1489882) und [Alkhateeb](https://moodle.aau.at/mod/assign/view.php?id=1489881). Raphael hat Gruppe 1 sowie die Teammitglieder Raphael Bleier, Devis und Fabio angegeben. Die Zuordnung zu einer der beiden Aktivitäten wurde nicht geprüft. Das lokale Archiv `ueb03-gruppe01.zip` enthält die aktuellen Artefakte und Gruppeninfo. Eingereicht wurde nichts.

Die PDFs lassen sich mit pdfLaTeX bauen. Jeden Befehl zweimal ausführen:

```bash
pdflatex -halt-on-error -jobname=loesung_blatt03 '\def\explainmode{0}\input{blatt03.tex}'
pdflatex -halt-on-error -jobname=erklaerung_blatt03 '\def\explainmode{1}\input{blatt03.tex}'
```

## Quellen

Grundlagen sind das Moodle-Blatt 03, die Datenbankschnittstelle, der mitgelieferte document root sowie `rn-chapter-2`, Folien 10–11, 36–37 und 59–60. Die Originalunterlagen bleiben im Kurs. Normative Quellen: [RFC 1939](https://www.rfc-editor.org/rfc/rfc1939), Abschnitte 3–7; [RFC 2449](https://www.rfc-editor.org/rfc/rfc2449), Abschnitte 4–6; [RFC 1945](https://www.rfc-editor.org/rfc/rfc1945), Abschnitte 5–6; [RFC 8314](https://www.rfc-editor.org/rfc/rfc8314) für die TLS-Einordnung; [RFC 9051](https://www.rfc-editor.org/rfc/rfc9051) für IMAP.
