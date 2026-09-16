"""Minimal example: feed collected /proc samples into an unsupervised
anomaly detector (Isolation Forest).

This demo mirrors the methodology used in the paper's reproduction
notebook (see the README "Related work" section) but keeps the
dependency footprint of the core package at zero: scikit-learn is only
required to run this example, not to `import linux_proc_anomaly`.

Usage:
    pip install linux-proc-anomaly scikit-learn
    python examples/isolation_forest_demo.py
"""

from sklearn.ensemble import IsolationForest

from linux_proc_anomaly import collect


def main() -> None:
    print("Collecting 10s of real /proc metrics from this host...")
    result = collect(duration_s=10.0, interval_s=0.5)
    print(f"Collected {len(result.rows)} samples, overhead {result.overhead_pct:.4f}% of wall-clock time")

    features = [
        [row["cpu_user"], row["cpu_system"], row["mem_available_kb"], row["net_rx_bytes"]]
        for row in result.rows
    ]

    model = IsolationForest(random_state=42)
    labels = model.fit_predict(features)  # -1 = anomaly, 1 = normal
    n_anomalies = sum(1 for label in labels if label == -1)
    print(f"Flagged {n_anomalies}/{len(labels)} samples as anomalous")


if __name__ == "__main__":
    main()
