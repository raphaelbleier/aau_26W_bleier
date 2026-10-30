# Kennzeichnung der KI-Nutzung

Die Aufnahmefolien verlangen auf Seite 18 Tool, Version und Datum, und bei übernommenem Code auch die Anfrage. Diese Kennzeichnung gilt für topology.py, start_lab.py, die Tests und die Texte in diesem Ordner.

Tool: Hermes Agent. Modell: grok-4.7. Datum: 30.10.2026.

Die Topologie folgt der Vorlage und Ü 7.2. Die Anfrage war: topology.py um einen zusätzlichen Router r3 und einen alternativen Weg zwischen r1 und dem Server erweitern, neue Verbindungen für die Router-zu-Router-Kommunikation, und in Ü 7.3 die beiden Wege mit delayA 5ms und delayB 30ms belegen. Ü 7.4 war: eine statische Route von r3 zum Server entfernen, die Ursache mit ping, tracepath und einem Mitschnitt finden, und die Route wieder eintragen.

Die Zahlen zu Interfaces, Routen, Ping, tracepath und dem ICMP-Mitschnitt sind Läufe mit Mininet 2.3.0 und Python 3.13.3 auf diesem Rechner am 30.10.2026. xterm fehlt hier. ip, ping und tracepath liefen in den Namespaces. tshark hat die PCAP gelesen, ein Wireshark-Fenster gab es nicht.

Es wurde nichts auf Moodle eingereicht.
