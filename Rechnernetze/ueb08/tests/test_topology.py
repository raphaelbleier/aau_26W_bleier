#!/usr/bin/env python3
"""Strukturprüfung. Startet kein Mininet und ändert keine Adressen.

KI-Kennzeichnung (Aufnahmefolien, Seite 18):
Tool: Hermes Agent. Modell: grok-4.7. Datum: 30.10.2026.
Anfrage: prüfen, dass die Zwei-LAN-Topologie die genannten
Knoten und Interface-Namen enthält, ohne das Labor zu starten.
"""

import unittest

from topology_routed import TwoLanTopo


class TwoLanStructureTest(unittest.TestCase):
    def setUp(self):
        self.topo = TwoLanTopo()
        self.topo.build()

    def test_nodes(self):
        self.assertEqual(
            set(self.topo.nodes()),
            {"client1", "client2", "server1", "server2", "router", "s1", "s2"},
        )

    def test_no_hardcoded_host_ip(self):
        for name in ("client1", "client2", "server1", "server2", "router"):
            self.assertIsNone(self.topo.nodeInfo(name).get("ip"))

    def test_host_interface_names(self):
        found = {}
        for left, right, info in self.topo.links(withInfo=True):
            found[(left, right)] = info
        self.assertEqual(found[("client1", "s1")]["intfName1"], "client1-eth0")
        self.assertEqual(found[("client2", "s1")]["intfName1"], "client2-eth0")
        self.assertEqual(found[("router", "s1")]["intfName1"], "router-eth0")
        self.assertEqual(found[("server1", "s2")]["intfName1"], "server1-eth0")
        self.assertEqual(found[("server2", "s2")]["intfName1"], "server2-eth0")
        self.assertEqual(found[("router", "s2")]["intfName1"], "router-eth1")

    def test_switches_standalone(self):
        self.assertEqual(self.topo.nodeInfo("s1").get("failMode"), "standalone")
        self.assertEqual(self.topo.nodeInfo("s2").get("failMode"), "standalone")
        self.assertEqual(self.topo.nodeInfo("s1").get("dpid"), "0000000000000001")
        self.assertEqual(self.topo.nodeInfo("s2").get("dpid"), "0000000000000002")


if __name__ == "__main__":
    unittest.main()
