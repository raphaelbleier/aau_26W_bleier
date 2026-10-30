#!/usr/bin/env python3
"""Zwei Ethernet-LANs mit einem Router dazwischen, für Ü 8.4.

Die Vorlage hat ein einziges Subnetz. Die Angabe sagt nur
"LAN A ---- router ---- LAN B" und nennt keine Adressen.
LAN A bleibt 10.0.1.0/24, die Clients behalten 10.0.1.2 und
10.0.1.3. LAN B ist 10.0.2.0/24, die Server behalten die
Hostnummern .10 und .11. Der Router hat 10.0.1.1 und 10.0.2.1.
Gesetzt werden die Adressen erst beim Start, nicht hier.

KI-Kennzeichnung (Aufnahmefolien, Seite 18):
Tool: Hermes Agent. Modell: grok-4.7. Datum: 30.10.2026.
Anfrage: die ÜB8-Vorlage um einen Router zwischen zwei
Ethernet-LANs erweitern, für den Vergleich in Ü 8.4.
"""

from mininet.topo import Topo
from mininet.node import Node, OVSSwitch
from mininet.link import TCLink


class LinuxRouter(Node):
    """Knoten, der Pakete weiterleitet, deren Ziel er nicht selbst ist."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0 >/dev/null")
        super().terminate()


class TwoLanTopo(Topo):
    def build(self):
        client1 = self.addHost("client1")
        client2 = self.addHost("client2")
        server1 = self.addHost("server1")
        server2 = self.addHost("server2")
        router = self.addHost("router", cls=LinuxRouter)

        s1 = self.addSwitch("s1", cls=OVSSwitch, failMode="standalone", dpid="0000000000000001")
        s2 = self.addSwitch("s2", cls=OVSSwitch, failMode="standalone", dpid="0000000000000002")

        self.addLink(client1, s1, intfName1="client1-eth0", cls=TCLink)
        self.addLink(client2, s1, intfName1="client2-eth0", cls=TCLink)
        self.addLink(
            router, s1,
            intfName1="router-eth0",
            cls=TCLink,
        )
        self.addLink(server1, s2, intfName1="server1-eth0", cls=TCLink)
        self.addLink(server2, s2, intfName1="server2-eth0", cls=TCLink)
        self.addLink(
            router, s2,
            intfName1="router-eth1",
            cls=TCLink,
        )


topos = {"twolan": TwoLanTopo}
