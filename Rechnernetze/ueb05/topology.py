#!/usr/bin/env python3
"""Assignment 05 topology.

Infrastructure only:
    client -------- router -------- server

Students may change LINK_DELAY and LINK_LOSS for experiments.
Do not change the topology structure unless explicitly requested.
"""

from mininet.topo import Topo
from mininet.node import Host, Node
from mininet.link import TCLink

# KI-Kennzeichnung: Hermes Agent, Modell gpt-6.1-sol, 17.11.2026.
# Anfrage: Parametrisiere die gegebene Blatt-05-Topologie fuer Delay und Loss.
import os

LINK_DELAY = os.environ.get("LINK_DELAY", "20ms")
LINK_LOSS = float(os.environ.get("LINK_LOSS", "0"))


class LinuxRouter(Node):
    """Mininet node that forwards IPv4 packets."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0 >/dev/null")
        super().terminate()


class TCPTopo(Topo):
    def build(self):
        client = self.addHost("client", cls=Host)
        router = self.addHost("router", cls=LinuxRouter)
        server = self.addHost("server", cls=Host)

        self.addLink(
            client, router,
            intfName1="client-eth0",
            intfName2="router-eth0",
            cls=TCLink,
            bw=10,
            delay=LINK_DELAY,
            loss=LINK_LOSS,
        )

        self.addLink(
            router, server,
            intfName1="router-eth1",
            intfName2="server-eth0",
            cls=TCLink,
            bw=10,
            delay=LINK_DELAY,
            loss=LINK_LOSS,
        )


topos = {"tcptopo": TCPTopo}
