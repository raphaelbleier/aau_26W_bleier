#!/usr/bin/env python3
"""Starter für Blatt 07. Die Vorlage kennt r3 nicht, deshalb liegen die
neuen Adressen hier.

Pfad A: client -> r1 -> r2 -> server
Pfad B: client -> r1 -> r3 -> r2 -> server

Es ist immer nur eine der beiden Fernrouten eingetragen. xterm fehlt
auf diesem Rechner, die Befehle laufen in den Namespaces. Das ist
dieselbe Sicht wie ein Terminal auf dem Knoten.

Aufruf:
    sudo python3 start_lab.py          # Pfad A, dann Mininet-CLI
    sudo python3 start_lab.py B
    sudo python3 start_lab.py B --check

KI-Kennzeichnung (Aufnahmefolien, Seite 18):
Tool: Hermes Agent. Modell: grok-4.7. Datum: 30.10.2026.
Anfrage aus Ü 7.2 bis 7.4: statische Routen so setzen, dass client den
Server über genau einen Pfad erreicht, beide Varianten testen, eine
Route auf r3 löschen und wieder eintragen.
"""

import sys

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info

from topology import RoutingTopo


ADDRS = (
    ("client", "client-eth0", "10.0.1.2/24"),
    ("r1", "r1-eth0", "10.0.1.1/24"),
    ("r1", "r1-eth1", "10.0.12.1/30"),
    ("r1", "r1-eth2", "10.0.13.1/30"),
    ("r2", "r2-eth0", "10.0.12.2/30"),
    ("r2", "r2-eth1", "10.0.2.1/24"),
    ("r2", "r2-eth2", "10.0.23.2/30"),
    ("r3", "r3-eth0", "10.0.13.2/30"),
    ("r3", "r3-eth1", "10.0.23.1/30"),
    ("server", "server-eth0", "10.0.2.2/24"),
)


def configure_addrs(net):
    for name, intf, ip in ADDRS:
        node = net[name]
        node.cmd(f"ip addr flush dev {intf}")
        node.cmd(f"ip addr add {ip} dev {intf}")
        node.cmd(f"ip link set {intf} up")
    net["client"].cmd("ip route replace default via 10.0.1.1 dev client-eth0")
    net["server"].cmd("ip route replace default via 10.0.2.1 dev server-eth0")
    net["r3"].cmd("ip route replace 10.0.1.0/24 via 10.0.13.1 dev r3-eth0")
    net["r3"].cmd("ip route replace 10.0.2.0/24 via 10.0.23.2 dev r3-eth1")


def select_path(net, path):
    """Genau eine Fernroute. Die andere wird vorher gelöscht."""
    r1, r2 = net["r1"], net["r2"]
    r1.cmd("ip route del 10.0.2.0/24")
    r2.cmd("ip route del 10.0.1.0/24")
    if path == "A":
        r1.cmd("ip route replace 10.0.2.0/24 via 10.0.12.2 dev r1-eth1")
        r2.cmd("ip route replace 10.0.1.0/24 via 10.0.12.1 dev r2-eth0")
        return
    if path == "B":
        r1.cmd("ip route replace 10.0.2.0/24 via 10.0.13.2 dev r1-eth2")
        r2.cmd("ip route replace 10.0.1.0/24 via 10.0.23.1 dev r2-eth2")
        return
    raise SystemExit("Pfad muss A oder B sein")


def show_state(net):
    for name in ("client", "r1", "r2", "r3", "server"):
        node = net[name]
        info(f"\n--- {name} ---\n")
        info(node.cmd("ip -br addr"))
        info(node.cmd("ip route"))


def ping_ok(node, target):
    out = node.cmd(f"ping -c 1 -W 2 {target}")
    info(out)
    return "0% packet loss" in out


def main():
    args = [a for a in sys.argv[1:] if a]
    path = "A"
    check = False
    for arg in args:
        if arg == "--check":
            check = True
        elif arg in ("A", "B"):
            path = arg
        else:
            raise SystemExit(f"unbekanntes Argument: {arg}")

    net = Mininet(topo=RoutingTopo(), controller=None, autoSetMacs=True, link=TCLink)
    net.start()
    try:
        configure_addrs(net)
        select_path(net, path)
        info(f"\n=== Pfad {path} ===\n")
        show_state(net)
        ok = ping_ok(net["client"], "10.0.2.2")
        info(net["client"].cmd("/usr/bin/tracepath -n 10.0.2.2"))
        if not ok:
            info("Ping auf dem gewählten Pfad ist fehlgeschlagen.\n")
            return 1
        if check:
            return 0
        info("\nIn der CLI: client ping -c 3 10.0.2.2\n")
        info("Pfad wechseln geht hier nicht per Befehl. Neu starten mit Argument B.\n")
        CLI(net)
        return 0
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    raise SystemExit(main())
