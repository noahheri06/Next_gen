import os
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk, messagebox
from scipy.signal.windows import blackman

# ==========================================
# 1. DATA PROCESSING CLASS
# ==========================================
class DataProcessing:
    def __init__(self, data_folder='measurements', num_pulses=20):
        self.data_folder = data_folder
        self.num_pulses = num_pulses
        self.sampling_rate = 5000 / (num_pulses * 1e-3)  # Hz
        self.chirp_bandwidth = 80e6      # Hz
        self.chirp_duration = 1e-3       # Seconds
        self.trigger_threshold = 450     # mV
        self.c = 3e8                     # m/s
        
        self.processed_data = {}

    def _load_oscilloscope_data(self, filepath):
        data_lines = []
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts and parts[0].replace('.', '', 1).replace('-', '', 1).isdigit():
                    data_lines.append(line)
                    
        data = np.loadtxt(data_lines)
        ch1 = data[:, 1]
        ch2 = data[:, 2]
        return ch1 - np.mean(ch1), ch2

    def _extract_pulses(self, ch1, ch2):
        is_pulse = np.abs(ch2) > self.trigger_threshold
        diff = np.diff(np.concatenate(([0], is_pulse.astype(int))))
        trigger_indices = np.where(diff == 1)[0]
        
        if len(trigger_indices) < 2:
            return []

        starts = trigger_indices[:-1]
        ends = trigger_indices[1:]
        
        pulses = []
        for s, e in zip(starts, ends):
            pulses.append(ch1[s:e])
            
        return pulses

    def process_folder(self):
        if not os.path.exists(self.data_folder):
            print(f"Warning: The folder '{self.data_folder}' was not found.")
            return False

        grouped_files = {}
        for filename in os.listdir(self.data_folder):
            if not filename.endswith('.txt'):
                continue
            match = re.match(r"^(.*?)(?:_\d+)?\.txt$", filename)
            basename = match.group(1) if match else filename.replace('.txt', '')
            
            if basename not in grouped_files:
                grouped_files[basename] = []
            grouped_files[basename].append(os.path.join(self.data_folder, filename))

        for basename, filepaths in grouped_files.items():
            all_pulses = []
            
            for fp in filepaths:
                try:
                    ch1, ch2 = self._load_oscilloscope_data(fp)
                    pulses = self._extract_pulses(ch1, ch2)
                    all_pulses.extend(pulses)
                except Exception as e:
                    print(f"Error processing {fp}: {e}")
            
            if not all_pulses:
                continue
                
            min_len = min(len(p) for p in all_pulses)
            aligned_pulses = np.array([p[:min_len] for p in all_pulses])
            coherent_signal = np.mean(aligned_pulses, axis=0)
            
            
            if basename=="through":
                coherent_signal *= 1#1.22#5.3
            
            
            t = np.arange(min_len) / self.sampling_rate
            window = blackman(min_len)
            windowed_signal = coherent_signal * window
            
            nfft = int(2**(3 + np.ceil(np.log2(len(windowed_signal)))))
            fft_result = np.fft.fft(windowed_signal, n=nfft)
            fft_mag = np.abs(fft_result)
            
            freqs = np.fft.fftfreq(nfft, 1 / self.sampling_rate)
            pos_mask = freqs >= 0
            freqs = freqs[pos_mask]
            fft_mag_lin = fft_mag[pos_mask]
            
            fft_mag_db = 20 * np.log10(fft_mag_lin + 1e-12)
            range_axis = (self.c * self.chirp_duration * freqs) / (2 * self.chirp_bandwidth)
            
            self.processed_data[basename] = {
                't': t,
                'coherent_signal': coherent_signal,
                'freqs': freqs,
                'fft_mag_lin': fft_mag_lin,
                'fft_mag_db': fft_mag_db,
                'range_axis': range_axis
            }
            
        return len(self.processed_data) > 0

# ==========================================
# 2. GRAPHICAL USER INTERFACE (GUI)
# ==========================================
class RadarGUI:
    def __init__(self, root, data_processor):
        self.root = root
        self.dp = data_processor
        self.root.title("Advanced FMCW Radar Analyzer")
        self.root.geometry("1400x850")
        
        self.measurements = list(self.dp.processed_data.keys())
        
        self._build_ui()

    def _build_ui(self):
        # --- Left Panel: Controls ---
        control_frame = ttk.Frame(self.root, width=350, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(control_frame, text="1. Select Measurements", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.listbox = tk.Listbox(control_frame, selectmode=tk.MULTIPLE, height=10, exportselection=False)
        for meas in self.measurements:
            self.listbox.insert(tk.END, meas)
        self.listbox.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Plot Selected", command=self.plot_selected).pack(fill=tk.X, pady=5)
        
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        ttk.Label(control_frame, text="2. Background Subtraction", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(control_frame, text="Select Control Measurement:").pack(anchor=tk.W)
        
        self.control_var = tk.StringVar()
        if self.measurements:
            self.control_var.set(self.measurements[0])
            
        self.control_dropdown = ttk.Combobox(control_frame, textvariable=self.control_var, values=self.measurements, state="readonly")
        self.control_dropdown.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Plot Subtracted (Selected - Control)", command=self.plot_subtracted).pack(fill=tk.X, pady=5)

        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # --- Target Information Panel ---
        ttk.Label(control_frame, text="3. Target Information (Highest Peak)", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.info_text = tk.Text(control_frame, height=15, width=40, state=tk.DISABLED, bg="#f0f0f0", font=("Consolas", 10))
        self.info_text.pack(fill=tk.X, pady=5)

        # --- Right Panel: Matplotlib Canvas ---
        plot_frame = ttk.Frame(self.root, padding=10)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 10))
        self.fig.tight_layout(pad=4.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()

    def get_selected_measurements(self):
        indices = self.listbox.curselection()
        return [self.listbox.get(i) for i in indices]

    def _clear_axes(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        self.ax1.set_title("Coherently Added Beat Tone (Time Domain)")
        self.ax1.set_xlabel("Time (ms)")
        self.ax1.set_ylabel("Amplitude")
        self.ax1.grid(True)
        
        self.ax2.set_title("Frequency Spectrum")
        self.ax2.set_xlabel("Frequency (kHz)")
        self.ax2.set_ylabel("Magnitude (dBV)")
        self.ax2.grid(True)
        
        self.ax3.set_title("Radar Range Profile")
        self.ax3.set_xlabel("Range (Meters)")
        self.ax3.set_ylabel("Magnitude (dBV)")
        self.ax3.set_xlim(0, 20)
        self.ax3.grid(True)

    def _update_target_info(self, info_lines):
        """Updates the text box with peak coordinates."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "\n".join(info_lines))
        self.info_text.config(state=tk.DISABLED)

    def plot_selected(self):
        selected = self.get_selected_measurements()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select at least one measurement.")
            return
            
        self._clear_axes()
        info_lines = []
        
        for name in selected:
            data = self.dp.processed_data[name]
            
            # Plot Time Domain
            self.ax1.plot(data['t'] * 1e3, data['coherent_signal'], label=name, alpha=0.8)
            
            # Plot Frequency Domain and capture color
            p = self.ax2.plot(data['freqs'] / 1e3, data['fft_mag_db'], label=name, alpha=0.8)
            line_color = p[0].get_color()
            
            # Plot Range Domain
            self.ax3.plot(data['range_axis'], data['fft_mag_db'], label=name, color=line_color, alpha=0.8)
            
            # --- Peak Detection ---
            peak_idx = np.argmax(data['fft_mag_db'])
            peak_freq = data['freqs'][peak_idx] / 1e3  # kHz
            peak_range = data['range_axis'][peak_idx]  # m
            peak_mag = data['fft_mag_db'][peak_idx]    # dBV
            
            # Plot Vertical Dotted Lines
            self.ax2.axvline(x=peak_freq, color=line_color, linestyle=':', alpha=0.8)
            self.ax3.axvline(x=peak_range, color=line_color, linestyle=':', alpha=0.8)
            
            # Append info for the text box
            info_lines.append(f"[{name}]")
            info_lines.append(f" Range: {peak_range:.3f} m")
            info_lines.append(f" Freq:  {peak_freq:.3f} kHz")
            info_lines.append(f" Mag:   {peak_mag:.2f} dBV")
            info_lines.append("-" * 35)
            
        self._update_target_info(info_lines)
        self.ax1.legend(loc="upper right")
        self.ax2.legend(loc="upper right")
        self.ax3.legend(loc="upper right")
        self.canvas.draw()

    def plot_subtracted(self):
        selected = self.get_selected_measurements()
        control_name = self.control_var.get()
        
        if not selected:
            messagebox.showwarning("Selection Error", "Please select at least one measurement to subtract from.")
            return
        if not control_name:
            return
            
        control_data = self.dp.processed_data[control_name]
        self._clear_axes()
        info_lines = []
        
        for name in selected:
            if name == control_name:
                continue 
                
            data = self.dp.processed_data[name]
            
            sub_mag_lin = np.abs(data['fft_mag_lin']/np.max(data['fft_mag_lin']) - control_data['fft_mag_lin']/np.max(control_data['fft_mag_lin']))
            sub_mag_db = 20 * np.log10(sub_mag_lin + 1e-12)
            sub_signal = data['coherent_signal']/np.max(data['coherent_signal']) - control_data['coherent_signal']/np.max(control_data['coherent_signal'])
            
            label_text = f"{name} - {control_name}"
            
            # Plot Data
            self.ax1.plot(data['t'] * 1e3, sub_signal, label=label_text, alpha=0.8)
            p = self.ax2.plot(data['freqs'] / 1e3, sub_mag_db, label=label_text, alpha=0.8)
            line_color = p[0].get_color()
            self.ax3.plot(data['range_axis'], sub_mag_db, label=label_text, color=line_color, alpha=0.8)
            
            # --- Peak Detection (on the subtracted data) ---
            peak_idx = np.argmax(sub_mag_db)
            peak_freq = data['freqs'][peak_idx] / 1e3  # kHz
            peak_range = data['range_axis'][peak_idx]  # m
            peak_mag = sub_mag_db[peak_idx]            # dBV
            
            # Plot Vertical Dotted Lines
            self.ax2.axvline(x=peak_freq, color=line_color, linestyle=':', alpha=0.8)
            self.ax3.axvline(x=peak_range, color=line_color, linestyle=':', alpha=0.8)
            
            # Append info for the text box
            info_lines.append(f"[{label_text}]")
            info_lines.append(f" Range: {peak_range:.3f} m")
            info_lines.append(f" Freq:  {peak_freq:.3f} kHz")
            info_lines.append(f" Mag:   {peak_mag:.2f} dBV")
            info_lines.append("-" * 35)
            
        self._update_target_info(info_lines)
        self.ax1.legend(loc="upper right")
        self.ax2.legend(loc="upper right")
        self.ax3.legend(loc="upper right")
        self.canvas.draw()

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    processor = DataProcessing(data_folder='measurements', num_pulses=20)
    
    print("Reading and processing radar data...")
    success = processor.process_folder()
    
    if success:
        root = tk.Tk()
        app = RadarGUI(root, processor)
        root.mainloop()
    else:
        print("Could not start GUI. No valid data found in the 'measurements' folder.")