"""Capture plotting and CSV export."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def _format_time_axis(times: list[float]) -> tuple[list[float], str]:
    """Scale time values and return (scaled_times, unit_label)."""
    if not times:
        return times, "s"
    max_t = max(times)
    if max_t < 1e-3:
        return [t * 1e6 for t in times], "\u00b5s"
    if max_t < 1.0:
        return [t * 1e3 for t in times], "ms"
    return times, "s"


def save_capture_plot(
    data: dict,
    output_path: str | Path,
    title: str | None = None,
) -> Path:
    """Save an oscilloscope-style plot of captured data.

    Args:
        data: Dict with keys time, ch1, ch2, sample_rate, config.
        output_path: Path to save (PNG or SVG based on extension).
        title: Optional plot title.

    Returns:
        Resolved output path.
    """
    output_path = Path(output_path)
    scaled_time, time_unit = _format_time_axis(data["time"])

    fig, ax = plt.subplots(figsize=(12, 6))

    # Dark scope-style theme
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")
    ax.tick_params(colors="#e0e0e0")
    for spine in ax.spines.values():
        spine.set_color("#333")

    # Plot channels
    ax.plot(scaled_time, data["ch1"], color="#ffff00", linewidth=0.8, label="CH1")
    ax.plot(scaled_time, data["ch2"], color="#00bfff", linewidth=0.8, label="CH2")

    ax.set_xlabel(f"Time ({time_unit})", color="#e0e0e0")
    ax.set_ylabel("Voltage (V)", color="#e0e0e0")
    ax.legend(loc="upper right", facecolor="#1a1a2e", edgecolor="#333", labelcolor="#e0e0e0")
    ax.grid(True, color="#333", linewidth=0.5, alpha=0.7)

    plot_title = title or f"Capture @ {data['sample_rate']}"
    ax.set_title(plot_title, color="#e0e0e0", fontsize=13)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)

    return output_path.resolve()


def save_capture_csv(data: dict, output_path: str | Path) -> Path:
    """Export capture data as CSV with metadata header.

    Args:
        data: Dict with keys time, ch1, ch2, sample_rate, config.
        output_path: Path to write CSV.

    Returns:
        Resolved output path.
    """
    output_path = Path(output_path)
    cfg = data.get("config", {})

    with open(output_path, "w", newline="") as f:
        f.write(f"# sample_rate: {data['sample_rate']}\n")
        f.write(f"# ch1_range: {cfg.get('ch1_range', '?')}\n")
        f.write(f"# ch2_range: {cfg.get('ch2_range', '?')}\n")
        writer = csv.writer(f)
        writer.writerow(["time_s", "ch1_v", "ch2_v"])
        for t, v1, v2 in zip(data["time"], data["ch1"], data["ch2"]):
            writer.writerow([t, v1, v2])

    return output_path.resolve()
