# linux-proc-anomaly

[![CI](https://github.com/AmadouAnne/linux-proc-anomaly/actions/workflows/ci.yml/badge.svg)](https://github.com/AmadouAnne/linux-proc-anomaly/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/linux-proc-anomaly.svg)](https://pypi.org/project/linux-proc-anomaly/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![HAL](https://img.shields.io/badge/HAL-hal--05486729v1-blue)](https://hal.science/hal-05486729v1)

A tiny, dependency-free collector for native Linux `/proc` counters (CPU, memory, network), built for anomaly detection on constrained and embedded systems where you can't afford dedicated instrumentation agents.

It reproduces the collection methodology from the preprint **"Métriques système natives pour la détection d'anomalies sous Linux embarqué"** ([hal.science/hal-05486729v1](https://hal.science/hal-05486729v1)): correlating `/proc/stat`, `/proc/meminfo` and `/proc/net/dev` can surface anomalies (CPU spikes, memory leaks, network exfiltration, fork bombs) at a measured overhead of well under 0.5% of wall-clock CPU time — because the collector times itself, on every run, on your own hardware.

## Why this exists

Most anomaly-detection tooling for embedded/IoT Linux assumes you can install a monitoring agent with its own dependency tree. On constrained targets that's often not true. This package reads only stdlib-available `/proc` files, has zero runtime dependencies, and measures its own CPU cost every time it runs — so the overhead claim is something you check on your target, not something you take on faith.

## Install

```bash
pip install linux-proc-anomaly
```

## Usage

As a library:

```python
from linux_proc_anomaly import collect

result = collect(duration_s=10.0, interval_s=0.5)
print(f"{len(result.rows)} samples, overhead: {result.overhead_pct:.4f}%")
for row in result.rows:
    ...  # feed into your own anomaly-detection pipeline
```

As a CLI:

```bash
proc-anomaly-collect --duration 15 --interval 0.5 --out run.csv
```

## Feeding it into an anomaly detector

The package itself only collects and self-measures — it deliberately has zero runtime dependencies. [`examples/isolation_forest_demo.py`](examples/isolation_forest_demo.py) shows the minimal path from `collect()` output to an unsupervised Isolation Forest model (`pip install scikit-learn` to run it).

For the full reproduction — synthetic labelled dataset, precision/recall/F1 against known anomaly classes, timeline and correlation-matrix plots — see the companion notebook in [AmadouAnne/anomaly-detection-research](https://github.com/AmadouAnne/anomaly-detection-research/tree/main/hal-anomaly-detection-reproduction), which this package's collector was extracted from.

## What this package does *not* claim

- It does not ship an anomaly-detection model — that's a deliberate scope boundary, see above.
- The <0.5% overhead figure is a claim about the *collector*, measured live on whatever host you run it on; it says nothing about the detection accuracy of any given downstream model.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Citation

If you use this in research, please cite the preprint — see [CITATION.cff](CITATION.cff).

## License

MIT — see [LICENSE](LICENSE).
