#!/usr/bin/env python3
"""RN-Lab Assignment 07, erweitert um r3.

Ausgangstopologie der Vorlage:
    client -- r1 -- r2 -- server

Die Angabe will einen zweiten Weg zwischen r1 und dem Server, über
neue Router-zu-Router-Verbindungen. Der Satz in der Angabe bricht
dort ab. Ich lese ihn so: neue Punkt-zu-Punkt-Netze, wie die /30
zwischen r1 und r2. r3 sitzt zwischen r1 und r2. Das Server-LAN
bleibt an r2. Ein zweites Interface am Server wäre keine
Router-zu-Router-Strecke.

Neue Netze:
    10.0.13.0/30  r1-eth2 -- r3-eth0
    10.0.23.0/30  r3-eth1 -- r2-eth2

Verzögerung pro Richtung:
    client-r1 und r2-server: 10ms, das ist LINK_DELAY der Vorlage
    r1-r2: 5ms, delayA aus Ü 7.3
    r1-r3 und r3-r2: je 30ms, delayB aus Ü 7.3

Der Knoten heißt in der Vorlage client, in der Angabe client1.

KI-Kennzeichnung (Aufnahmefolien, Seite 18):
Tool: Hermes Agent. Modell: grok-4.7. Datum: 30.10.2026.
Anfrage aus Ü 7.2: topology.py um r3 und einen alternativen Weg
zwischen r1 und dem Server erweitern. Ü 7.3: delayA 5ms, delayB 30ms.
"""

from mininet.topo import Topo
from mininet.node import Host, Node
from mininet.link import TCLink

DELAY_SHARED = "10ms"
DELAY_A = "5ms"
DELAY_B = "30ms"


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
        r1 = self.addHost("r1", cls=LinuxRouter)
        r2 = self.addHost("r2", cls=LinuxRouter)
        r3 = self.addHost("r3", cls=LinuxRouter)
        server = self.addHost("server", cls=Host)

        self.addLink(
            client, r1,
            intfName1="client-eth0",
            intfName2="r1-eth0",
            cls=TCLink,
            delay=DELAY_SHARED,
        )
        self.addLink(
            r1, r2,
            intfName1="r1-eth1",
            intfName2="r2-eth0",
            cls=TCLink,
            delay=DELAY_A,
        )
        self.addLink(
            r2, server,
            intfName1="r2-eth1",
            intfName2="server-eth0",
            cls=TCLink,
            delay=DELAY_SHARED,
        )
        self.addLink(
            r1, r3,
            intfName1="r1-eth2",
            intfName2="r3-eth0",
            cls=TCLink,
            delay=DELAY_B,
        )
        self.addLink(
            r3, r2,
            intfName1="r3-eth1",
            intfName2="r2-eth2",
            cls=TCLink,
            delay=DELAY_B,
        )


topos = {"routingtopo": RoutingTopo}
