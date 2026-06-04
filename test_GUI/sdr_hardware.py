import adi
import numpy as np

class PlutoController:
    def __init__(self, ip_address="ip:192.168.2.1"):
        self.ip_address = ip_address
        self.sdr = None

    def connect(self):
        try:
            self.sdr = adi.Pluto(self.ip_address)
            return True, "Successfully connected to PlutoSDR."
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def configure(self, sample_rate, rx_lo, tx_lo, rx_gain, tx_gain, cyclic_buffer):
        if not self.sdr:
            return False, "SDR not connected."
        try:
            self.sdr.sample_rate = int(sample_rate)
            self.sdr.rx_lo = int(rx_lo)
            self.sdr.tx_lo = int(tx_lo)
            self.sdr.gain_control_mode_chan0 = 'manual'
            self.sdr.rx_hardwaregain_chan0 = float(rx_gain)
            self.sdr.tx_hardwaregain_chan0 = float(tx_gain)
            self.sdr.tx_cyclic_buffer = cyclic_buffer
            return True, "Configuration applied successfully."
        except Exception as e:
            return False, f"Configuration error: {str(e)}"

    def transmit(self, samples):
        if not self.sdr:
            return False
        try:
            self.sdr.tx(samples)
            return True
        except Exception as e:
            print(f"TX Error: {e}")
            return False

    def stop_transmit(self):
        if self.sdr:
            try:
                self.sdr.tx_destroy_buffer()
            except:
                pass

    def receive(self, num_samples):
        if not self.sdr:
            return None
        try:
            self.sdr.rx_buffer_size = int(num_samples)
            samples = self.sdr.rx()
            return samples
        except Exception as e:
            print(f"RX Error: {e}")
            return None