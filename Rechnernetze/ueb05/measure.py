# KI-Kennzeichnung: Hermes Agent, Modell gpt-6.1-sol, 17.11.2026.
# Anfrage: Miss Blatt 05 wirklich in Mininet: Handshake, Byte-Stream,
# Sequenznummern, 0/5/10 Prozent Verlust, 0/10/20/50 ms, TCP und UDP
# bei 10 und 50 Mbit/s. Speichere iperf3-JSON, PCAP und Empfangsprotokolle.
"""Mit sudo /usr/bin/python3 measure.py --output messungen starten."""
import argparse
import json
import os
from pathlib import Path
import signal
import shutil
import threading
import subprocess
import time

from mininet.net import Mininet
from mininet.log import setLogLevel
import topology
from start_lab import configure_network

ROOT = Path(__file__).resolve().parent


def stop(proc):
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    if hasattr(proc, "capture_thread"):
        proc.capture_thread.join(timeout=10)
        if proc.capture_thread.is_alive():
            raise RuntimeError("Capture-Pipe nicht geschlossen")
        if not getattr(proc, "capture_saved", False):
            proc.capture_path.with_suffix(".capture.log").write_bytes(proc.stderr.read())
            proc.capture_saved = True


def capture(node, path, port):
    # Pipe entkoppelt tcpdump von Dateirechten und Puffern des Zielpfads.
    proc = node.popen(["tcpdump", "--immediate-mode", "-U", "-Z", "root", "-i", "client-eth0", "-w", "-", f"tcp port {port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    def drain():
        with path.open("wb") as target:
            shutil.copyfileobj(proc.stdout, target)
    proc.capture_path = path
    proc.capture_thread = threading.Thread(target=drain)
    proc.capture_thread.start()
    return proc


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("messungen"))
    p.add_argument("--capture-only", action="store_true", help="Nur TCP bei 20 ms samt Mitschnitten erneuern")
    args = p.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    records = json.loads((out / "results.json").read_text()) if args.capture_only else []
    setLogLevel("error")
    for delay in ((20,) if args.capture_only else (0, 10, 20, 50)):
        for loss in (0, 5, 10):
            topology.LINK_DELAY = f"{delay}ms"
            topology.LINK_LOSS = loss
            net = Mininet(topo=topology.TCPTopo(), controller=None, autoSetMacs=True)
            procs = []
            try:
                net.start()
                configure_network(net)
                c, s = net["client"], net["server"]
                for node in net.hosts:
                    for intf in node.intfList():
                        node.cmd(f"ethtool -K {intf} tso off gso off gro off 2>/dev/null")
                # Erst ARP aufbauen, damit die kurzen Tests nicht davon abhängen.
                c.cmd("ping -c 2 -W 2 10.0.2.2")
                protocols = [("tcp", None)]
                if delay == 20 and not args.capture_only:
                    protocols += [("udp", "10M"), ("udp", "50M")]
                for protocol, rate in protocols:
                    name = f"{protocol}-d{delay}-p{loss}" + (f"-{rate}" if rate else "")
                    cap = None
                    if protocol == "tcp" and delay == 20:
                        cap = capture(c, out / (name + ".pcap"), 5201)
                        procs.append(cap)
                        time.sleep(0.3)
                    cmd = ["iperf3", "-c", "10.0.2.2", "-t", "6", "-J"]
                    if rate:
                        cmd += ["-u", "-b", rate, "-l", "1200"]
                    else:
                        cmd += ["-l", "4096"]
                    for attempt in range(3):
                        iperf = s.popen(["iperf3", "-s", "-1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        procs.append(iperf)
                        time.sleep(0.3)
                        r = c.popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        procs.append(r)
                        try:
                            stdout, stderr = r.communicate(timeout=45)
                            data = json.loads(stdout)
                            valid = r.returncode == 0 and "error" not in data
                        except (subprocess.TimeoutExpired, ValueError):
                            valid = False
                        stop(r)
                        stop(iperf)
                        if valid:
                            break
                        print(f"Retry {name}: Versuch {attempt + 1}", flush=True)
                    else:
                        raise RuntimeError(f"Messung fehlgeschlagen: {name}")
                    # iperf-interne Cookies und Hostnamen gehören nicht zur Messung.
                    data["start"].pop("cookie", None)
                    data["start"].pop("system_info", None)
                    (out / (name + ".json")).write_text(json.dumps(data, indent=2))
                    if cap:
                        time.sleep(0.4)
                        stop(cap)
                    end = data["end"]
                    item = {"name": name, "protocol": protocol, "delay_ms_per_link": delay, "loss_pct_per_link": loss, "offered_mbps": int(rate[:-1]) if rate else None}
                    if protocol == "tcp":
                        item.update(mbps=end["sum_received"]["bits_per_second"] / 1e6, retransmits=end["sum_sent"]["retransmits"])
                    else:
                        received = end.get("sum_received", end.get("sum"))
                        item.update(mbps=received["bits_per_second"] / 1e6, reported_lost_percent=received["lost_percent"], lost_percent=100 * received["lost_packets"] / received["packets"] if received["packets"] else 0, lost_packets=received["lost_packets"], packets=received["packets"])
                    records = [old for old in records if old["name"] != name]
                    records.append(item)
                    print(json.dumps(item), flush=True)
                if delay == 20 and loss == 0:
                    # Ein kompletter, eigener TCP-Flow für 5.1, 5.3 und 5.7.
                    cap = capture(c, out / "handshake.pcap", 5000)
                    procs.append(cap)
                    with (out / "framed-server.log").open("w") as log:
                        server = s.popen(["/usr/bin/python3", str(ROOT / "tcp_server.py"), "--once", "--recv-size", "1024"], stdout=log, stderr=log)
                        procs.append(server)
                        time.sleep(0.4)
                        result = c.cmd(f"/usr/bin/python3 {ROOT / 'tcp_client.py'} --large 256")
                        if "OK" not in result:
                            raise RuntimeError(result)
                        (out / "framed-client.log").write_text(result.replace("\r\n", "\n"))
                        server.wait(timeout=30)
                        if server.returncode:
                            raise RuntimeError("Server fehlgeschlagen")
                    time.sleep(0.4)
                    stop(cap)
                    # Beobachtete recv-Grenzen, nicht nur ein simulierter Socket.
                    for size in (1, 8, 1024):
                        with (out / f"raw-recv-{size}.log").open("w") as log:
                            server = s.popen(["/usr/bin/python3", str(ROOT / "tcp_server.py"), "--once", "--mode", "raw", "--recv-size", str(size)], stdout=log, stderr=log)
                            procs.append(server)
                            time.sleep(0.2)
                            result = c.cmd(f"/usr/bin/python3 {ROOT / 'tcp_client.py'} --mode raw")
                            if "OK" not in result:
                                raise RuntimeError(result)
                            server.wait(timeout=15)
                            if server.returncode:
                                raise RuntimeError("Raw-Server fehlgeschlagen")
            finally:
                for proc in reversed(procs):
                    stop(proc)
                net.stop()
            (out / "results.json").write_text(json.dumps(records, indent=2))
    (out / "environment.json").write_text(json.dumps({"kernel": os.uname().release, "iperf3": subprocess.check_output(["iperf3", "--version"], text=True).splitlines()[0], "seconds_per_run": 6, "repetitions": 1, "bandwidth_mbps_per_link": 10, "capture_interface": "client-eth0", "offload": "TSO/GSO/GRO disabled", "date": "2026-11-17"}, indent=2))


if __name__ == "__main__":
    main()
