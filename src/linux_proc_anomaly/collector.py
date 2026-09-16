"""Native /proc metrics collector for constrained-Linux anomaly detection.

Reproduces the collection methodology described in:
  Anne, A.T. (2026). "Metriques systeme natives pour la detection
  d'anomalies sous Linux embarque." HAL preprint hal-05486729v1.
  https://hal.science/hal-05486729v1

Reads /proc/stat, /proc/meminfo and /proc/net/dev at a fixed sampling
interval and measures its own CPU cost, so the paper's overhead claim
(<0.5% CPU) can be checked on any given host rather than assumed.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

PROC_STAT = "/proc/stat"
PROC_MEMINFO = "/proc/meminfo"
PROC_NET_DEV = "/proc/net/dev"

FIELDNAMES = [
    "timestamp",
    "cpu_user", "cpu_nice", "cpu_system", "cpu_idle",
    "cpu_iowait", "cpu_irq", "cpu_softirq",
    "mem_total_kb", "mem_free_kb", "mem_available_kb",
    "net_rx_bytes", "net_tx_bytes",
    "collector_cpu_time_s",
]


def read_cpu_times(proc_stat: str = PROC_STAT) -> dict:
    with open(proc_stat, "r") as f:
        line = f.readline()
    parts = line.split()
    # cpu user nice system idle iowait irq softirq ...
    values = list(map(int, parts[1:8]))
    keys = ["cpu_user", "cpu_nice", "cpu_system", "cpu_idle", "cpu_iowait", "cpu_irq", "cpu_softirq"]
    return dict(zip(keys, values))


def read_meminfo(proc_meminfo: str = PROC_MEMINFO) -> dict:
    wanted = {"MemTotal": "mem_total_kb", "MemFree": "mem_free_kb", "MemAvailable": "mem_available_kb"}
    out = {}
    with open(proc_meminfo, "r") as f:
        for line in f:
            key, _, rest = line.partition(":")
            if key in wanted:
                out[wanted[key]] = int(rest.strip().split()[0])
    return out


def read_net_dev(iface: str | None = None, proc_net_dev: str = PROC_NET_DEV) -> dict:
    rx_total = 0
    tx_total = 0
    with open(proc_net_dev, "r") as f:
        lines = f.readlines()[2:]  # skip 2 header lines
    for line in lines:
        name, _, rest = line.partition(":")
        name = name.strip()
        if iface is not None and name != iface:
            continue
        if name == "lo" and iface is None:
            continue
        fields = rest.split()
        rx_total += int(fields[0])
        tx_total += int(fields[8])
    return {"net_rx_bytes": rx_total, "net_tx_bytes": tx_total}


def sample_once() -> dict:
    """Take one sample of CPU/memory/network /proc counters.

    Returns a flat dict matching FIELDNAMES, including collector_cpu_time_s:
    the CPU time this call itself consumed, used to measure the collector's
    own overhead.
    """
    t0 = time.process_time()
    row = {"timestamp": time.time()}
    row.update(read_cpu_times())
    row.update(read_meminfo())
    row.update(read_net_dev())
    row["collector_cpu_time_s"] = time.process_time() - t0
    return row


@dataclass
class RunResult:
    rows: list[dict] = field(default_factory=list)
    wall_elapsed_s: float = 0.0
    proc_elapsed_s: float = 0.0

    @property
    def overhead_pct(self) -> float:
        """Collector CPU time as a percentage of wall-clock time."""
        if self.wall_elapsed_s <= 0:
            return float("nan")
        return (self.proc_elapsed_s / self.wall_elapsed_s) * 100


def collect(duration_s: float, interval_s: float) -> RunResult:
    """Sample /proc metrics for duration_s, every interval_s seconds.

    Returns a RunResult with the collected rows and measured overhead,
    so callers can feed rows straight into their own anomaly-detection
    pipeline without going through a file on disk.
    """
    # round(), not int(): float division (e.g. 0.6 / 0.2 == 2.9999999999999996)
    # would otherwise silently truncate to one fewer sample than requested.
    n_samples = max(1, round(duration_s / interval_s))
    rows = []
    wall_start = time.time()
    proc_start = time.process_time()

    for _ in range(n_samples):
        rows.append(sample_once())
        time.sleep(interval_s)

    wall_elapsed = time.time() - wall_start
    proc_elapsed = time.process_time() - proc_start
    return RunResult(rows=rows, wall_elapsed_s=wall_elapsed, proc_elapsed_s=proc_elapsed)
