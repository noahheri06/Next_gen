import socket
import time
import numpy as np
import matplotlib.pyplot as plt

class OwonVDS:
    def __init__(self, ip_address, port=3000):
        """Initialize the connection to the Owon oscilloscope."""
        self.ip = ip_address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self):
        print(f"Connecting to {self.ip}:{self.port}...")
        self.sock.connect((self.ip, self.port))
        # Query instrument ID to verify connection
        idn = self.query("*IDN?")
        print(f"Connected: {idn}")

    def send_cmd(self, cmd):
        """Send a SCPI command without expecting a response."""
        # The protocol usually expects a newline character at the end of commands
        message = f"{cmd}\n".encode('ascii')
        self.sock.sendall(message)
        time.sleep(0.1) # Brief pause to let the scope process

    def query(self, cmd, buffer_size=4096):
        """Send a SCPI command and return the response."""
        self.send_cmd(cmd)
        data = b""
        while True:
            chunk = self.sock.recv(buffer_size)
            data += chunk
            if len(chunk) < buffer_size:
                break
        return data.decode('ascii').strip()

    def set_capture_params(self, timebase="1ms", memory_depth="1M"):
        """
        Sets the timebase and memory depth. 
        Available memory depths: 1K, 10K, 100K, 1M, 5M, 10M
        Available timebases vary by model, e.g., 500us, 1ms, 2ms, etc.
        """
        print(f"Setting timebase to {timebase} and memory depth to {memory_depth}...")
        self.send_cmd(f":TIMebase:SCALE {timebase}")
        self.send_cmd(f":ACQuire:MDEPth {memory_depth}")
        
        # Verify settings
        actual_tb = self.query(":TIMebase:SCALE?")
        actual_md = self.query(":ACQuire:MDEPth?")
        print(f"Scope reports - Timebase: {actual_tb}, Mem Depth: {actual_md}")

    def read_channel_adc(self, channel="CH1"):
        """
        Reads the comma-separated ADC screen data for a specific channel.
        Returns a numpy array of integers.
        """
        print(f"Fetching ADC data for {channel}...")
        raw_data = self.query(f"*ADC? {channel}", buffer_size=8192)
        
        if not raw_data:
            print("No data received.")
            return np.array([])
            
        # Convert the comma-separated string "50,50,51,52..." into a numpy array
        try:
            str_values = raw_data.split(',')
            # Filter out any empty strings that might occur at the end
            adc_values = np.array([int(val) for val in str_values if val.strip()], dtype=int)
            return adc_values
        except ValueError as e:
            print(f"Error parsing data: {e}")
            return np.array([])
            
    def trigger_remote_deep_memory_dump(self):
        """
        Triggers the scope to dump its full deep memory buffer.
        According to the manual, this saves a 'dm.bin' file to the client directory.
        """
        print("Requesting full Deep Memory dump (dm.bin)...")
        # Note: You may need to handle raw binary socket receiving here if the 
        # scope streams the file directly over this port instead of writing to disk.
        response = self.query("*RDM?")
        print(f"Scope response: {response}")

    def close(self):
        self.sock.close()
        print("Connection closed.")

# --- Execution ---
if __name__ == "__main__":
    # Replace with your scope's actual IP address [cite: 1014]
    SCOPE_IP = "192.168.1.80" 
    
    scope = OwonVDS(SCOPE_IP)
    
    try:
        scope.connect()
        
        # Stop the scope to ensure stable data in the buffer
        scope.send_cmd("*RUNStop")
        
        # Set up for a deep capture
        scope.set_capture_params(timebase="1ms", memory_depth="1M")
        
        # Read standard ADC data for both channels
        ch1_data = scope.read_channel_adc("CH1")
        ch2_data = scope.read_channel_adc("CH2")
        
        print(f"Grabbed {len(ch1_data)} points from CH1.")
        print(f"Grabbed {len(ch2_data)} points from CH2.")
        
        # Optional: Trigger the deep memory binary file transfer if you need millions of points
        # scope.trigger_remote_deep_memory_dump()
        
        # Plot the results
        if len(ch1_data) > 0 or len(ch2_data) > 0:
            plt.figure(figsize=(10, 5))
            if len(ch1_data) > 0:
                plt.plot(ch1_data, label="CH1", color='blue', alpha=0.7)
            if len(ch2_data) > 0:
                plt.plot(ch2_data, label="CH2", color='red', alpha=0.7)
                
            plt.title("Owon VDS ADC Data Capture")
            plt.xlabel("Sample Index")
            plt.ylabel("ADC Value (Raw)")
            plt.legend()
            plt.grid(True)
            
            # Save the figure to disk before displaying to prevent blank output files
            plt.savefig("scope_capture.png", dpi=300, bbox_inches='tight')
            plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Put the scope back into run mode
        scope.send_cmd("*RUNStop")
        scope.close()