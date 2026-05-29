"""
tdd_trigger_stream.py — Pluto TDD engine with external L10P sync pulse.

Used by Mode 2 (HW chain + oscilloscope) as an alternative TX path: instead
of driving the Pluto via MATLAB's sdrtx continuous-repeat, we use the
ADALM-Pluto AXI TDD engine to:

  1. Re-trigger the TX DMA at every frame (chirp is played back in a
     perfectly PRI-locked manner)
  2. Drive a rectangular pulse on pin L10P (PL_GPIO_0, Zynq K13) that is
     visible to an external oscilloscope as the capture trigger.

The rising edge of the L10P pulse and the first sample of the chirp are
produced by the SAME hardware counter — relative jitter < 10 ns.  A fixed
pipeline delay (tens of ns) exists between the TDD sync event and the
actual DAC output; this shows up as a constant range offset on the radar
spectrum and can be calibrated out.

TDD channel mapping (stock Pluto, firmware ≥ 0.39):
  channel[0]  →  L10P pulse (scope trigger)     — enabled via gpio_phaser_enable
  channel[1]  →  RX DMA sync    — not used here (Mode 2 has no Pluto RX)
  channel[2]  →  TX DMA sync    — makes the chirp start at each frame

Requirements:
  * ADALM-Pluto Rev C or Rev D (Rev B does NOT have the TDD IP)
  * Firmware ≥ 0.39
  * pyadi-iio ≥ 0.0.18  (provides the adi.tddn class)

Note on gpio_phaser_enable:
  This flag (on the adi.one_bit_adc_dac device) multiplexes L10P away
  from its default "SPI MOSI" function and routes the TDD channel[0]
  output there.  The name mentions "phaser" but it is simply the mux
  enable for the TDD→L10P route; it works on any stock Pluto.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import adi
import numpy as np


@dataclass
class TDDStreamHandles:
    """Container for the active pyadi-iio objects.

    When ``tdd`` and ``pins`` are ``None`` this represents a plain cyclic-TX
    stream (no AXI TDD engine, no L10P pulse) — see
    :func:`start_continuous_stream`.
    """
    sdr:      "adi.Pluto"
    tdd:      "adi.tddn | None"
    pins:     "adi.one_bit_adc_dac | None"


def start_tdd_stream(
    pluto_ip:     str,
    sample_rate:  int,
    center_freq:  int,
    tx_gain:      float,
    tx_iq:        np.ndarray,
    frame_ms:     float,
    pulse_us:     float,
) -> TDDStreamHandles:
    """
    Configure the Pluto TDD engine and start transmitting ``tx_iq`` in a
    PRI-locked loop, while emitting a rectangular pulse on L10P at the
    start of every frame.

    Parameters
    ----------
    pluto_ip     : IP, e.g. ``'192.168.2.1'``
    sample_rate  : Pluto Fs in Sa/s (e.g. 60_500_000)
    center_freq  : Pluto LO in Hz (e.g. 2_500_000_000)
    tx_gain      : TX attenuation in dB (negative, e.g. -15)
    tx_iq        : interleaved int16 [I0, Q0, I1, Q1, ...] column vector
                   (output of MATLAB ``pluto_build_input.m``).  Must contain
                   exactly one chirp period (samples_per_chirp complex samples
                   → 2*samples_per_chirp int16 values).
    frame_ms     : PRI (T_chirp + T_gap) in milliseconds
    pulse_us     : L10P rising-edge-on time in microseconds.  Must be
                   shorter than the frame.  The rising edge is the scope
                   trigger; the falling edge does not need to coincide
                   with anything.

    Returns
    -------
    handles : :class:`TDDStreamHandles`  — keep this alive; when the
        process exits, call :func:`stop_tdd_stream` to release hardware.
    """
    if pulse_us <= 0:
        raise ValueError("pulse_us must be > 0")
    if pulse_us / 1e3 >= frame_ms:
        raise ValueError(
            f"pulse_us ({pulse_us} µs) must be shorter than frame_ms "
            f"({frame_ms} ms × 1000 µs)"
        )

    uri = f"ip:{pluto_ip}"
    print(f"[tdd_stream] connecting to Pluto at {uri}")
    sdr  = adi.Pluto(uri=uri)
    tdd  = adi.tddn(uri)
    pins = adi.one_bit_adc_dac(uri)

    # ── LO / sample rate: program only if still factory-default ──────────
    # Reprogramming an already-locked PLL causes a glitch; detect by the
    # post-boot default values (same heuristic as setup_pluto_tdd.py).
    _FS_DEFAULT_LOW, _FS_DEFAULT_HIGH      = 30_719_990, 30_720_009
    _LO_DEFAULT_RX_LOW, _LO_DEFAULT_RX_HIGH = 2_399_999_990, 2_400_000_009
    _LO_DEFAULT_TX_LOW, _LO_DEFAULT_TX_HIGH = 2_449_999_990, 2_450_000_009

    is_default = (
        _FS_DEFAULT_LOW  < sdr.sample_rate < _FS_DEFAULT_HIGH
        and _LO_DEFAULT_RX_LOW < sdr.rx_lo  < _LO_DEFAULT_RX_HIGH
        and _LO_DEFAULT_TX_LOW < sdr.tx_lo  < _LO_DEFAULT_TX_HIGH
    )
    if is_default:
        sdr.sample_rate = int(sample_rate)
        sdr.rx_lo       = int(center_freq)
        sdr.tx_lo       = int(center_freq)
        print(f"[tdd_stream] programmed Fs={sample_rate} Hz  LO={center_freq} Hz")
    else:
        print(f"[tdd_stream] Pluto already configured: "
              f"Fs={sdr.sample_rate} Hz  LO={sdr.tx_lo} Hz")

    # ── TX configuration ────────────────────────────────────────────────
    sdr.tx_enabled_channels   = [0]
    sdr.tx_hardwaregain_chan0 = float(tx_gain)
    sdr.tx_cyclic_buffer      = True  # TDD re-gates the buffer every frame

    # ── Route channel[0] → L10P (scope trigger) ─────────────────────────
    # This takes L10P away from its default "SPI MOSI" mux and connects
    # it to TDD channel[0].  Must be set BEFORE tdd.enable = True.
    pins.gpio_phaser_enable = True
    print("[tdd_stream] L10P mux enabled (gpio_phaser_enable = True)")

    # ── TDD engine ──────────────────────────────────────────────────────
    # Disable while reconfiguring.
    tdd.enable = False

    tdd.startup_delay_ms = 0
    tdd.frame_length_ms  = float(frame_ms)
    tdd.burst_count      = 0          # 0 = repeat indefinitely

    # channel[0]: rectangular pulse on L10P
    tdd.channel[0].polarity = 0
    tdd.channel[0].on_ms    = 0.0
    tdd.channel[0].off_ms   = float(pulse_us) / 1_000.0  # µs → ms
    tdd.channel[0].enable   = True

    # channel[1]: RX DMA sync — not used, park it low
    tdd.channel[1].polarity = 0
    tdd.channel[1].on_raw   = 0
    tdd.channel[1].off_raw  = 10
    tdd.channel[1].enable   = False

    # channel[2]: TX DMA sync — re-triggers the TX buffer every frame.
    # The rising edge here is simultaneous with channel[0] on the same
    # 100 MHz counter → relative jitter < 10 ns.
    tdd.channel[2].polarity = 0
    tdd.channel[2].on_raw   = 0
    tdd.channel[2].off_raw  = 10
    tdd.channel[2].enable   = True

    # Use the internal sync generator so the engine self-starts on enable.
    tdd.sync_external = False
    tdd.sync_internal = True
    tdd.sync_reset    = False

    # ── Load TX buffer ──────────────────────────────────────────────────
    # tx_iq is an interleaved int16 vector [I0, Q0, I1, Q1, ...].
    # Convert back to complex float (pyadi-iio takes complex for Pluto).
    tx_iq = np.asarray(tx_iq).reshape(-1)
    if tx_iq.size % 2 != 0:
        raise ValueError("tx_iq must have an even length (interleaved I/Q)")
    I = tx_iq[0::2].astype(np.float32)
    Q = tx_iq[1::2].astype(np.float32)
    iq = I + 1j * Q
    print(f"[tdd_stream] TX buffer: {iq.size} complex samples  "
          f"({iq.size / sdr.sample_rate * 1e3:.3f} ms)")
    sdr.tx(iq)

    # ── Arm + start ─────────────────────────────────────────────────────
    tdd.enable    = True
    tdd.sync_soft = 1
    print(f"[tdd_stream] TDD running: frame={frame_ms:.3f} ms  "
          f"L10P pulse={pulse_us:.2f} µs")

    return TDDStreamHandles(sdr=sdr, tdd=tdd, pins=pins)


def start_continuous_stream(
    pluto_ip:     str,
    sample_rate:  int,
    center_freq:  int,
    tx_gain:      float,
    tx_iq:        np.ndarray,
) -> TDDStreamHandles:
    """
    Start a plain cyclic TX on the Pluto (no AXI TDD engine, no L10P pulse).

    Pluto replays ``tx_iq`` from its cyclic buffer indefinitely.  No frame
    re-arm and no sync pulse on L10P — the oscilloscope must be put in
    AUTO/free-run mode because there is no deterministic trigger source.
    Doppler processing is NOT usable in this mode (no phase-coherent
    reference), but it is useful for quickly verifying the RF chain
    (signal present on the scope, beat on the mixer output).

    Parameters match :func:`start_tdd_stream` except ``frame_ms`` and
    ``pulse_us`` are absent (no TDD timing to program).

    Returns
    -------
    handles : :class:`TDDStreamHandles` with ``tdd=None, pins=None``.
    """
    uri = f"ip:{pluto_ip}"
    print(f"[continuous_stream] connecting to Pluto at {uri}")
    sdr = adi.Pluto(uri=uri)

    # Same "don't reprogram if already default" heuristic as start_tdd_stream.
    _FS_DEFAULT_LOW, _FS_DEFAULT_HIGH       = 30_719_990, 30_720_009
    _LO_DEFAULT_RX_LOW, _LO_DEFAULT_RX_HIGH = 2_399_999_990, 2_400_000_009
    _LO_DEFAULT_TX_LOW, _LO_DEFAULT_TX_HIGH = 2_449_999_990, 2_450_000_009

    is_default = (
        _FS_DEFAULT_LOW  < sdr.sample_rate < _FS_DEFAULT_HIGH
        and _LO_DEFAULT_RX_LOW < sdr.rx_lo  < _LO_DEFAULT_RX_HIGH
        and _LO_DEFAULT_TX_LOW < sdr.tx_lo  < _LO_DEFAULT_TX_HIGH
    )
    if is_default:
        sdr.sample_rate = int(sample_rate)
        sdr.rx_lo       = int(center_freq)
        sdr.tx_lo       = int(center_freq)
        print(f"[continuous_stream] programmed Fs={sample_rate} Hz  "
              f"LO={center_freq} Hz")
    else:
        print(f"[continuous_stream] Pluto already configured: "
              f"Fs={sdr.sample_rate} Hz  LO={sdr.tx_lo} Hz")

    sdr.tx_enabled_channels   = [0]
    sdr.tx_hardwaregain_chan0 = float(tx_gain)
    sdr.tx_cyclic_buffer      = True

    # Load TX buffer — same interleave convention as start_tdd_stream.
    tx_iq = np.asarray(tx_iq).reshape(-1)
    if tx_iq.size % 2 != 0:
        raise ValueError("tx_iq must have an even length (interleaved I/Q)")
    I = tx_iq[0::2].astype(np.float32)
    Q = tx_iq[1::2].astype(np.float32)
    iq = I + 1j * Q
    print(f"[continuous_stream] TX buffer: {iq.size} complex samples  "
          f"({iq.size / sdr.sample_rate * 1e3:.3f} ms)  cyclic")
    sdr.tx(iq)

    return TDDStreamHandles(sdr=sdr, tdd=None, pins=None)


def stop_tdd_stream(h: TDDStreamHandles) -> None:
    """
    Cleanly shut down the TDD engine (if present), stop TX, and release
    L10P back to its default mux target.  Safe to call multiple times;
    also handles continuous-stream handles (where ``tdd`` and ``pins`` are
    ``None``).
    """
    print("[tdd_stream] shutdown requested")

    # Disable TDD engine first so the DMA stops being retriggered.
    if h.tdd is not None:
        try:
            h.tdd.enable = False
        except Exception as e:
            print(f"[tdd_stream] warning: tdd.enable=False failed: {e}")

        # Park all channels (prevents any lingering pulse on L10P).
        try:
            for ch in range(3):
                h.tdd.channel[ch].enable   = False
                h.tdd.channel[ch].polarity = 0
                h.tdd.channel[ch].on_raw   = 0
                h.tdd.channel[ch].off_raw  = 0
        except Exception as e:
            print(f"[tdd_stream] warning: channel park failed: {e}")

    # Release TX buffer.
    try:
        h.sdr.tx_destroy_buffer()
    except Exception as e:
        print(f"[tdd_stream] warning: tx_destroy_buffer failed: {e}")

    # Return L10P to SPI MOSI (default mux).
    if h.pins is not None:
        try:
            h.pins.gpio_phaser_enable = False
        except Exception as e:
            print(f"[tdd_stream] warning: gpio_phaser_enable=False failed: {e}")

    print("[tdd_stream] shutdown complete")


def heartbeat(h: TDDStreamHandles, period_s: float = 5.0) -> None:
    """Print a short status line once per ``period_s`` seconds."""
    print(f"[tdd_stream] heartbeat  tdd.state={h.tdd.state}  "
          f"frame={h.tdd.frame_length_ms:.3f} ms")
    time.sleep(period_s)
