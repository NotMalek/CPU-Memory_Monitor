import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import logging
from core.monitor import SystemMonitor
from storage.repository import MetricsRepository
import seaborn as sns
from matplotlib.gridspec import GridSpec
import numpy as np

class Dashboard:
    def __init__(self, monitor: SystemMonitor, repository: MetricsRepository):
        logging.info("Initializing Dashboard...")
        self.monitor = monitor
        self.repository = repository
        self.root = None
        self.figures = {}
        self.canvases = {}

        # Initialize data buffers
        self.cpu_data = []
        self.mem_data = []
        self.net_recv_data = []
        self.net_send_data = []
        self.timestamps = []
        self.max_points = 50

        self._setup_gui()
        self._setup_styles()
        logging.info("Dashboard initialization complete.")

    def _setup_styles(self):
        sns.set_theme(style="darkgrid")
        plt.style.use('dark_background')

    def _setup_gui(self):
        self.root = tk.Tk()
        self.root.title("System Performance Monitor")
        self.root.state('zoomed')

        # Create main figure for overview plots
        fig = Figure(figsize=(12, 8), facecolor='#2F2F2F')
        gs = GridSpec(2, 2, figure=fig)
        plt.subplots_adjust(hspace=0.3)

        # CPU Usage
        ax_cpu = fig.add_subplot(gs[0, 0])
        ax_cpu.set_title('CPU Usage (%)', color='white')
        ax_cpu.set_ylim(0, 100)
        ax_cpu.set_facecolor('#1F1F1F')
        ax_cpu.tick_params(colors='white')
        ax_cpu.grid(True)

        # Memory Usage
        ax_mem = fig.add_subplot(gs[0, 1])
        ax_mem.set_title('Memory Usage (%)', color='white')
        ax_mem.set_ylim(0, 100)
        ax_mem.set_facecolor('#1F1F1F')
        ax_mem.tick_params(colors='white')
        ax_mem.grid(True)

        # Network Usage
        ax_net = fig.add_subplot(gs[1, 0])
        ax_net.set_title('Network Usage (MB/s)', color='white')
        ax_net.set_facecolor('#1F1F1F')
        ax_net.tick_params(colors='white')
        ax_net.grid(True)

        # Disk Usage (Pie Chart)
        ax_disk = fig.add_subplot(gs[1, 1])
        ax_disk.set_title('Disk Usage', color='white')
        ax_disk.set_facecolor('#1F1F1F')
        ax_disk.tick_params(colors='white')

        fig.tight_layout()

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figures['overview'] = fig
        self.canvases['overview'] = canvas

    async def _update_plots(self, metrics):
        try:
            # Update data buffers
            self.cpu_data.append(metrics.cpu_percent)
            self.mem_data.append(metrics.memory_percent)
            self.net_recv_data.append(metrics.network_recv)
            self.net_send_data.append(metrics.network_sent)
            self.timestamps.append(len(self.timestamps))

            # Keep only last max_points
            if len(self.cpu_data) > self.max_points:
                self.cpu_data.pop(0)
                self.mem_data.pop(0)
                self.net_recv_data.pop(0)
                self.net_send_data.pop(0)
                self.timestamps.pop(0)

            # Get figure axes
            ax_cpu = self.figures['overview'].axes[0]
            ax_mem = self.figures['overview'].axes[1]
            ax_net = self.figures['overview'].axes[2]
            ax_disk = self.figures['overview'].axes[3]

            # Clear previous plots
            ax_cpu.clear()
            ax_mem.clear()
            ax_net.clear()
            ax_disk.clear()

            # Plot CPU Usage
            ax_cpu.plot(self.timestamps, self.cpu_data, 'r-', label='CPU Usage')
            ax_cpu.set_ylim(0, 100)
            ax_cpu.set_title(f'CPU Usage: {metrics.cpu_percent:.1f}%', color='white')
            ax_cpu.grid(True)
            ax_cpu.legend()
            ax_cpu.set_facecolor('#1F1F1F')
            ax_cpu.tick_params(colors='white')

            # Plot Memory Usage
            ax_mem.plot(self.timestamps, self.mem_data, 'b-', label='Memory Usage')
            ax_mem.set_ylim(0, 100)
            ax_mem.set_title(f'Memory Usage: {metrics.memory_percent:.1f}%', color='white')
            ax_mem.grid(True)
            ax_mem.legend()
            ax_mem.set_facecolor('#1F1F1F')
            ax_mem.tick_params(colors='white')

            # Plot Network Usage
            ax_net.plot(self.timestamps, self.net_recv_data, 'g-', label='Download', linewidth=2)
            ax_net.plot(self.timestamps, self.net_send_data, '#FF00FF', label='Upload', linewidth=2)

            max_net = max(max(self.net_recv_data or [0]), max(self.net_send_data or [0]))
            y_limit = max(1, min(max_net * 1.2, 100))

            ax_net.set_ylim(0, y_limit)
            ax_net.set_title(f'Network (MB/s) - ↑{metrics.network_sent:.1f} ↓{metrics.network_recv:.1f}', color='white')
            ax_net.grid(True, alpha=0.3)
            ax_net.legend(loc='upper right')
            ax_net.set_facecolor('#1F1F1F')
            ax_net.tick_params(colors='white')

            # Update Disk Usage (Pie Chart)
            disk_labels = ['Used', 'Free']
            disk_values = [metrics.disk_percent, 100 - metrics.disk_percent]
            colors = ['#4CAF50', '#2196F3']  # Green for used, Blue for free
            ax_disk.pie(disk_values, labels=disk_labels, colors=colors, autopct='%1.1f%%')
            ax_disk.set_title(f'Disk Usage', color='white')
            ax_disk.set_facecolor('#1F1F1F')

            # Adjust layout
            self.figures['overview'].tight_layout()

            # Update canvas
            self.canvases['overview'].draw()

        except Exception as e:
            logging.error(f"Error updating plots: {str(e)}")

    def run(self):
        """Run the main GUI loop"""
        self.root.mainloop()