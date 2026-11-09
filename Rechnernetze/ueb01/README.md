# Rechnernetze: Übungsblatt 01

Erklärung als PDF: [erklaerung_blatt01.pdf](erklaerung_blatt01.pdf) · [KI-Kennzeichnung und offene Herkunftslücke](KI_NUTZUNG.md) · LaTeX-Quelle: [erklaerung_blatt01.tex](erklaerung_blatt01.tex).

Die Aufgaben 1.1 bis 1.7 sind umgesetzt. Am 24.10.2026 bestanden in der lokalen Arbeitsfassung alle 37 Tests unter Python 3.8.20 und Python 3.11. Diese Zwischenänderungen sind noch nicht veröffentlicht. Ihre KI-Kennzeichnung ist unvollständig; deshalb ist die Arbeitsfassung nicht abgabefertig.

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

Die Programme verwenden nur die Python-Standardbibliothek. Das Aufgabenblatt verlangt Python 3. Getestet wurde mit Python 3.8.20.

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

`hello.py` gibt den Namen aus (standardmäßig Raphael Bleier, änderbar mit `--name`), dazu die Python-Version über `platform.python_version()` und das Arbeitsverzeichnis über `os.getcwd()`.

### 1.2 Text und Bytes

`str` enthält Unicode-Zeichen. `bytes` enthält Zahlen von 0 bis 255. UTF-8 kann ein Zeichen mit mehreren Bytes codieren. Darum kann `len(text)` kleiner als `len(text.encode("utf-8"))` sein. Bei einer falschen Kodierung kann Dekodieren fehlschlagen oder falsche Zeichen ergeben. Netzwerkprogramme senden Bytes; Text muss vor dem Senden kodiert und nach dem Empfang passend dekodiert werden.

### 1.3 Datei-I/O

`convert.py` nimmt Ein- und Ausgabedatei als Argumente. `newline=None` vereinheitlicht die eingelesenen Zeilenenden; beim Schreiben setzt `newline="\n"` überall LF. Fehlende Parameter meldet `argparse`. Dateifehler, ungültiges UTF-8 und dieselbe Eingabe-/Ausgabedatei werden mit einer Fehlermeldung und Exitcode 1 beendet; erkannt werden auch Symlink- und Hardlink-Aliase. `with` schließt Dateien auch bei einem Fehler.

### 1.4 Binärnachricht

Das erste 32-Bit-Wort enthält laut Grafik die Version in den Diagrammbits 0–4 (Wert 2), neun reservierte Bits, die Flags D/U und die 16-Bit-Sequenznummer. Die Grafik zählt von links; im Big-Endian-Wort liegt das Versionsfeld daher in den höchstwertigen fünf Bits. Danach folgen Payload-Länge und Payload. `struct`-Format `!II` schreibt beide Wörter in Network Byte Order. Für D=U=0, Sequenznummer 42 und Payload-Länge 11 ergibt sich `10 00 00 2a 00 00 00 0b`; ein Test prüft diese Feldbelegung direkt.

Hinweis zur Angabe: Die Bildprüfung bestätigt, dass die Round-Trip-Abbildung auf Seite 3 `40 00 00 2a 00 00 00 0b …` zeigt. Im Feldkasten stehen keine konkreten Eingabewerte; aus den Bytes lassen sich aber `D=U=0`, Sequenznummer 42 und Payload-Länge 11 ablesen. Der Payload selbst ist nur als Auslassung dargestellt. Nach dem Bitfeldschema auf Seite 2 steht `0x40` im fünf Bit breiten Versionsfeld für 8, nicht für 2. Das Beispiel widerspricht damit der Vorgabe „Versionsnummer immer 2“. Die Implementierung folgt dem Feldschema und der festen Version 2; für die aus der Abbildung erkennbaren übrigen Werte ergibt sich `10 00 00 2a 00 00 00 0b`. Die Abweichung ist dokumentiert; eine Klärung durch die Lehrveranstaltung steht aus.

### 1.5 Threads

Die Elemente werden mit `divmod` in zusammenhängende, überschneidungsfreie Bereiche geteilt. Die ersten `Rest` Threads bekommen je ein zusätzliches Element; so fehlt bei einer nicht teilbaren Arraylänge nichts und kein Wert wird doppelt berechnet. Jeder Thread schreibt sein Teilergebnis in einen eigenen Platz. `start()` startet den Thread, `join()` wartet auf sein Ende. Teilweise fehlgeschlagene Threadstarts sammeln schon gestartete Worker ein; Workerfehler werden an den aufrufenden Thread weitergegeben. Getrennte Datenbereiche und Ergebnisplätze vermeiden konkurrierende Schreibzugriffe. CPython-Threads machen CPU-lastige Python-Berechnungen wegen des GIL nicht automatisch schneller; hier geht es um die Aufteilung und das Warten auf alle Worker.

### 1.6 Thread Safety

`result += value` besteht gedanklich aus Lesen, Addieren und Schreiben. Wenn mehrere Threads dazwischenlaufen, kann ein Update den anderen überschreiben. `thread_safety.py` führt zuerst die direkte ungeschützte Summe mit `+=` und die geschützte Variante mit `Lock` aus. Standardmäßig wiederholt das Programm den Vergleich dreimal und gibt die sequenzielle Sollsumme aus. Mit `zahlen.txt` ergaben die drei direkten Läufe unter Python 3.8.20 jeweils 15088760.258000, genau wie die Lock-Läufe und die sequenzielle Summe; in diesem Versuch war kein verlorener Beitrag zu beobachten. Das ist kein Beweis für Thread Safety: Ein verlorenes Update hängt von Laufzeit und Thread-Scheduling ab. Ein zusätzlicher Kontrolllauf mit Barriere lässt alle Threads denselben alten Wert lesen und macht den möglichen verlorenen Update reproduzierbar sichtbar. Dieser Kontrolllauf ersetzt den direkten Versuch nicht. Der Lock lässt immer nur einen Thread gleichzeitig auf die gemeinsame Summe zugreifen. Er umfasst nur diese kurze Änderung, damit andere Threads nicht unnötig warten und die Arbeit nicht stärker als nötig serialisiert wird. Bei einem Workerfehler wird die Barriere abgebrochen und der Fehler weitergegeben; bei einem Startfehler werden bereits gestartete Threads eingesammelt.

### 1.7 Producer-Consumer

`queue.Queue(maxsize=...)` schützt Einfügen und Entnehmen zwischen Threads und blockiert den Producer bei voller Queue. `get()` wartet, wenn die Queue leer ist. Ein eindeutiges Sentinel-Objekt zeigt das Produktionsende an; `task_done()` und `join()` lassen den Hauptthread warten, bis alle Queue-Einträge abgearbeitet sind. Zeitlimits bei `put()` und `get()` lassen die Worker auf Fehler reagieren, statt unbegrenzt zu warten. Producer- und Consumer-Fehler werden an den aufrufenden Thread weitergegeben; teilweise fehlgeschlagene Threadstarts beenden und sammeln bereits gestartete Worker ein. Eine normale Liste bietet diese Synchronisation nicht.

## Gruppe und Abgabe

Vorbereitet für Gruppe 1 mit Raphael Bleier, Devis und Fabio, wie von Raphael angegeben. Die tatsächliche Zuordnung zu einer der Moodle-Abgabeaktivitäten wurde nicht geprüft. Das lokale Archiv `ueb01-gruppe01.zip` enthält Programme, Tests, `zahlen.txt`, Erklärung und Gruppeninfo. Die widersprüchliche Bytefolge ist dokumentiert; eingereicht wurde nichts.

## Prüfen

```bash
python3 -m unittest discover -s tests -v
```
