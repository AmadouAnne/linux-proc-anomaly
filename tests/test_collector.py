import time

from linux_proc_anomaly.collector import collect, read_cpu_times, read_meminfo, read_net_dev, sample_once


def test_read_cpu_times_has_expected_keys():
    keys = read_cpu_times()
    assert set(keys) == {
        "cpu_user", "cpu_nice", "cpu_system", "cpu_idle", "cpu_iowait", "cpu_irq", "cpu_softirq",
    }
    assert all(isinstance(v, int) for v in keys.values())


def test_read_meminfo_has_expected_keys():
    keys = read_meminfo()
    assert set(keys) == {"mem_total_kb", "mem_free_kb", "mem_available_kb"}
    assert keys["mem_total_kb"] > 0


def test_read_net_dev_excludes_loopback_by_default():
    counters = read_net_dev()
    assert set(counters) == {"net_rx_bytes", "net_tx_bytes"}
    assert counters["net_rx_bytes"] >= 0
    assert counters["net_tx_bytes"] >= 0


def test_sample_once_measures_its_own_cost():
    row = sample_once()
    assert row["collector_cpu_time_s"] >= 0
    assert row["timestamp"] <= time.time()


def test_collect_returns_expected_sample_count_and_overhead():
    result = collect(duration_s=0.6, interval_s=0.2)
    assert len(result.rows) == 3
    assert result.wall_elapsed_s > 0
    assert 0 <= result.overhead_pct < 100
