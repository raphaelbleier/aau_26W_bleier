#!/usr/bin/env python3
"""Start and verify the RN-Lab environment for Assignment 05."""

import time
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.term import makeTerm

from topology import TCPTopo, LINK_DELAY, LINK_LOSS

CLIENT_IP = "10.0.1.2/24"
CLIENT_GW = "10.0.1.1"
ROUTER_LEFT_IP = "10.0.1.1/24"
ROUTER_RIGHT_IP = "10.0.2.1/24"
SERVER_IP = "10.0.2.2/24"
SERVER_GW = "10.0.2.1"


def configure_network(net):
    client = net["client"]
    router = net["router"]
    server = net["server"]

    # Explicitly configure every interface. This avoids depending on
    # implicit address configuration in addLink().
    client.cmd("ip addr flush dev client-eth0")
    router.cmd("ip addr flush dev router-eth0")
    router.cmd("ip addr flush dev router-eth1")
    server.cmd("ip addr flush dev server-eth0")

    client.cmd(f"ip addr add {CLIENT_IP} dev client-eth0")
    router.cmd(f"ip addr add {ROUTER_LEFT_IP} dev router-eth0")
    router.cmd(f"ip addr add {ROUTER_RIGHT_IP} dev router-eth1")
    server.cmd(f"ip addr add {SERVER_IP} dev server-eth0")

    for node, intf in (
        (client, "client-eth0"),
        (router, "router-eth0"),
        (router, "router-eth1"),
        (server, "server-eth0"),
    ):
        node.cmd(f"ip link set {intf} up")

    # The two end hosts need routes to the remote subnet.
    client.cmd(f"ip route replace default via {CLIENT_GW} dev client-eth0")
    server.cmd(f"ip route replace default via {SERVER_GW} dev server-eth0")

    # The router needs both directly connected networks.
    router.cmd("ip route replace 10.0.1.0/24 dev router-eth0 src 10.0.1.1")
    router.cmd("ip route replace 10.0.2.0/24 dev router-eth1 src 10.0.2.1")
    router.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null")


def verify(net):
    client = net["client"]
    router = net["router"]
    server = net["server"]

    checks = [
        ("client -> router", client, "10.0.1.1"),
        ("router -> client", router, "10.0.1.2"),
        ("router -> server", router, "10.0.2.2"),
        ("server -> router", server, "10.0.2.1"),
        ("client -> server", client, "10.0.2.2"),
        ("server -> client", server, "10.0.1.2"),
    ]

    print("\nConnectivity check:")
    failed = []
    for label, node, address in checks:
        result = node.cmd(f"ping -c 2 -W 1 {address}")
        ok = "0% packet loss" in result
        print(f"  {'OK  ' if ok else 'FAIL'} {label}")
        if not ok:
            failed.append(label)

    if failed:
        print("\nInterface state:")
        for name, node in (("client", client), ("router", router), ("server", server)):
            print(f"\n{name}:")
            print(node.cmd("ip -br addr"))
            print(node.cmd("ip route"))
        raise RuntimeError("Connectivity check failed: " + ", ".join(failed))

    print("  All connectivity checks passed.\n")


def show_state(net):
    client = net["client"]
    router = net["router"]
    server = net["server"]

    print("=" * 68)
    print("RN-Lab - Assignment 05")
    print("=" * 68)
    print("Topology: client -------- router -------- server")
    print(f"Link delay: {LINK_DELAY}")
    print(f"Link loss : {LINK_LOSS}%")
    print("\nActual interfaces:")
    print("CLIENT :", client.cmd("ip -br addr").strip())
    print("ROUTER :", router.cmd("ip -br addr").strip())
    print("SERVER :", server.cmd("ip -br addr").strip())
    print("\nActual routing tables:")
    print("CLIENT :\n" + client.cmd("ip route").strip())
    print("ROUTER :\n" + router.cmd("ip route").strip())
    print("SERVER :\n" + server.cmd("ip route").strip())
    print("=" * 68 + "\n")


def main():
    net = Mininet(topo=TCPTopo(), controller=None, autoSetMacs=True)
    info("*** Starting RN-Lab Assignment 05\n")
    net.start()

    try:
        configure_network(net)
        time.sleep(0.2)
        show_state(net)
        verify(net)

        info("*** Opening three Mininet terminals\n")
        makeTerm(net["client"], title="A05 Client")
        makeTerm(net["router"], title="A05 Router")
        makeTerm(net["server"], title="A05 Server")

        print("Three terminals are ready.")
        print("From the client: ping -c 4 10.0.2.2")
        print("From the server: ping -c 4 10.0.1.2")
        print("\nPress ENTER in this terminal to stop the experiment.")

        try:
            input()
        except KeyboardInterrupt:
            pass
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
