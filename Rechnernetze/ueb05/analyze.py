# KI-Kennzeichnung: Hermes Agent, Modell gpt-6.1-sol, 17.11.2026.
# Anfrage: Werte echte PCAPs fuer Blatt 05 mit tshark aus. Exportiere
# Paketfelder, fuenf Segmente und ACKs sowie Verlustindikatoren ohne Payload.
import argparse
import csv
import io
import json
from pathlib import Path
import subprocess

FIELDS = ["frame.number", "frame.time_relative", "ip.src", "tcp.srcport", "tcp.dstport", "tcp.stream", "tcp.flags", "tcp.seq", "tcp.seq_raw", "tcp.ack", "tcp.ack_raw", "tcp.len", "tcp.window_size_value", "tcp.window_size", "tcp.options.wscale.shift", "tcp.analysis.retransmission", "tcp.analysis.fast_retransmission", "tcp.analysis.duplicate_ack", "tcp.analysis.out_of_order"]


def packets(path):
    args = ["tshark", "-r", "-", "-Y", "tcp", "-T", "fields", "-E", "header=y", "-E", "separator=\t"]
    for field in FIELDS:
        args += ["-e", field]
    result = subprocess.run(args, input=path.read_bytes(), capture_output=True, check=True)
    return list(csv.DictReader(io.StringIO(result.stdout.decode()), delimiter="\t"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("directory", type=Path, nargs="?", default=Path("messungen"))
    args = p.parse_args()
    root = args.directory
    all_packets = {}
    for name in ("handshake", "tcp-d20-p0", "tcp-d20-p5", "tcp-d20-p10"):
        rows = packets(root / (name + ".pcap"))
        all_packets[name] = rows
        with (root / (name + "-packets.tsv")).open("w") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t", quoting=csv.QUOTE_ALL, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    rows = all_packets["handshake"]
    segments = []
    for row in rows:
        if row["ip.src"] == "10.0.1.2" and int(row["tcp.len"]) >= 1000:
            end = int(row["tcp.seq"]) + int(row["tcp.len"])
            ack = next((r for r in rows if int(r["frame.number"]) > int(row["frame.number"]) and r["ip.src"] == "10.0.2.2" and int(r["tcp.ack"]) >= end), None)
            if ack:
                segments.append({"frame": int(row["frame.number"]), "seq": int(row["tcp.seq"]), "length": int(row["tcp.len"]), "end": end, "ack_frame": int(ack["frame.number"]), "ack": int(ack["tcp.ack"])})
            if len(segments) == 5:
                break
    assert len(segments) == 5
    counts = {}
    for name, rows in all_packets.items():
        counts[name] = {field: sum(bool(r[field]) for r in rows) for field in FIELDS[-4:]}
    (root / "tcp_summary.json").write_text(json.dumps({"segments": segments, "events": counts}, indent=2))
    print(json.dumps({"segments": segments, "events": counts}, indent=2))


if __name__ == "__main__":
    main()
