# Rechnernetze: Übungsblatt 04

[KI-Kennzeichnung](KI_NUTZUNG.md). Gruppe 1 (Raphael Bleier, Devis, Fabio). Welche der beiden Moodle-Abgaben (Horvath oder Alkhateeb) das ist, habe ich nicht geprüft. Beide nennen Dienstag, 24.11.2026, 08:00. Nichts wurde hochgeladen.

Gemessen am 30.10.2026 mit Mininet 2.3.0 und Python 3.13.3. `sudo mn` ist gestartet, hat aber gemeldet, dass kein Standard-OpenFlow-Controller da ist, und ist auf eine OVS-Bridge zurückgefallen. Deshalb fehlt `c0` in der Ausgabe. Die Host-Adressen stimmen trotzdem mit der Abbildung überein. `xterm` ist hier nicht installiert, also liefen dieselben Befehle in den Netzwerk-Namespaces der Hosts. Das ist dieselbe Sicht, die ein xterm auf h1 oder h2 hätte.

## Standardtopologie

`nodes` listet die Knotennamen, hier kamen `h1 h2 s1`, und ein Controller-Knoten fehlt wegen des Fallbacks oben.

`net` zeigt, welches Interface an welchem Gegenstück hängt.

```
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0
```

`links` prüft, ob die Enden oben sind, und beide Links waren in diesem Lauf `OK OK`.

`dump` nennt Klasse, Interfaces, IP und PID. Die PIDs gelten nur für diesen Start.

```
<Host h1: h1-eth0:10.0.0.1 pid=692451>
<Host h2: h2-eth0:10.0.0.2 pid=692453>
<OVSBridge s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=692458>
```

`exit` räumt die virtuellen Interfaces wieder ab, und danach waren h1-eth0 und s1 weg.

## Aufgabe 4.1

h1 hat zwei Interfaces. `lo` trägt 127.0.0.1/8, und `h1-eth0` trägt 10.0.0.1/8. h2 hat analog `lo` und `h2-eth0` mit 10.0.0.2/8. Die IPv4-Adresse von h1 ist also 10.0.0.1, die von h2 ist 10.0.0.2. Genau so steht es in der Abbildung, jeweils als /8.

Auf h1 liegt nur diese Route, keine Default-Route:

```
10.0.0.0/8 dev h1-eth0 proto kernel scope link src 10.0.0.1
```

10.0.0.2 steckt im selben Netz, deshalb reicht die verbundene Route. Die MAC-Adresse von h1-eth0 war in diesem Lauf `f6:55:9d:e0:21:fb`, bei h2 `02:6a:d4:90:9e:22`. Beim nächsten Start sind andere MACs normal, weil Mininet sie neu vergibt.

Der Unterschied zu einer normalen Schnittstelle ist größer, als die ähnlichen `ip addr`-Zeilen zuerst vermuten lassen: `h1-eth0` ist nur ein Ende eines veth-Paares in einem eigenen Netzwerk-Namespace, es gibt sie nur solange Mininet läuft, und dahinter steckt kein physisches Kabel und kein eigener Rechner. `pingall` kam in diesem Lauf auf 0% Verlust (2/2).

`h1 hostname` und `h2 hostname` lieferten beide `ubuntu`, Python war 3.13.3, und `pwd` zeigte bei beiden das Verzeichnis, aus dem Mininet gestartet wurde. Die Hosts teilen sich Dateisystem und Hostname. Getrennt ist der Netzwerk-Namespace. Deshalb sieht ein Programm in h1 die Interfaces von h2 nicht: `ip addr` liest nur die Interfaces des eigenen Namespace, und h2-eth0 liegt in einem anderen.

## Aufgabe 4.2

Ohne xterm habe ich `ip addr`, `ip route` und `hostname` direkt in den beiden Namespaces ausgeführt. Das ist die Ausgabe, die in den beiden Fenstern stehen würde.

Gleich bleibt `lo` mit 127.0.0.1/8 und der Hostname. Verschieden sind Interface-Name, MAC, IPv4 der Daten-Schnittstelle und die Route: bei h1 Gerät `h1-eth0` und Quelle 10.0.0.1, bei h2 `h2-eth0` und Quelle 10.0.0.2. Das Präfix 10.0.0.0/8 ist dasselbe, weil beide Hosts in diesem einen Netz stecken.

## Aufgabe 4.3

Der Server bindet 10.0.0.2:5000. Das ist die IPv4-Adresse von h2, nicht die von h1, und der Client auf h1 schickt dorthin.

127.0.0.1 geht nicht. Loopback bleibt im eigenen Namespace, ein Paket an 127.0.0.1 auf h1 erreicht also h1 selbst und nie h2. h2 ist nur über 10.0.0.2 erreichbar.

Port 5000 ist der UDP-Zielport, an den der Server gebunden ist. Der Kernel liefert ein ankommendes Datagramm an genau den Socket, der dieses Paar aus Adresse und Port besitzt. Der Quellport des Clients ist flüchtig und bei jedem Start ein anderer.

`b"Hello from Mininet!"` ist eine Bytefolge. `sendto` schickt Bytes, keinen Python-String. Ohne das `b` wäre der Typ `str`, und der Aufruf scheitert.

Im Lauf hat der Server gemeldet: `Received from ('10.0.0.1', 34726): b'Hello from Mininet!'`. Ein zweiter Lauf für den Mitschnitt hatte den Quellport 34692. Die Nutzlast war beide Male dieselbe.

## Aufgabe 4.4

Mitschnitt am Switch-Port Richtung h1, ein UDP-Datagramm, Datei [udp-hello.pcap](udp-hello.pcap):

```
7e:ce:55:c9:bc:c8 > 22:35:0a:8d:14:98, ethertype IPv4 (0x0800), length 61
10.0.0.1.34692 > 10.0.0.2.5000: UDP, length 19
```

Quelle 10.0.0.1, Ziel 10.0.0.2. Quellport 34692, Zielport 5000.

Die IP-Länge im Paket ist 47. Davon sind 20 Byte IPv4-Header, weil das erste Byte 0x45 ist und die Headerlänge damit 5 Wörter beträgt. Bleiben 27 Byte UDP. Das UDP-Längenfeld steht im Hexdump als `001b`, also 27. Davon sind 8 Byte Header und 19 Byte Nutzlast. Der UDP-Header ist damit 8 Byte, nicht nur nach Lehrbuch, sondern aus diesem Paket.

Die Nutzlast ist 19 Byte. Im Hexdump ab `48656c6c6f20` steht `Hello from Mininet!`, genau die Bytefolge aus dem Client.

tcpdump meckert hier über eine offene UDP-Prüfsumme (`bad udp cksum`). Das ist Checksum-Offload an der virtuellen Schnittstelle, der Mitschnitt sieht die Summe vor der Fertigstellung. Der Server hat die Nutzlast trotzdem angenommen, die Warnung ist also kein Fehler im Programm.

Schichten, am selben Paket: Ethernet trägt die MAC-Adressen und den Typ 0x0800. Darüber liegt IPv4 mit den beiden Adressen und Protokoll 17. UDP nennt die Ports und die Länge. Die Nutzlast ist kein eigenes Protokoll, nur die Bytes aus `sendto`.

## RN-Lab

`topology.py` legt die Hosts in `RNLabTopo.build` an: client, router (Klasse `LinuxRouter`), server. Die Links stehen in den beiden `addLink`-Aufrufen, mit `TCLink`, `delay="20ms"` und `loss=0`. Die Adressen stehen dort als Konstanten (`CLIENT_IP` 10.0.1.2/24, Router 10.0.1.1/24 und 10.0.2.1/24, Server 10.0.2.2/24). Gesetzt werden sie erst in `start_lab.py`, in `configure_network`. `LinuxRouter.config` schaltet `ip_forward` ein. Die Dateien habe ich nicht geändert.

`start_lab.py` öffnet am Ende drei Terminals. Ohne xterm und ohne Display habe ich nur `configure_network`, `show_state` und `verify_connectivity` aufgerufen. Alle sechs Ping-Prüfungen der Vorlage waren OK, inklusive client nach server und zurück. Das reicht für die Routingfragen. Die GUI-Fenster selbst fehlen hier.

## Aufgabe 4.5

`ping -c 4 10.0.2.2` vom Client: 4 gesendet, 4 empfangen, 0% Verlust. RTT etwa 80,2 ms (80,082 bis 80,358). TTL 63, nicht 64. Das Paket ist über den Router gelaufen, der die TTL um eins senkt. 80 ms passen zu 20 ms je Richtung und Link, hin zwei Links und zurück zwei Links.

`ip route get 10.0.2.2` auf dem Client lieferte `10.0.2.2 via 10.0.1.1 dev client-eth0 src 10.0.1.2`. Der Client schickt also an 10.0.1.1. Der Router hat 10.0.2.0/24 an `router-eth1` mit Quelle 10.0.2.1 und liefert dort an 10.0.2.2 aus.

Der Router braucht zwei Adressen, weil er in zwei Netzen hängt. 10.0.1.1 ist sein Ende im Client-Netz, 10.0.2.1 sein Ende im Server-Netz. Eine Adresse kann nicht in beiden /24-Netzen liegen.

Der Client braucht eine Default-Route, weil 10.0.2.2 nicht in 10.0.1.0/24 liegt. Ohne den Eintrag `default via 10.0.1.1` wüsste er nicht, wohin das Paket soll. Direkt über sein eigenes Ethernet geht es nicht: anderes Subnetz, keine gemeinsame Schicht-2-Verbindung, der Server hängt am anderen Interface des Routers.

IP-Forwarding heißt, dass der Router ein Paket annimmt, dessen Ziel nicht er selbst ist, und es über das andere Interface weiterschickt. Ohne `net.ipv4.ip_forward = 1` würde er es verwerfen, in diesem Lauf stand der Wert auf 1.

## Aufgabe 4.6

`tcp_server.py` macht die geforderten Schritte: Socket, `bind`, `listen`, `accept`, `recv`, schließen. Ohne `--multi` liest er bis zum Schreib-Shutdown des Clients und schickt eine Antwort. Mit `--multi` bleibt die Verbindung offen, jede Zeile ist eine Nachricht, und `QUIT` beendet die Sitzung.

`tcp_client.py` verbindet, sendet und liest die Antwort. Bei einer Nachricht sendet er, macht `shutdown(SHUT_WR)`, liest die Antwort und schließt. Bei mehreren Nachrichten gehen mehrere Zeilen über denselben Socket, danach `QUIT`.

Im RN-Lab, Server auf 10.0.2.2:5000, kam `Connection from ('10.0.1.2', 56754)` und `Received: b'Hello from TCP'`. Der Client bekam `ACK: Hello from TCP`. Drei Zeilen über eine Verbindung, Quellport 56764: der Server druckte `eins`, `zwei` und `drei` und antwortete auf jede Zeile, bevor `BYE` kam.

Der Mitschnitt [tcp-handshake.pcap](tcp-handshake.pcap) zeigt den Aufbau. Drei Segmente, danach erst Nutzlast.

1. SYN, Flags `[S]`, 10.0.1.2:52782 nach 10.0.2.2:5000, Sequenz 1687460832, Länge 0, TTL 64.
2. SYN-ACK, Flags `[S.]`, zurück von 10.0.2.2:5000, Sequenz 1150169307, ACK 1687460833, TTL 63.
3. ACK, Flags `[.]`, 10.0.1.2 nach 10.0.2.2, Sequenz 1687460833, ACK 1150169308, Länge 0.

Dann ein Segment mit Flags `[P.]` und Länge 14. Im Klartext steht dort `Hello from TCP`. Die Antwort hat Länge 19 und den Text `ACK: Hello from TCP`. Der Abbau folgt mit FIN in beide Richtungen. Auch hier steht bei tcpdump `cksum incorrect`, wieder Offload, die Verbindung lief durch.

Ein einzelnes `recv()` ist keine Nachricht. TCP liefert einen Bytestrom, zwei `send()` können in einem `recv()` ankommen, und ein `send()` kann auf mehrere `recv()` verteilt werden. Der lokale Test schickt `alpha\nbeta\n` in einem `sendall`. Ein `recv(4096)` liefert beide Zeilen auf einmal. Deshalb die Zeilengrenze im Mehrnachrichten-Modus, und im Einzelnachrichten-Modus das Schließen der Schreibseite als Ende.

Eine Verbindung für mehrere Nachrichten spart den Handshake und den Abbau pro Satz, es gibt weniger RTTs, und das Fenster muss nicht jedes Mal neu wachsen. Bei 80 ms RTT im Labor, gemessen am Ping über die beiden Links mit je 20 ms, wäre jede neue Verbindung spürbar teurer als eine weitere Zeile auf der schon offenen Verbindung.

## Starten

Im Blattordner, ohne Mininet, nur die TCP-Gegenprobe:

```bash
python3 -m unittest discover -s tests -v
```

Am 30.10.2026 sind alle drei Tests durchgelaufen, lokal und ohne Mininet, nur mit der Python-Standardbibliothek.

In der Standardtopologie, nach `sudo mn`, auf h2 den Server und auf h1 den Client:

```bash
python3 udp_server.py --host 10.0.0.2 --port 5000
python3 udp_client.py --host 10.0.0.2 --port 5000
```

In der RN-Lab-Topologie läuft der Server auf dem Server-Host und der Client auf dem Client-Host:

```bash
python3 tcp_server.py --host 10.0.2.2 --port 5000
python3 tcp_client.py --host 10.0.2.2 --port 5000 --message "Hello from TCP"
python3 tcp_server.py --host 10.0.2.2 --port 5000 --multi
python3 tcp_client.py --host 10.0.2.2 --port 5000 --multi --message eins --message zwei
```

Die Vorlage `topology.py` und `start_lab.py` bleibt außerhalb. Sie wird nicht mit abgegeben, weil sie zum Labor gehört und nicht verändert werden soll.
