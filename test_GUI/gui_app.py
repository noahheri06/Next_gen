import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import waveform_gen
from sdr_hardware import PlutoController

class PlutoRadarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PlutoSDR Radar Controls")
        
        self.sdr_controller = PlutoController()
        self.tx_waveform = np.array([], dtype=complex)
        self.rx_history = []  # Stores multiple waves for coherent accumulation

        self.setup_ui()

    def setup_ui(self):
        # --- Hardware Parameters Frame ---
        hw_frame = tk.LabelFrame(self.root, text=" PlutoSDR Hardware Configuration ")
        hw_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(hw_frame, text="IP Address:").grid(row=0, column=0, padx=5, pady=2)
        self.entry_ip = tk.Entry(hw_frame, width=15)
        self.entry_ip.insert(0, "ip:192.168.2.1")
        self.entry_ip.grid(row=0, column=1, padx=5, pady=2)

        self.btn_connect = tk.Button(hw_frame, text="Connect", command=self.connect_sdr)
        self.btn_connect.grid(row=0, column=2, padx=10, pady=2)

        tk.Label(hw_frame, text="Sample Rate (Hz):").grid(row=1, column=0, padx=5, pady=2)
        self.entry_fs = tk.Entry(hw_frame, width=12)
        self.entry_fs.insert(0, "2084000")
        self.entry_fs.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(hw_frame, text="TX LO (Hz):").grid(row=1, column=2, padx=5, pady=2)
        self.entry_tx_lo = tk.Entry(hw_frame, width=12)
        self.entry_tx_lo.insert(0, "915000000")
        self.entry_tx_lo.grid(row=1, column=3, padx=5, pady=2)

        tk.Label(hw_frame, text="RX LO (Hz):").grid(row=1, column=4, padx=5, pady=2)
        self.entry_rx_lo = tk.Entry(hw_frame, width=12)
        self.entry_rx_lo.insert(0, "915000000")
        self.entry_rx_lo.grid(row=1, column=5, padx=5, pady=2)

        tk.Label(hw_frame, text="TX Gain (dB):").grid(row=2, column=0, padx=5, pady=2)
        self.entry_tx_gain = tk.Entry(hw_frame, width=12)
        self.entry_tx_gain.insert(0, "-10")
        self.entry_tx_gain.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(hw_frame, text="RX Gain (dB):").grid(row=2, column=2, padx=5, pady=2)
        self.entry_rx_gain = tk.Entry(hw_frame, width=12)
        self.entry_rx_gain.insert(0, "20")
        self.entry_rx_gain.grid(row=2, column=3, padx=5, pady=2)

        self.var_cyclic = tk.BooleanVar(value=True)
        self.chk_cyclic = tk.Checkbutton(hw_frame, text="Cyclic Buffer", variable=self.var_cyclic)
        self.chk_cyclic.grid(row=2, column=4, padx=5, pady=2)

        self.btn_apply = tk.Button(hw_frame, text="Apply Config", command=self.apply_config, state="disabled")
        self.btn_apply.grid(row=2, column=5, padx=5, pady=2)

        # --- Waveform Options Frame ---
        wf_frame = tk.LabelFrame(self.root, text=" Waveform Generation ")
        wf_frame.pack(fill="x", padx=10, pady=5)

        self.wf_type = tk.StringVar(value="chirp")
        tk.Radiobutton(wf_frame, text="Chirp", variable=self.wf_type, value="chirp").grid(row=0, column=0, padx=5)
        tk.Radiobutton(wf_frame, text="Complex Exp", variable=self.wf_type, value="exp").grid(row=0, column=1, padx=5)

        tk.Label(wf_frame, text="Num Samples:").grid(row=0, column=2, padx=5)
        self.entry_samples = tk.Entry(wf_frame, width=8)
        self.entry_samples.insert(0, "2048")
        self.entry_samples.grid(row=0, column=3, padx=5)

        tk.Label(wf_frame, text="Freq / Mid Freq (Hz):").grid(row=1, column=0, padx=5)
        self.entry_wf_freq = tk.Entry(wf_frame, width=10)
        self.entry_wf_freq.insert(0, "0")
        self.entry_wf_freq.grid(row=1, column=1, padx=5)

        tk.Label(wf_frame, text="Chirp Bandwidth (Hz):").grid(row=1, column=2, padx=5)
        self.entry_wf_bw = tk.Entry(wf_frame, width=10)
        self.entry_wf_bw.insert(0, "1000000")
        self.entry_wf_bw.grid(row=1, column=3, padx=5)

        btn_gen = tk.Button(wf_frame, text="Generate Signal", command=self.generate_signal)
        btn_gen.grid(row=1, column=4, padx=5, pady=5)

        btn_load = tk.Button(wf_frame, text="Load Ext File (.npy)", command=self.load_signal_file)
        btn_load.grid(row=1, column=5, padx=5, pady=5)

        # --- Action Control Panel ---
        act_frame = tk.Frame(self.root)
        act_frame.pack(fill="x", padx=10, pady=5)

        self.btn_tx = tk.Button(act_frame, text="Start Transmit", command=self.start_tx, state="disabled", bg="#d4edda")
        self.btn_tx.pack(side="left", padx=5)

        self.btn_stop_tx = tk.Button(act_frame, text="Stop Transmit", command=self.stop_tx, state="disabled", bg="#f8d7da")
        self.btn_stop_tx.pack(side="left", padx=5)

        self.btn_rx = tk.Button(act_frame, text="Capture Single RX", command=self.capture_rx, state="disabled")
        self.btn_rx.pack(side="left", padx=5)

        self.btn_coherent = tk.Button(act_frame, text="Add Coherently (Radar)", command=self.process_coherent, state="disabled")
        self.btn_coherent.pack(side="left", padx=5)

        self.btn_clear_radar = tk.Button(act_frame, text="Clear Radar History", command=self.clear_radar)
        self.btn_clear_radar.pack(side="left", padx=5)

        self.btn_save_rx = tk.Button(act_frame, text="Save Latest RX Data", command=self.save_rx_data)
        self.btn_save_rx.pack(side="right", padx=5)

        # --- Visual Matplotlib Graphs ---
        self.fig, (self.ax_tx, self.ax_rx) = plt.subplots(2, 1, figsize=(7, 4.5))
        self.fig.tight_layout(pad=2.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        self.update_plots_empty()

    def update_plots_empty(self):
        self.ax_tx.clear()
        self.ax_tx.set_title("Transmitted Signal (Time Domain Magnitude)")
        self.ax_tx.grid(True)
        
        self.ax_rx.clear()
        self.ax_rx.set_title("Received Signal (Time Domain Magnitude)")
        self.ax_rx.grid(True)
        self.canvas.draw()

    def connect_sdr(self):
        self.sdr_controller.ip_address = self.entry_ip.get()
        success, msg = self.sdr_controller.connect()
        messagebox.showinfo("Hardware Status", msg)
        if success:
            self.btn_apply.config(state="normal")
            self.btn_tx.config(state="normal")
            self.btn_stop_tx.config(state="normal")
            self.btn_rx.config(state="normal")
            self.btn_coherent.config(state="normal")

    def apply_config(self):
        success, msg = self.sdr_controller.configure(
            sample_rate=self.entry_fs.get(),
            rx_lo=self.entry_rx_lo.get(),
            tx_lo=self.entry_tx_lo.get(),
            rx_gain=self.entry_rx_gain.get(),
            tx_gain=self.entry_tx_gain.get(),
            cyclic_buffer=self.var_cyclic.get()
        )
        messagebox.showinfo("Config Status", msg)

    def generate_signal(self):
        fs = float(self.entry_fs.get())
        n = int(self.entry_samples.get())
        freq = float(self.entry_wf_freq.get())
        bw = float(self.entry_wf_bw.get())

        if self.wf_type.get() == "chirp":
            self.tx_waveform = waveform_gen.generate_chirp(fs, n, bw, freq)
        else:
            self.tx_waveform = waveform_gen.generate_complex_exp(fs, n, freq)

        self.plot_tx()

    def load_signal_file(self):
        path = filedialog.askopenfilename(filetypes=[("Numpy Binary", "*.npy"), ("CSV Text", "*.csv")])
        if path:
            try:
                self.tx_waveform = waveform_gen.load_waveform(path)
                self.plot_tx()
            except Exception as e:
                messagebox.showerror("Error Loading File", str(e))

    def plot_tx(self):
        self.ax_tx.clear()
        self.ax_tx.plot(np.real(self.tx_waveform), color='blue', label='Real')
        self.ax_tx.plot(np.imag(self.tx_waveform), color='green', label='Imaginary')
        self.ax_tx.set_title("Transmitted Signal Envelope (Magnitude)")
        self.ax_tx.grid(True)
        self.ax_tx.legend()
        self.canvas.draw()

    def start_tx(self):
        if len(self.tx_waveform) == 0:
            messagebox.showwarning("Warning", "Please generate or load a waveform first.")
            return
        # Ensure latest settings match configuration before sending data
        self.apply_config()
        self.sdr_controller.transmit(self.tx_waveform)

    def stop_tx(self):
        self.sdr_controller.stop_transmit()

    def capture_rx(self):
        n = int(self.entry_samples.get())
        samples = self.sdr_controller.receive(n)
        if samples is not None:
            self.rx_history.append(samples)
            self.plot_rx(samples, f"Received Signal (Capture #{len(self.rx_history)})")

    def process_coherent(self):
        if len(self.rx_history) < 2:
            messagebox.showwarning("Radar Processing", "Capture at least 2 waves into history first.")
            return
        if len(self.tx_waveform) == 0:
            messagebox.showerror("Radar Processing", "Transmitter wave reference is empty. Cannot align.")
            return

        coherent_result = waveform_gen.coherent_alignment(self.rx_history, self.tx_waveform)
        self.plot_rx(coherent_result, f"Coherently Integrated Signal ({len(self.rx_history)} Pulses integrated)")

    def clear_radar(self):
        self.rx_history.clear()
        self.update_plots_empty()

    def plot_rx(self, samples, title_text):
        self.ax_rx.clear()
        self.ax_rx.plot(np.abs(samples), color='red')
        self.ax_rx.set_title(title_text)
        self.ax_rx.grid(True)
        self.canvas.draw()

    def save_rx_data(self):
        if not self.rx_history:
            messagebox.showwarning("Save Error", "No raw capture history available to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".npy", filetypes=[("Numpy Binary", "*.npy")])
        if path:
            np.save(path, self.rx_history[-1])
            messagebox.showinfo("Saved", "Latest raw channel matrix saved successfully.")