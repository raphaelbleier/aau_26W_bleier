# Kennzeichnung der KI-Nutzung

Die Aufnahmefolien verlangen auf Seite 18 Tool, Version und Datum, und bei übernommenem Code auch die Anfrage. Diese Kennzeichnung gilt für die Programme, die Tests und die Erklärung in diesem Ordner.

Tool: Hermes Agent. Modell: grok-4.7. Datum: 30.10.2026.

Die UDP-Programme folgen der Angabe in Ü 4.3, also Bindung an 10.0.0.2:5000, `recvfrom` und die Nutzlast als Bytes. Ergänzt sind nur Kommandozeilenargumente, damit derselbe Code in der Standardtopologie und in der RN-Lab-Topologie läuft.

Die TCP-Programme setzen Ü 4.6 um. Die Anfrage aus der Angabe war: Socket erzeugen, an IP-Adresse und Port binden, auf Verbindungen warten, mit `accept()` annehmen, Daten empfangen und die Verbindung schließen. Der Client soll verbinden, eine Nachricht senden, gegebenenfalls eine Antwort lesen und schließen, danach mehrere Nachrichten über dieselbe TCP-Verbindung.

Es wurde nichts auf Moodle eingereicht.
