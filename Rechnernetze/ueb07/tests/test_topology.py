#!/usr/bin/env python3
"""Strukturprüfung. Startet kein Mininet und ändert keine Routen."""

import unittest

from topology import DELAY_A, DELAY_B, DELAY_SHARED, RoutingTopo


class TopologyStructureTest(unittest.TestCase):
    def setUp(self):
        self.topo = RoutingTopo()
        self.topo.build()

    def test_nodes(self):
        self.assertEqual(
            set(self.topo.nodes()),
            {"client", "r1", "r2", "r3", "server"},
        )

    def test_no_hardcoded_host_ip(self):
        # Adressen setzt start_lab.py, nicht die Topologie.
        for name in ("client", "r1", "r2", "r3", "server"):
            self.assertIsNone(self.topo.nodeInfo(name).get("ip"))

    def test_links_and_delays(self):
        found = {}
        for left, right, info in self.topo.links(withInfo=True):
            found[(left, right)] = info
        self.assertEqual(found[("client", "r1")]["intfName1"], "client-eth0")
        self.assertEqual(found[("client", "r1")]["intfName2"], "r1-eth0")
        self.assertEqual(found[("client", "r1")]["delay"], DELAY_SHARED)
        self.assertEqual(found[("r1", "r2")]["intfName1"], "r1-eth1")
        self.assertEqual(found[("r1", "r2")]["intfName2"], "r2-eth0")
        self.assertEqual(found[("r1", "r2")]["delay"], DELAY_A)
        self.assertEqual(found[("r2", "server")]["intfName1"], "r2-eth1")
        self.assertEqual(found[("r2", "server")]["intfName2"], "server-eth0")
        self.assertEqual(found[("r2", "server")]["delay"], DELAY_SHARED)
        self.assertEqual(found[("r1", "r3")]["intfName1"], "r1-eth2")
        self.assertEqual(found[("r1", "r3")]["intfName2"], "r3-eth0")
        self.assertEqual(found[("r1", "r3")]["delay"], DELAY_B)
        self.assertEqual(found[("r3", "r2")]["intfName1"], "r3-eth1")
        self.assertEqual(found[("r3", "r2")]["intfName2"], "r2-eth2")
        self.assertEqual(found[("r3", "r2")]["delay"], DELAY_B)

    def test_delay_values_from_sheet(self):
        self.assertEqual(DELAY_A, "5ms")
        self.assertEqual(DELAY_B, "30ms")
        self.assertEqual(DELAY_SHARED, "10ms")


if __name__ == "__main__":
    unittest.main()
