#!/usr/bin/env python3
"""Strukturprüfung für die erweiterte Topologie. Startet kein Mininet."""

import unittest

from topology import RoutingTopo


class TopologyStructureTest(unittest.TestCase):
    def setUp(self):
        self.topo = RoutingTopo()
        self.topo.build()

    def test_nodes(self):
        names = set(self.topo.nodes())
        self.assertEqual(
            names,
            {"client", "client2", "r1", "r2", "server", "s1"},
        )

    def test_client2_address_and_route(self):
        info = self.topo.nodeInfo("client2")
        self.assertEqual(info.get("ip"), "10.0.1.3/24")
        self.assertEqual(info.get("defaultRoute"), "via 10.0.1.1")

    def test_switch_has_no_ip(self):
        info = self.topo.nodeInfo("s1")
        self.assertIsNone(info.get("ip"))

    def test_links_keep_template_interface_names(self):
        links = self.topo.links(withInfo=True)
        pairs = set()
        for left, right, info in links:
            pairs.add((left, info.get("intfName1"), right, info.get("intfName2")))
        self.assertIn(("client", "client-eth0", "s1", None), pairs)
        self.assertIn(("client2", "client2-eth0", "s1", None), pairs)
        self.assertIn(("s1", None, "r1", "r1-eth0"), pairs)
        self.assertIn(("r1", "r1-eth1", "r2", "r2-eth0"), pairs)
        self.assertIn(("r2", "r2-eth1", "server", "server-eth0"), pairs)

    def test_original_hosts_have_no_hardcoded_ip(self):
        # Adressen von client, r1, r2 und server setzt das unveränderte start_lab.py.
        for name in ("client", "r1", "r2", "server"):
            self.assertIsNone(self.topo.nodeInfo(name).get("ip"))


if __name__ == "__main__":
    unittest.main()
