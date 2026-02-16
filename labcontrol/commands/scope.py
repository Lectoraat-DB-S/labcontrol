"""Scope-specific commands."""

import click

from ..output import status_display, success, error, console

# Hardware constraints
MAX_SAMPLES = 2048
MIN_RATE = 20e3    # 20 kS/s
MAX_RATE = 48e6    # 48 MS/s
MAX_SINGLE_DURATION = MAX_SAMPLES / MIN_RATE  # 0.1024s (single-shot limit)
MAX_STREAM_DURATION = 30.0  # streaming limit in seconds


@click.group()
def scope():
    """Scope configuration commands."""
    pass


@scope.command()
def status():
    """Show current scope configuration."""
    from ..drivers import hantek  # noqa: F401
    from ..drivers.registry import get_device

    driver = get_device("scope")
    if not driver:
        error("Scope not found or failed to connect")
        return
    status_display(driver.get_status())


@scope.command("set")
@click.argument("settings", nargs=-1, required=True)
def set_cmd(settings: tuple[str, ...]):
    """Set individual scope settings. E.g.: ch1.vdiv=0.5 ch2.coupling=AC timebase=1ms"""
    from ..drivers import hantek  # noqa: F401
    from ..drivers.registry import get_device
    from ..preset import parse_time_value

    driver = get_device("scope")
    if not driver:
        error("Scope not found or failed to connect")
        return

    for setting in settings:
        if "=" not in setting:
            error(f"Invalid setting format: {setting!r} (use key=value)")
            continue
        key, value = setting.split("=", 1)
        key = key.strip().lower()

        try:
            if key.startswith("ch") and key.endswith(".vdiv"):
                ch = int(key[2])
                result = driver.set_channel_vdiv(ch, float(value))
            elif key.startswith("ch") and key.endswith(".coupling"):
                ch = int(key[2])
                result = driver.set_channel_coupling(ch, value)
            elif key == "timebase":
                result = driver.set_timebase(parse_time_value(value))
            else:
                error(f"Unknown setting: {key}")
                continue
            success(result)
        except Exception as e:
            error(f"Failed to set {key}: {e}")


@scope.command()
@click.option("--save", "save_path", type=click.Path(), default=None, help="Save plot as PNG/SVG")
@click.option("--csv", "csv_path", type=click.Path(), default=None, help="Export data as CSV")
@click.option("--samples", default=None, type=int, help="Number of samples (default: 1024, max: 2048)")
@click.option("--interval", default=None, type=float, help="Seconds between samples (sets sample rate)")
@click.option("--duration", default=None, type=float, help="Total capture time in seconds")
@click.option("--title", default=None, help="Plot title")
def capture(
    save_path: str | None,
    csv_path: str | None,
    samples: int | None,
    interval: float | None,
    duration: float | None,
    title: str | None,
):
    """Capture waveform data from the scope.

    Short captures (<=2048 samples) use fast single-shot mode.
    Longer captures use async streaming for durations up to 30s.

    \b
    Examples:
      scope capture                           # 1024 samples @ current rate
      scope capture --samples 2048            # max single-shot samples
      scope capture --duration 0.01           # 10ms → single-shot
      scope capture --duration 1.0            # 1s → streaming
      scope capture --duration 5.0            # 5s → streaming
      scope capture --interval 0.00005        # 50us = 20 kS/s
    \b
    See valid rates: scope rates
    """
    from ..drivers import hantek  # noqa: F401
    from ..drivers.registry import get_device
    from ..drivers.hantek import _find_best_sample_rate
    from PyHT6022.LibUsbScope import Oscilloscope

    if interval is not None and duration is not None:
        error("Use --interval or --duration, not both")
        return

    # --- Validate constraints ---
    use_stream = False

    if samples is not None and samples > MAX_SAMPLES and duration is None:
        error(
            f"{samples} samples te veel voor single-shot. Max: {MAX_SAMPLES}.\n"
            f"Gebruik --duration voor langere captures:\n"
            f"  labcontrol scope capture --duration 1.0"
        )
        return

    if duration is not None:
        if duration > MAX_STREAM_DURATION:
            error(
                f"Duration {duration}s te lang. Max: {MAX_STREAM_DURATION}s.\n"
                f"Suggestie: labcontrol scope capture --duration {MAX_STREAM_DURATION}"
            )
            return

        # --duration always uses streaming (async API is more reliable than
        # single-shot read_data which suffers from LIBUSB_ERROR_OVERFLOW)
        desired_rate = (samples if samples else MAX_SAMPLES) / duration
        rate_idx = _find_best_sample_rate(desired_rate)
        use_stream = True

    elif interval is not None:
        desired_rate = 1.0 / interval
        if desired_rate < MIN_RATE:
            max_interval = 1.0 / MIN_RATE
            error(
                f"Interval {interval}s te groot (rate {desired_rate:.0f} Hz < min {MIN_RATE/1e3:.0f} kS/s).\n"
                f"Suggestie: labcontrol scope capture --interval {max_interval}"
            )
            return
        if desired_rate > MAX_RATE:
            min_interval = 1.0 / MAX_RATE
            error(
                f"Interval {interval}s te klein (rate {desired_rate/1e6:.0f} MHz > max {MAX_RATE/1e6:.0f} MS/s).\n"
                f"Suggestie: labcontrol scope capture --interval {min_interval:.10f}"
            )
            return

        rate_idx = _find_best_sample_rate(desired_rate)
        _label, actual_rate = Oscilloscope.SAMPLE_RATES[rate_idx]

        if samples is None:
            samples = 1024

    else:
        rate_idx = None
        if samples is None:
            samples = 1024

    # --- Connect and capture ---

    driver = get_device("scope")
    if not driver:
        error("Scope not found or failed to connect")
        return

    if rate_idx is not None:
        _label, actual_rate = Oscilloscope.SAMPLE_RATES[rate_idx]
        result = driver.set_sample_rate(rate_idx)
        if use_stream:
            success(f"{result} (streaming {duration}s)")
        else:
            actual_interval = 1.0 / actual_rate
            actual_duration = samples / actual_rate
            success(f"{result} (interval: {actual_interval:.6f}s, duur: {actual_duration:.6f}s)")

    try:
        if use_stream:
            data = driver.capture_stream(duration=duration)
        else:
            data = driver.capture(num_samples=samples)
    except Exception as e:
        error(f"Capture failed: {e}")
        return

    # Show summary
    from rich.table import Table

    times = data["time"]
    actual_dur = times[-1] - times[0] if len(times) > 1 else 0
    table = Table(title=f"Capture: {len(data['ch1'])} samples @ {data['sample_rate']} ({actual_dur:.6f}s)")
    table.add_column("Channel", style="cyan")
    table.add_column("Min (V)", style="white")
    table.add_column("Max (V)", style="white")
    table.add_column("Avg (V)", style="white")
    for ch_name, ch_key in [("CH1", "ch1"), ("CH2", "ch2")]:
        vals = data[ch_key]
        if vals:
            table.add_row(
                ch_name,
                f"{min(vals):.4f}",
                f"{max(vals):.4f}",
                f"{sum(vals) / len(vals):.4f}",
            )
    console.print(table)

    if save_path:
        from ..plotting import save_capture_plot

        out = save_capture_plot(data, save_path, title=title)
        success(f"Plot saved: {out}")

    if csv_path:
        from ..plotting import save_capture_csv

        out = save_capture_csv(data, csv_path)
        success(f"CSV saved: {out}")

    driver.disconnect()
    success("Scope disconnected")


@scope.command("rates")
def rates_cmd():
    """Show supported hardware sample rates and their limits."""
    from PyHT6022.LibUsbScope import Oscilloscope
    from rich.table import Table

    table = Table(title=f"Hantek DSO-6022 Sample Rates (single-shot max {MAX_SAMPLES}, stream max {MAX_STREAM_DURATION}s)")
    table.add_column("Rate", style="cyan")
    table.add_column("Interval", style="white")
    table.add_column("Max duur", style="white")
    table.add_column("Stream 1s", style="green")

    for idx in sorted(Oscilloscope.SAMPLE_RATES.keys()):
        label, rate = Oscilloscope.SAMPLE_RATES[idx]
        interval = 1.0 / rate
        max_dur = MAX_SAMPLES / rate

        # Format interval
        if interval >= 1e-3:
            interval_str = f"{interval * 1e3:.3f}ms"
        elif interval >= 1e-6:
            interval_str = f"{interval * 1e6:.3f}us"
        else:
            interval_str = f"{interval * 1e9:.3f}ns"

        # Format single-shot duration
        if max_dur >= 1e-3:
            dur_str = f"{max_dur * 1e3:.2f}ms"
        elif max_dur >= 1e-6:
            dur_str = f"{max_dur * 1e6:.2f}us"
        else:
            dur_str = f"{max_dur * 1e9:.2f}ns"

        # Stream 1s data volume (2 channels × rate samples × 1 byte each)
        stream_bytes = rate * 2  # 2 channels, 8-bit ADC
        if stream_bytes >= 1e6:
            stream_str = f"{stream_bytes / 1e6:.1f} MB"
        else:
            stream_str = f"{stream_bytes / 1e3:.0f} KB"

        table.add_row(label, interval_str, dur_str, stream_str)

    console.print(table)
