import tkinter as tk
from gui_app import PlutoRadarGUI

def main():
    root = tk.Tk()
    # Provide a generous window size for viewing signal graphs clearly
    root.geometry("900x750")
    app = PlutoRadarGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()