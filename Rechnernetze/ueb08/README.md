# Rechnernetze: Übungsblatt 08

[KI-Kennzeichnung](KI_NUTZUNG.md). Gruppe 1 (Raphael Bleier, Devis, Fabio). Welche der beiden Moodle-Abgaben das ist, habe ich nicht geprüft. Beide nennen Dienstag, 19.01.2027, 08:00. Nichts wurde hochgeladen.

Gemessen am 30.10.2026 mit Mininet 2.3.0 und Python 3.13.3. `xterm` fehlt, also liefen `ip`, `ping` und `tcpdump` in den Namespaces, und das ist dieselbe Sicht wie in einem Terminal auf dem Host. Ein Wireshark-Fenster gab es nicht. `tshark` durfte die PCAP-Dateien hier nicht lesen, `tcpdump -r` schon, und die zitierten Header kommen daher.

Die Vorlage (`topology.py`, `start_lab.py`, `start_lab_monitor.py`) habe ich nicht verändert und nicht mit ins Repo gelegt. Ü 8.4 steht in [topology_routed.py](topology_routed.py). Die Angabe zeichnet nur `LAN A ---- router ---- LAN B` und nennt keine Adressen, deshalb bleibt LAN A bei 10.0.1.0/24 und die Clients behalten .2 und .3. LAN B ist 10.0.2.0/24, die Server behalten die Hostnummern .10 und .11, und der Router hat 10.0.1.1 und 10.0.2.1.

## Vorlage, ein Subnetz

`autoSetMacs` hat die MACs vergeben, ich habe sie dort nicht gesetzt. `ip link` zeigte:

- client1-eth0: 10.0.1.2/24, MAC `00:00:00:00:00:01`
- client2-eth0: 10.0.1.3/24, MAC `00:00:00:00:00:02`
- server1-eth0: 10.0.1.10/24, MAC `00:00:00:00:00:03`
- server2-eth0: 10.0.1.11/24, MAC `00:00:00:00:00:04`

Die Endungen passen zu dem, was die Angabe für Ü 8.3 hinschreibt. Jeder Host hat nur die verbundene Route `10.0.1.0/24`, keine Default-Route. `ovs-vsctl get-fail-mode s1` lieferte `standalone`. `ovs-ofctl show s1` nennt Port 1 als s1-eth1, Port 2 als s1-eth2, Port 3 als s1-eth3, Port 4 als s1-eth4. Die Vorlage hängt die Hosts in der Reihenfolge client1, client2, server1, server2 an. Die FDB weiter unten bestätigt diese Zuordnung.

## 8.1 Echo Request

server1 hat `ping -c 4 -W 2 10.0.1.2` geschickt. 4 gesendet, 4 empfangen, 0% Verlust. TTL 64. RTT min/avg/max/mdev = 0,031/0,106/0,316/0,121 ms. Der erste war 0,316 ms, die späteren lagen bei 0,039 und 0,031 ms. Der erste enthält die ARP-Auflösung, die späteren nicht.

Mitschnitt auf client1-eth0, Datei [echo-request.pcap](echo-request.pcap). Ein Echo Request daraus:

```
00:00:00:00:00:03 > 00:00:00:00:00:01, ethertype IPv4 (0x0800), length 98:
(tos 0x0, ttl 64, id 50192, offset 0, flags [DF], proto ICMP (1), length 84)
10.0.1.10 > 10.0.1.2: ICMP echo request, id 61245, seq 1, length 64
```

Im Hexdump stehen die ersten Bytes `0000 0000 0001 0000 0000 0003 0800`. Ziel-MAC, Quell-MAC, dann EtherType 0x0800. Danach `4500`, also IPv4 mit 20 Byte Header, und `40` als TTL.

Source MAC ist server1, Destination MAC ist client1, Source IP 10.0.1.10, Destination IP 10.0.1.2, EtherType 0x0800.

Die MAC-Adresse gilt nur für diesen Ethernet-Hop, und der Switch stellt anhand der Ziel-MAC zu, nicht anhand der IP. Die IP benennt die Endpunkte, hier server1 und client1. Die beiden liegen im selben Subnetz, deshalb ist die Ziel-MAC direkt die des Empfängers und nicht die eines Routers. TTL 64 passt dazu, weil niemand sie gesenkt hat.

## 8.2 ARP

Auf der Vorlage habe ich auf client1 `ip neigh flush all` ausgeführt. Die Tabelle war danach leer. Der erste `ping -c 1 -W 2 10.0.1.3` brauchte 0,434 ms, der zweite 0,023 ms. Nach dem ersten stand da:

```
10.0.1.3 dev client1-eth0 lladdr 00:00:00:00:00:02 REACHABLE
```

Nach dem zweiten derselbe Eintrag, weiter REACHABLE.

Der eigene Mitschnitt genau dieses Laufs auf der Vorlage blieb bei 24 Byte, also nur der PCAP-Kopf. Die ARP-Zeilen zitiere ich deshalb aus [lan-ping.pcap](lan-ping.pcap). Das ist client1-eth0, gleiche Adressen, gleiches Subnetz, aufgenommen beim Ping auf 10.0.1.3:

```
00:00:00:00:00:01 > ff:ff:ff:ff:ff:ff, ethertype ARP (0x0806):
Request who-has 10.0.1.3 tell 10.0.1.2
00:00:00:00:00:02 > 00:00:00:00:00:01, ethertype ARP (0x0806):
Reply 10.0.1.3 is-at 00:00:00:00:00:02
```

Gesucht wird 10.0.1.3, und zurück kommt `00:00:00:00:00:02`, die MAC von client2. Der Request geht an die Broadcast-MAC, weil der Sender die Ziel-MAC noch nicht kennt.

ARP braucht es vor der IP-Nutzlast, weil der Ethernet-Frame eine Ziel-MAC verlangt und die IP-Adresse allein der Netzwerkkarte nicht sagt, welches Frame wohin soll. Ohne den Reply wüsste client1 nicht, wohin das Echo soll.

Beim zweiten Ping ist der Eintrag schon da. In dem Mitschnitt liegt zwischen Echo seq 1 und seq 2 kein neuer ARP-Request, die RTT fällt von etwa 0,4 ms auf 0,023 ms, und der zweite Ping löst 10.0.1.3 nicht noch einmal auf.

## 8.3 Switch Learning

Die Angabe schreibt `ocs-appctl`. Das ist in der Vorlage `ovs-appctl fdb/show s1`, und genau den Befehl habe ich benutzt. `start_lab_monitor.py` würde dafür ein xterm mit `watch` öffnen, xterm fehlt aber, also habe ich die Tabelle an den drei Stellen selbst gelesen.

Vorher `ovs-appctl fdb/flush s1`, Antwort `table successfully flushed`. Danach nur die Kopfzeile, keine Einträge. Das ist der Start.

`ping -c 1` von client1 nach 10.0.1.10, also server1. Danach:

```
 port  VLAN  MAC                Age
    1     0  00:00:00:00:00:01    0
    3     0  00:00:00:00:00:03    0
```

Port 1 ist s1-eth1, dort hängt client1, und Port 3 ist s1-eth3, dort hängt server1. Der Switch hat die Quell-MAC des ankommenden Frames mit dem Eingangsport gespeichert: der Request von client1 lehrt Port 1, die Antwort von server1 lehrt Port 3.

Dann `ping -c 1` von client2 nach derselben Adresse. Zusätzlich:

```
    2     0  00:00:00:00:00:02    0
```

Port 2 ist s1-eth2, also client2, und server1 bleibt auf Port 3. Der Switch muss die MAC von server1 nicht neu lernen, der Eintrag ist noch da. Ein späterer Rahmen an `00:00:00:00:00:03` geht nur auf Port 3, nicht mehr an alle Ports. Am Start war die Tabelle leer, nach Ping 1 kannte er zwei Stationen, nach Ping 2 drei.

## 8.4 Zwei LANs

Die MACs der Hosts habe ich hier auf dieselben Werte gesetzt, die `autoSetMacs` in der Vorlage vergeben hat, sonst wären die beiden Läufe schlecht zu vergleichen. router-eth0 hat `00:00:00:00:00:0a` und router-eth1 hat `00:00:00:00:00:0b`. Die habe ich selbst gesetzt. Die kommen nicht aus `autoSetMacs`.

`sysctl net.ipv4.ip_forward` war auf dem Router 1 und auf den Hosts 0. `ip route get 10.0.1.3` auf client1 lieferte `dev client1-eth0`, ohne `via`, und `ip route get 10.0.2.10` lieferte `via 10.0.1.1 dev client1-eth0`. Das lokale Ziel bleibt im LAN, das fremde geht an den Router.

Ping innerhalb des LAN, client1 nach 10.0.1.3: 3 von 3, TTL 64, RTT min/avg/max/mdev = 0,030/0,155/0,402 ms. Der erste ist wieder der mit ARP. Im Mitschnitt [lan-ping.pcap](lan-ping.pcap) steht der Echo Request so:

```
00:00:00:00:00:01 > 00:00:00:00:00:02, ethertype IPv4 (0x0800), ttl 64
10.0.1.2 > 10.0.1.3: ICMP echo request
```

Beide MACs gehören den Hosts, und im Frame steckt kein Router.

Ping über den Router, client1 nach 10.0.2.10: 3 von 3, TTL 63, RTT 0,036/0,264/0,716 ms. TTL 63, nicht 64, weil ein Router sie um eins gesenkt hat.

Derselbe Echo Request, id 14648, auf beiden Seiten. Vor dem Router, [wan-client.pcap](wan-client.pcap), auf client1-eth0:

```
00:00:00:00:00:01 > 00:00:00:00:00:0a, ethertype IPv4 (0x0800), ttl 64, id 14648
10.0.1.2 > 10.0.2.10: ICMP echo request, id 62229, seq 1
```

Nach dem Router, [wan-server.pcap](wan-server.pcap), auf server1-eth0:

```
00:00:00:00:00:0b > 00:00:00:00:00:03, ethertype IPv4 (0x0800), ttl 63, id 14648
10.0.1.2 > 10.0.2.10: ICMP echo request, id 62229, seq 1
```

Die IP-Adressen bleiben, die id 14648 bleibt, die MACs nicht. Vor dem Router ist die Quelle client1 und das Ziel der Router auf LAN A. Dahinter ist die Quelle der Router auf LAN B und das Ziel server1.

ARP auf der Client-Seite fragt nicht nach 10.0.2.10. Der Request lautet `who-has 10.0.1.1 tell 10.0.1.2`, die Antwort `10.0.1.1 is-at 00:00:00:00:00:0a`. Auf der Server-Seite fragt der Router selbst `who-has 10.0.2.10 tell 10.0.2.1`, und die Antwort ist `is-at 00:00:00:00:00:03`. Danach hatte client1 in `ip neigh` den Eintrag 10.0.1.1, nicht 10.0.2.10, und der Router hatte 10.0.2.10 an router-eth1.

ARP gilt dem Next Hop, weil 10.0.2.10 nicht in 10.0.1.0/24 liegt und der Client deshalb an sein Gateway schickt. Die MAC von server1 steht nicht im Frame auf client1-eth0, weil Ethernet nur bis zum nächsten Hop reicht. client1 hat keine Schicht-2-Verbindung zu server1, der liegt hinter dem anderen Interface des Routers.

## 8.5 Schichten

Ping hat Link und Network, aber keine Transport- und keine Anwendungsschicht. Deshalb ein kurzes TCP von client1 nach server1:9000, Nutzlast `hello-ueb08` plus Zeilenumbruch, 12 Byte. Der Server hat genau diese 12 Byte geschrieben und `ack-ueb08` zurückgeschickt, die Anwendung ist also angekommen.

Der Datenrahmen auf client1-eth0, Datei [tcp-client.pcap](tcp-client.pcap):

```
00:00:00:00:00:01 > 00:00:00:00:00:0a, ethertype IPv4 (0x0800), length 78:
(tos 0x0, ttl 64, id 57965, offset 0, flags [DF], proto TCP (6), length 64)
10.0.1.2.32998 > 10.0.2.10.9000: Flags [P.], seq 1919849476:1919849488, length 12
```

Im Hexdump ab `68656c6c` steht `hello-ueb08` und `0a`.

- Link: Quell-MAC `00:00:00:00:00:01`, Ziel-MAC `00:00:00:00:00:0a`, EtherType 0x0800
- Network: 10.0.1.2 nach 10.0.2.10, TTL 64, Protokoll 6, id 57965
- Transport: TCP, Quellport 32998, Zielport 9000, 12 Byte, Flags PSH und ACK
- Application: die 12 Byte `hello-ueb08\n`

`tcpdump` meckert über die TCP-Prüfsumme (`incorrect -> 0x188f`). Das ist Checksum-Offload an der virtuellen Schnittstelle, derselbe Effekt wie beim UDP-Mitschnitt von Blatt 4, und der Server hat die Nutzlast trotzdem angenommen.

Der Mitschnitt desselben TCP auf server1-eth0 blieb bei 24 Byte, die Header hinter dem Router zitiere ich dafür nicht. Was ein Hop verändert, zeigt der Echo Request von Ü 8.4 mit id 14648 auf beiden Seiten: MAC-Adressen neu, TTL von 64 auf 63, IP-Adressen und IP-id gleich. Ende-zu-Ende bleiben die IP-Adressen und die Nutzlast. Der Server hat `hello-ueb08` geschrieben, also sind die 12 Byte angekommen. Ports und Sequenznummer habe ich nur auf der Client-Seite im Mitschnitt. Die zitiere ich dort und nicht als zweite Messung.

## Starten

Strukturtest, ohne root und ohne ein laufendes Mininet:

```bash
python3 -m unittest discover -s tests -v
```

Am 30.10.2026 waren die Tests mit `/usr/bin/python3` grün. Das ist Python 3.13.3, dort liegt das Paket `mininet`. Ein venv ohne das Paket kann die Topologie nicht importieren.

Die Adressen setzt die Vorlage in `start_lab.py`, meine Erweiterung setzt sie nicht selbst, und im Lauf standen sie so, wie oben aufgeschrieben. Nichts davon wurde auf Moodle hochgeladen.
