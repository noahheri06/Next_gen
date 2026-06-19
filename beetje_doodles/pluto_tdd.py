"""
pluto_tdd.py - ADALM-Pluto AXI-TDD backend.  Single file, two independent uses:

  A) TX + trigger  (scope project):  start_tdd_stream() / stop_tdd_stream()
       Pluto transmits a cyclic chirp and emits an L10P pulse on every frame
       (the oscilloscope trigger).  The scope is the receiver.

  B) TX + RX       (transceiver project):  init_pluto_txrx() / transmit_receive()
       The TDD engine synchronizes TX *and* RX: the Pluto transmits the chirp and
       captures its own echo, PRI-locked, n_frames at a time.  No oscilloscope;
       the dechirp is done in software.

Called from MATLAB: pluto_tx_tdd.m (A) and pluto_txrx.m (B), via py.pluto_tdd.*

TDD channel mapping (stock Pluto, firmware >= 0.39, Rev C/D):
  A) channel[0] -> L10P pulse (scope trigger, via gpio_phaser_enable)
     channel[1] -> off ;  channel[2] -> TX DMA sync
  B) channel[0] -> TX gate ;  channel[1] -> RX DMA sync ;  channel[2] -> TX DMA sync

Requires: ADALM-Pluto Rev C/D, firmware >= 0.39, `pip install pyadi-iio numpy`.
"""

from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import adi


SCALE = 4096   # complex |.|=1 -> int16 +/-4096 (Pluto 12-bit DAC convention)


def _deinterleave(tx_iq):
    """int16 [I0,Q0,I1,Q1,...] -> complex64 (already DAC-scaled)."""
    iq = np.asarray(tx_iq).reshape(-1)
    if iq.size % 2:
        raise ValueError("tx_iq must be even-length (interleaved I/Q)")
    return iq[0::2].astype(np.float32) + 1j * iq[1::2].astype(np.float32)


# =====================================================================
#  A)  TX + trigger  (scope project)
# =====================================================================

@dataclass
class TDDStreamHandles:
    """Active pyadi-iio objects - keep alive, pass to stop_tdd_stream()."""
    sdr:  object
    tdd:  object
    pins: object


def start_tdd_stream(pluto_ip, sample_rate, center_freq, tx_gain,
                     tx_iq, frame_ms, pulse_us):
    """Start PRI-locked cyclic TX + an L10P trigger pulse on every frame.

    tx_iq    : interleaved int16 [I0,Q0,...] = one chirp period.
    frame_ms : PRI in ms.   pulse_us : L10P width in us (< frame_ms*1000).
    """
    if pulse_us <= 0 or pulse_us / 1e3 >= frame_ms:
        raise ValueError("need 0 < pulse_us < frame_ms * 1000")

    uri = "ip:" + str(pluto_ip)
    print("[tdd] connecting to", uri)
    sdr  = adi.Pluto(uri=uri)
    tdd  = adi.tddn(uri)
    pins = adi.one_bit_adc_dac(uri)

    sdr.sample_rate           = int(sample_rate)
    sdr.tx_rf_bandwidth       = int(sample_rate)   # analog TX filter = full chirp band
    sdr.tx_lo                 = int(center_freq)
    sdr.rx_lo                 = int(center_freq)
    sdr.tx_enabled_channels   = [0]
    sdr.tx_hardwaregain_chan0 = float(tx_gain)
    sdr.tx_cyclic_buffer      = True

    pins.gpio_phaser_enable = True       # route TDD channel[0] -> L10P pin

    tdd.enable           = False
    tdd.startup_delay_ms = 0
    tdd.frame_length_ms  = float(frame_ms)
    tdd.burst_count      = 0             # 0 = loop forever
    # channel[0]: L10P pulse, rising edge at frame start (scope trigger)
    tdd.channel[0].polarity = 0
    tdd.channel[0].on_ms    = 0.0
    tdd.channel[0].off_ms   = float(pulse_us) / 1000.0
    tdd.channel[0].enable   = True
    # channel[1]: RX DMA sync - unused (the scope receives)
    tdd.channel[1].enable   = False
    # channel[2]: TX DMA sync - restarts the cyclic chirp every frame
    tdd.channel[2].polarity = 0
    tdd.channel[2].on_raw   = 0
    tdd.channel[2].off_raw  = 10
    tdd.channel[2].enable   = True
    # External-sync + soft pulse: the production-validated RadarNEXT path
    # (sync_internal is read-only on Rev C bitstreams).
    tdd.sync_external = True
    tdd.sync_reset    = False
    tdd.enable        = True

    cplx = _deinterleave(tx_iq)
    try:
        sdr.tx_destroy_buffer()
    except Exception:
        pass
    sdr.tx(cplx)
    tdd.sync_soft = 1
    print("[tdd] running: frame=%.3f ms  L10P=%.1f us  %d samples"
          % (frame_ms, pulse_us, cplx.size))
    return TDDStreamHandles(sdr=sdr, tdd=tdd, pins=pins)


def stop_tdd_stream(h):
    """Stop TX, park the TDD channels, silence the carrier, release L10P."""
    if h is None:
        return
    try:
        h.tdd.enable = False
        for ch in range(3):
            h.tdd.channel[ch].enable = False
    except Exception:
        pass
    try:
        h.sdr.tx_hardwaregain_chan0 = -88.0     # silence BEFORE destroy
    except Exception:
        pass
    try:
        h.sdr.tx_destroy_buffer()
    except Exception:
        pass
    try:
        h.pins.gpio_phaser_enable = False
    except Exception:
        pass
    print("[tdd] stopped")


# =====================================================================
#  B)  TX + RX transceiver  (Pluto receives its own echo)
# =====================================================================

def init_pluto_txrx(pluto_ip, sample_rate, center_freq, rx_gain, tx_gain,
                    frame_ms, n_samples):
    """Configure the Pluto + TDD engine for synchronized TX *and* RX.

    Returns (sdr, tdd).  Fs/LO and the TX/RX analog filter bandwidth are always
    programmed (like the lab's setupPlutoSDR.py). To change Fs/LO reliably after
    a run, reboot the Pluto (unplug/replug).
    """
    uri = "ip:" + str(pluto_ip)
    print("[txrx] connecting to", uri)
    sdr = adi.Pluto(uri=uri)
    tdd = adi.tddn(uri)

    # Program Fs / LO / RF-bandwidth (TX and RX analog filters = full chirp band).
    sdr.sample_rate     = int(sample_rate)
    sdr.tx_rf_bandwidth = int(sample_rate)
    sdr.rx_rf_bandwidth = int(sample_rate)
    sdr.rx_lo           = int(center_freq)
    sdr.tx_lo           = int(center_freq)

    # --- RX ---
    sdr.rx_enabled_channels     = [0]
    sdr.gain_control_mode_chan0 = "manual"
    sdr.rx_hardwaregain_chan0   = int(rx_gain)
    sdr.rx_buffer_size          = int(n_samples)
    try:
        sdr._rxadc.set_kernel_buffers_count(1)   # minimum latency
    except Exception:
        pass

    # --- TX ---
    sdr.tx_enabled_channels   = [0]
    sdr.tx_hardwaregain_chan0 = float(tx_gain)
    sdr.tx_cyclic_buffer      = True

    # --- TDD: sync TX and RX on the same frame ---
    tdd.enable           = False
    tdd.startup_delay_ms = 0
    tdd.frame_length_ms  = float(frame_ms)
    tdd.burst_count      = 0
    # channel[0]: TX gate (PA on for the frame)
    tdd.channel[0].on_raw = 0; tdd.channel[0].off_raw = 0
    tdd.channel[0].polarity = 1; tdd.channel[0].enable = 1
    # channel[1]: RX DMA sync (starts the RX capture at the frame edge)
    tdd.channel[1].on_raw = 0; tdd.channel[1].off_raw = 10
    tdd.channel[1].polarity = 0; tdd.channel[1].enable = 1
    # channel[2]: TX DMA sync (restarts the chirp at the same edge)
    tdd.channel[2].on_raw = 0; tdd.channel[2].off_raw = 10
    tdd.channel[2].polarity = 0; tdd.channel[2].enable = 1
    tdd.sync_external = True
    tdd.enable        = True
    print("[txrx] configured: Fs=%d  rx_gain=%d  tx_gain=%.0f  frame=%.3f ms  N=%d"
          % (int(sdr.sample_rate), int(rx_gain), float(tx_gain), frame_ms, int(n_samples)))
    return sdr, tdd


def transmit_receive(sdr, tdd, tx_iq, n_frames, save_path):
    """Transmit tx_iq, capture n_frames echoes, and save
    <save_path>/received_data.mat with variable 'received_data' = a complex
    (n_frames, n_samples) matrix (one frame per row, like the lab's
    pluto_transmit_receive.py).

    The .mat round-trip is the robust way to hand a complex matrix to MATLAB.
    USB 2.0: the capture is bursted frame-by-frame (not a real-time stream);
    a few hundred frames take a couple of seconds.
    """
    import os
    from scipy.io import savemat

    cplx = _deinterleave(tx_iq)
    n_samples = int(sdr.rx_buffer_size)
    try:
        sdr._rx_init_channels()
    except Exception:
        pass
    try:
        sdr.tx_destroy_buffer()
    except Exception:
        pass
    sdr.tx(cplx)
    tdd.sync_soft = 1

    rx = np.zeros((int(n_frames), n_samples), dtype=np.complex64)
    for kf in range(int(n_frames)):
        rx[kf] = sdr.rx()

    try:
        tdd.enable = False
    except Exception:
        pass
    try:
        sdr.tx_destroy_buffer()
    except Exception:
        pass

    out = os.path.join(str(save_path), "received_data.mat")
    savemat(out, {"received_data": rx})            # (n_frames, n_samples), one frame per row
    print("[txrx] saved %d frames x %d samples -> %s" % (int(n_frames), n_samples, out))
    return out
