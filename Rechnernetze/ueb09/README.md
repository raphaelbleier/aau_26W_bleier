# Rechnernetze: Übungsblatt 09

[KI-Kennzeichnung](KI_NUTZUNG.md). Gruppe 1 (Raphael Bleier, Devis, Fabio). Welche der beiden Moodle-Abgaben das ist, habe ich nicht geprüft. Horvath nennt Dienstag, 26.01.2027, 08:00. Alkhateeb zeigt Montag, 26.01.2026, 08:00. Das Jahr passt nicht zum Semester, ich habe es nicht geraten. Nichts wurde hochgeladen.

Gemessen am 30.10.2026 mit Mininet 2.3.0, Python 3.13.3, tcpdump 4.99.4 und Open vSwitch 3.5.1. `xterm` fehlt, also liefen `ip`, `ping` und die beiden Python-Programme in den Namespaces. Das ist dieselbe Sicht wie in einem Terminal auf dem Host. Ein Wireshark-Fenster gab es nicht.

Die Vorlage (`topology.py`, `start_lab.py`, `tcp_client.py`, `tcp_server.py`, die drei capture-Skripte) habe ich nicht verändert und nicht mit ins Repo gelegt. Auf dem Blatt gibt es keine Übung 9.2. Es geht von 9.1 nach 9.3. Die Zeichnung sagt switch1 und switch2, die Vorlage heißt sw1 und sw2. Den oberen Knoten nennt die Zeichnung nur client. Vorlage und der Abschnitt zum erwarteten Verhalten heißen ihn client1.

Zwei Starts, dieselbe Vorlage. Der erste hat die Erreichbarkeit geprüft. Der zweite ist der mit den Mitschnitten. router-eth1 bekommt jedes Mal eine neue MAC, die zitiere ich nur aus dem zweiten Start. Die Adressen sind in beiden gleich.

## 9.1 Bestand

`ip -c=never -br addr` und `ip -c=never -br link` im zweiten Start:

- client1-eth0: 10.10.1.10/24, MAC `00:00:00:00:00:01`
- client2-eth0: 10.10.1.11/24, MAC `00:00:00:00:00:02`
- router-eth0: 10.10.1.1/24, MAC `00:00:00:00:00:03`
- router-eth1: 10.10.2.1/24, MAC `7e:f3:ca:f0:60:c1`
- server-eth0: 10.10.2.10/24, MAC `00:00:00:00:00:04`

Die 00:00:00-Adressen kommen von `autoSetMacs`. router-eth1 nicht, die setzt der Kernel beim zweiten Interface. 10.10.2.254 hatte keiner der vier Hosts.

Routen, ebenfalls zweiter Start:

```
client1: default via 10.10.1.1 dev client1-eth0
         10.10.1.0/24 dev client1-eth0 src 10.10.1.10
client2: default via 10.10.1.1 dev client2-eth0
         10.10.1.0/24 dev client2-eth0 src 10.10.1.11
router:  10.10.1.0/24 dev router-eth0 src 10.10.1.1
         10.10.2.0/24 dev router-eth1 src 10.10.2.1
server:  default via 10.10.2.254 dev server-eth0
         10.10.2.0/24 dev server-eth0 src 10.10.2.10
```

Der Router hat keine Default-Route. Braucht er nicht, beide Netze hängen direkt an ihm. `sysctl net.ipv4.ip_forward` war auf dem Router 1, auf client1, client2 und server 0. Im ersten Start waren sw1 und sw2 `standalone`, und `iptables -S` auf dem Server nur die drei ACCEPT-Policies, keine Extra-Regel.

Erreichbarkeit im ersten Start, `ping -c 3 -W 2`:

- client1 nach 10.10.1.1: 3 von 3, TTL 64, RTT 14,050/18,971/28,781/6,936 ms
- client2 nach 10.10.1.1: 3 von 3, TTL 64, RTT 14,054/18,969/28,799/6,950 ms
- client1 nach 10.10.1.11: 3 von 3, TTL 64, RTT 8,303/11,209/16,980/4,080 ms
- router nach 10.10.2.10: 3 von 3, TTL 64, RTT 14,180/19,060/28,790/6,879 ms
- server nach 10.10.2.1: 3 von 3, TTL 64, RTT 14,052/14,205/14,433/0,164 ms
- client1 nach 10.10.2.10: 3 gesendet, 0 empfangen, 100 Prozent Verlust, 2070 ms
- client2 nach 10.10.2.10: 3 gesendet, 0 empfangen, 100 Prozent Verlust, 2030 ms
- server nach 10.10.1.10: `From 10.10.2.10 icmp_seq=1 Destination Host Unreachable`, dasselbe für seq 2 und 3
- server nach 10.10.1.1: dieselbe Meldung, wieder von 10.10.2.10

Im zweiten Start, vor jeder Änderung, wieder 3 gesendet und 0 empfangen von client1 nach 10.10.2.10, 2064 ms. Beide Clients fallen aus, nicht nur einer. Das Client-LAN selbst geht. Der Router erreicht den Server. Der Server erreicht sein eigenes Gateway 10.10.2.1, aber nichts dahinter.

Nach den Pings im zweiten Start stand auf dem Server:

```
10.10.2.1 dev server-eth0 lladdr 7e:f3:ca:f0:60:c1 STALE
10.10.2.254 dev server-eth0 INCOMPLETE
```

client1 hatte nur `10.10.1.1 lladdr 00:00:00:00:00:03 REACHABLE`. Keinen Eintrag für 10.10.2.10. Der Router hatte beide Enden: 10.10.1.10 an router-eth0 und 10.10.2.10 an router-eth1.

`ip route get 10.10.1.10` auf dem Server, vor dem Fix:

```
10.10.1.10 via 10.10.2.254 dev server-eth0 src 10.10.2.10
```

## 9.3 Paketfluss

tcpdump lief nicht im Host, sondern am anderen Ende derselben Leitung. sw1-eth1 ist die Gegenstelle von client1-eth0, sw2-eth2 die von server-eth0. Dateien [before-client1.pcap](before-client1.pcap) und [before-server.pcap](before-server.pcap). Darin liegt auch IPv6 von der VM (Router Solicitation, mDNS). Das ist nicht der Fehler, die Zeilen zitiere ich nicht.

Vor dem Mitschnitt habe ich `ip neigh flush all` gemacht, damit das ARP im Capture steht.

Echo Request, id 36370, icmp id 4808, seq 1. Auf client1, TTL 64, Ziel-MAC ist der Router auf dem Client-LAN:

```
00:00:00:00:00:01 > 00:00:00:00:00:03, ethertype IPv4 (0x0800), length 98:
(tos 0x0, ttl 64, id 36370, offset 0, flags [DF], proto ICMP (1), length 84)
10.10.1.10 > 10.10.2.10: ICMP echo request, id 4808, seq 1, length 64
```

Davor das ARP, das dazugehört: `who-has 10.10.1.1 tell 10.10.1.10`, Antwort `10.10.1.1 is-at 00:00:00:00:00:03`. client1 fragt nicht nach 10.10.2.10. Das Ziel liegt nicht in 10.10.1.0/24, also geht der Frame an das Gateway.

Derselbe Request auf der Server-Leitung, 27 ms später. TTL 63, IP-id 36370 bleibt, die MACs nicht:

```
7e:f3:ca:f0:60:c1 > 00:00:00:00:00:04, ethertype IPv4 (0x0800), length 98:
(tos 0x0, ttl 63, id 36370, offset 0, flags [DF], proto ICMP (1), length 84)
10.10.1.10 > 10.10.2.10: ICMP echo request, id 4808, seq 1, length 64
```

Der Router hat weitergeleitet. Quelle ist jetzt router-eth1, Ziel ist der Server. Zwei Millisekunden später:

```
00:00:00:00:00:04 > ff:ff:ff:ff:ff:ff, ethertype ARP (0x0806):
Request who-has 10.10.2.254 tell 10.10.2.10
```

Keine Antwort. Seq 2 und seq 3 kommen genauso an, id 36383 und 36695, TTL 63, und jedes Mal wieder `who-has 10.10.2.254`. Ein Echo Reply ist in beiden Mitschnitten nicht drin.

Der TCP-Versuch danach. `tcp_server.py` lauscht auf 0.0.0.0:5000, `tcp_client.py` von client1 läuft in den Timeout nach 5 Sekunden. Auf der Client-Leitung nur SYN, Wiederholungen, kein SYN-ACK. Der erste:

```
00:00:00:00:00:01 > 00:00:00:00:00:03, ethertype IPv4 (0x0800), length 74:
(tos 0x0, ttl 64, id 63834, offset 0, flags [DF], proto TCP (6), length 60)
10.10.1.10.41372 > 10.10.2.10.5000: Flags [S], seq 1929350596, win 64240, length 0
```

Auf der Server-Leitung derselbe SYN, TTL 63, dieselbe IP-id 63834, dasselbe seq 1929350596. Danach wieder ARP nach 10.10.2.254, und kein SYN-ACK auf dem Draht. Der Handshake bricht am Rückweg ab, nicht am Hinweg.

`tcpdump` schreibt bei dem SYN `cksum 0x1756 (incorrect -> 0x2723)`. Das ist Checksum-Offload an der virtuellen Schnittstelle, wie beim UDP von Blatt 4. Der Stack hat den SYN gesehen und eine Antwort bauen wollen, sonst würde er nicht nach dem Next Hop dafür fragen. Die Anwendung hat die Verbindung nicht angenommen, `accept` wartet auf den Handshake.

Der Punkt, an dem der Fluss vom erwarteten abweicht, ist der Server nach dem Empfang. Hinweg: Client, sw1, Router, sw2, Server. Rückweg: der Server sucht 10.10.2.254 und findet niemanden. Der Router sieht die Antwort deshalb nie.

## 9.4 Hypothese

Die Default-Route des Servers zeigt auf eine Adresse, die es nicht gibt. Deshalb kommt der Request an, und die Antwort verlässt das Interface nicht.

Zwei Beobachtungen reichen der Angabe nicht als einzelne fehlgeschlagene Verbindung. Hier sind es vier, und sie hängen nicht an demselben Befehl:

- `ip route` und `ip route get 10.10.1.10` nennen `via 10.10.2.254`. Kein Host hat diese Adresse.
- `ip neigh` bleibt auf 10.10.2.254 bei INCOMPLETE. Im Mitschnitt geht `who-has 10.10.2.254 tell 10.10.2.10` an die Broadcast-MAC, eine Reply kommt nicht.
- Echo Request id 36370 steht auf beiden Seiten der Leitung, TTL 64 vor dem Router und 63 dahinter. Ein Echo Reply mit dieser id gibt es nicht. Der TCP-SYN id 63834 genauso: ankommen ja, SYN-ACK nein.
- Gegenprobe. Router nach 10.10.2.10 geht, TTL 64, weil das dasselbe Subnetz ist und keine Default-Route braucht. Server nach 10.10.2.1 geht auch. ip_forward auf dem Router ist 1, die Switches waren standalone, iptables hat nichts verworfen.

Die Anwendung ist nicht kaputt. Der Server bekommt den SYN, er kann nur nicht zurück. Ein Switch-Fehler wäre es auch nicht, sonst käme der Request nicht mit derselben IP-id an.

## 9.5 Ursache

Fehlerhaft war die Default-Route auf server-eth0: `default via 10.10.2.254`. 10.10.2.254 liegt in 10.10.2.0/24, deshalb installiert der Kernel die Route. Antworten tut dort niemand. Das Gateway des Server-LANs ist router-eth1, und das ist 10.10.2.1.

Nach der Diagnose, und erst dann, eine Zeile auf dem Server:

```
ip route replace default via 10.10.2.1 dev server-eth0
```

Die ersetzt den einen falschen Eintrag. Danach steht da `default via 10.10.2.1 dev server-eth0`, die Connected-Route 10.10.2.0/24 bleibt. Antworten an 10.10.1.0/24 gehen damit an den Router, der beide Netze kennt und ip_forward an hat. Genau das fehlte.

Eine speziellere Route `ip route add 10.10.1.0/24 via 10.10.2.1` würde diese beiden Clients auch durchlassen. Die falsche Default-Route bliebe, und jedes andere Ziel außerhalb von 10.10.2.0/24 wäre weiter tot. Einen Host auf 10.10.2.254 zu setzen würde das ARP beantworten, die Pakete müssten von dort aber immer noch zum Router. Das ist der größere Umbau, nicht der kleinere. `start_lab.py` anzufassen würde erst den nächsten Start ändern, die laufende Umgebung nicht. Die Angabe will die kleinste Änderung an der laufenden Konfiguration. Das ist das `replace`.

## 9.6 Reparatur

Dieselbe Umgebung, nicht neu gestartet. `ping -c 3 -W 2 10.10.2.10` von client1: 3 von 3, TTL 63, RTT 28,090/38,011/57,733/13,945 ms. Von client2: 3 von 3, TTL 63, RTT 28,167/28,374/28,625/0,189 ms. TTL 63, weil der Router auf dem Rückweg eine Stelle abzieht. Vorher kam gar keine Antwort, also auch keine TTL.

`tcp_server.py` wieder auf dem Server, dann `tcp_client.py` von beiden Clients. Beide haben `RN-Lab forensic test server` gedruckt, Rückgabe 0.

Zweiter Mitschnitt, [after-client1.pcap](after-client1.pcap) und [after-server.pcap](after-server.pcap). Echo Request id 42668, icmp id 4855, seq 1. Auf dem Client TTL 64 an die MAC `00:00:00:00:00:03`. Auf dem Server TTL 63, Quelle `7e:f3:ca:f0:60:c1`. Der Reply geht diesmal raus, IP-id 2115, vom Server mit TTL 64 an genau diese Router-MAC, und kommt beim Client mit TTL 63 an. Vorher endete die Spur im ARP nach 10.10.2.254. Das ARP ist in diesem Mitschnitt weg.

TCP von client1, Port 38034. SYN, SYN-ACK, ACK, dann 28 Byte Nutzlast, dann FIN. Der SYN hat IP-id 11429, TTL 64 auf client1-eth0 und TTL 63 auf server-eth0, seq 142331801. Das SYN-ACK kommt von 10.10.2.10:5000, ack 142331802. Die 28 Byte, aus dem Hexdump ab `524e2d4c`:

```
524e 2d4c 6162 2066 6f72 656e
7369 6320 7465 7374 2073 6572 7665 720a
```

Das ist `RN-Lab forensic test server` und ein Zeilenumbruch. Dieselbe Nutzlast geht auch an client2, Port 35048. Der Client hat genau diesen Text geschrieben, die Anwendung ist also angekommen.

Auch hier meckert tcpdump über die TCP-Prüfsumme (`incorrect -> ...`). Offload, kein zweiter Fehler. Der Banner wäre sonst nicht angekommen.

Vorher: SYN kommt an, ARP nach 10.10.2.254, kein SYN-ACK, Timeout. Nachher: voller Handshake, 28 Byte zurück, beide Clients. Der Unterschied ist die eine Route.
