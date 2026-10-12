# Rechnernetze: Übungsblatt 01

Erklärung als PDF: [erklaerung_blatt01.pdf](erklaerung_blatt01.pdf). LaTeX-Quelle: [erklaerung_blatt01.tex](erklaerung_blatt01.tex).

| Aufgabe | Datei | Inhalt |
|---|---|---|
| 1.1 | `hello.py` | Name, Python-Version und Arbeitsverzeichnis |
| 1.2 | `text_bytes.py` | UTF-8, `str` und `bytes` |
| 1.3 | `convert.py` | UTF-8-Dateien kopieren, Zeilenenden normalisieren, Fehler melden |
| 1.4 | `protocol.py` | Nachrichtenformat mit `struct` erzeugen und parsen |
| 1.5 | `threaded_calc.py` | Dateiwerte mit Threads berechnen, auch bei ungerader Aufteilung |
| 1.6 | `thread_safety.py` | Gemeinsame Summe mit und ohne `Lock` vergleichen |
| 1.7 | `producer_consumer.py` | Producer und Consumer mit begrenzter `queue.Queue` |

## Ausführen

Die Programme verwenden nur die Python-Standardbibliothek. Getestet wurde mit Python 3.8.20; die Einführungsfolien empfehlen Python 3.8.5 oder neuer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python hello.py
python text_bytes.py --text 'Grüße aus Klagenfurt'
python convert.py eingabe.txt ausgabe.txt
python protocol.py --data --sequence 42 --text 'Hallo Netzwerk'
python threaded_calc.py zahlen.txt --threads 3
python thread_safety.py zahlen.txt --threads 4 --repeats 3
python producer_consumer.py --count 20 --queue-size 3
python3 -m unittest discover -s tests -v
```

`zahlen.txt` enthält eine Gleitkommazahl pro Zeile. `convert.py` liest LF, CRLF und CR ein und schreibt immer LF. Für den Test mit derselben Python-Version:

```bash
uv python install 3.8.20
uv run --python 3.8.20 python -m unittest discover -s tests -v
```

## Lösungen und kurze Erklärungen

### 1.1 Python-Umgebung

`hello.py` zeigt den Namen, den die laufende Python-Version über `platform.python_version()` meldet, und das Arbeitsverzeichnis von `os.getcwd()`. Der Name lässt sich mit `--name` ändern.

### 1.2 Text und Bytes

`str` enthält Unicode-Zeichen. `bytes` enthält Zahlen von 0 bis 255. UTF-8 kann ein Zeichen mit mehreren Bytes codieren. Darum kann `len(text)` kleiner als `len(text.encode("utf-8"))` sein. Bei einer falschen Kodierung kann Dekodieren fehlschlagen oder falsche Zeichen ergeben. Netzwerkprogramme senden Bytes; Text muss vor dem Senden kodiert und nach dem Empfang passend dekodiert werden.

### 1.3 Datei-I/O

`convert.py` nimmt Ein- und Ausgabedatei als Argumente. `newline=None` vereinheitlicht die eingelesenen Zeilenenden; beim Schreiben setzt `newline="\n"` überall LF. Fehlende Parameter meldet `argparse`. Dateifehler, ungültiges UTF-8 und identische Ein-/Ausgabepfade werden mit einer Fehlermeldung und Exitcode 1 beendet. `with` schließt Dateien auch bei einem Fehler.

### 1.4 Binärnachricht

Der erste 32-Bit-Wert enthält Version (5 Bit, Wert 2), reservierte Bits (9 Bit), D- und U-Flag (je 1 Bit) sowie Sequenznummer (16 Bit). Danach folgen die 32-Bit-Payload-Länge und die Payload. `struct`-Format `!II` legt Big Endian fest. `parse_message` kontrolliert Version, reservierte Bits, positive Sequenznummer und exakte Payload-Länge. Der Test vergleicht auch einen konkreten Byte-String.

### 1.5 Threads

Die Elemente werden mit `divmod` in zusammenhängende, überschneidungsfreie Bereiche geteilt. Die ersten `Rest` Threads bekommen je ein zusätzliches Element; so fehlt bei einer nicht teilbaren Arraylänge nichts und kein Wert wird doppelt berechnet. Jeder Thread schreibt sein Teilergebnis in einen eigenen Platz. `start()` startet den Thread, `join()` wartet auf sein Ende. Teilweise fehlgeschlagene Threadstarts sammeln schon gestartete Worker ein; Workerfehler werden an den aufrufenden Thread weitergegeben. Getrennte Datenbereiche und Ergebnisplätze vermeiden konkurrierende Schreibzugriffe. CPython-Threads machen CPU-lastige Python-Berechnungen wegen des GIL nicht automatisch schneller; hier geht es um die Aufteilung und das Warten auf alle Worker.

### 1.6 Thread Safety

`result += value` besteht gedanklich aus Lesen, Addieren und Schreiben. Wenn mehrere Threads dazwischenlaufen, kann ein Update den anderen überschreiben. `thread_safety.py` wiederholt den Vergleich standardmäßig dreimal und gibt auch die erwartete Summe aus einer sequentiellen Berechnung aus. Im ungeschützten Lauf sorgt eine Barriere dafür, dass alle Threads denselben alten Wert lesen und der verlorene Beitrag reproduzierbar sichtbar wird. Mit `Lock` läuft die Änderung innerhalb eines kritischen Abschnitts; der Lock wird danach sofort wieder freigegeben. Bei einem Workerfehler wird die Barriere abgebrochen und der Fehler weitergegeben; bei einem Startfehler werden bereits gestartete Threads zuerst eingesammelt.

### 1.7 Producer-Consumer

`queue.Queue(maxsize=...)` schützt Einfügen und Entnehmen zwischen Threads und blockiert den Producer bei voller Queue. `get()` wartet, wenn die Queue leer ist. Ein eindeutiges Sentinel-Objekt zeigt das Produktionsende an; `task_done()` und `join()` lassen den Hauptthread warten, bis alle Queue-Einträge abgearbeitet sind. Zeitlimits bei `put()` und `get()` lassen die Worker auf Fehler reagieren, statt unbegrenzt zu warten. Producer- und Consumer-Fehler werden an den aufrufenden Thread weitergegeben; teilweise fehlgeschlagene Threadstarts beenden und sammeln bereits gestartete Worker ein. Eine normale Liste bietet diese Synchronisation nicht.

## KI-Nutzung

Hermes Agent mit OpenAI GPT-6 Luna (`gpt-6-luna`), verwendet am 12.10.2026. Am Anfang jeder Python-Datei stehen Tool, Modell, Datum und der jeweilige Aufgabenblatt-Auszug, der als Anfrage diente. Laut Aufnahmefolien zur LV ist generative KI ausdrücklich erlaubt und muss gekennzeichnet werden. Die Gruppennummer ist noch nicht bekannt; deshalb ist kein gruppenspezifisches Abgabearchiv erstellt und es wurde nichts auf Moodle eingereicht.

## Prüfen

```bash
python3 -m unittest discover -s tests -v
```
