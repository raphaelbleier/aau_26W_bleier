#!/usr/bin/env python3
"""RN-Lab Assignment 06, erweitert um den zweiten Client aus Ü 6.7.

Ausgangstopologie der Vorlage:
    client -- r1 -- r2 -- server

Ab Ü 6.7 hängt client2 am selben linken Netz. Eine zweite direkte
Leitung an r1 würde kein gemeinsames LAN ergeben, weil 10.0.1.1/24
schon an r1-eth0 liegt. Die Bridge s1 verbindet client, client2 und
r1 auf Schicht 2. start_lab.py bleibt unverändert: es setzt die
bekannten Interfaces und die Route 10.0.1.0/24 auf r2 deckt beide
Clients ab.

KI-Kennzeichnung (Aufnahmefolien, Seite 18):
Tool: Hermes Agent. Modell: grok-4.7. Datum: 30.10.2026.
Anfrage aus der Angabe, Ü 6.7: weiteren Client anlegen, passende
IP-Adresse vergeben, mit r1 verbinden, Default-Route setzen,
Verbindung zum Server testen. tcp_client.py und tcp_server.py
nicht verändern.
"""

from mininet.topo import Topo
from mininet.node import Host, Node, OVSBridge
from mininet.link import TCLink

LINK_DELAY = "10ms"


class LinuxRouter(Node):
    """Mininet-Knoten mit eingeschaltetem IPv4-Forwarding."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0 >/dev/null")
        super().terminate()


class RoutingTopo(Topo):
    def build(self):
        client = self.addHost("client", cls=Host)
        # 10.0.1.3 ist frei in 10.0.1.0/24: nicht Netz, nicht Broadcast, nicht r1.
        # Ohne Default-Route kennt client2 das Servernetz 10.0.2.0/24 nicht.
        client2 = self.addHost(
            "client2",
            cls=Host,
            ip="10.0.1.3/24",
            defaultRoute="via 10.0.1.1",
        )
        r1 = self.addHost("r1", cls=LinuxRouter)
        r2 = self.addHost("r2", cls=LinuxRouter)
        server = self.addHost("server", cls=Host)
        # Lernende Bridge, kein OpenFlow-Controller. Keine eigene IP, kein IP-Hop.
        left = self.addSwitch("s1", cls=OVSBridge, failMode="standalone")

        self.addLink(
            client, left,
            intfName1="client-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
        )
        self.addLink(
            client2, left,
            intfName1="client2-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
        )
        self.addLink(
            left, r1,
            intfName2="r1-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
        )
        self.addLink(
            r1, r2,
            intfName1="r1-eth1",
            intfName2="r2-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
        )
        self.addLink(
            r2, server,
            intfName1="r2-eth1",
            intfName2="server-eth0",
            cls=TCLink,
            delay=LINK_DELAY,
        )


topos = {"routingtopo": RoutingTopo}
