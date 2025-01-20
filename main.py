import asyncio
import logging
from ui.dashboard import Dashboard
from core.monitor import SystemMonitor
from storage.repository import MetricsRepository
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler()
    ]
)

async def update_gui(dashboard: Dashboard, monitor: SystemMonitor):
    """Update GUI periodically"""
    while True:
        try:
            metrics = monitor.get_current_metrics()
            if metrics:
                await dashboard._update_plots(metrics)
            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Error updating GUI: {str(e)}")
            await asyncio.sleep(1)

def run_async_loop(async_loop):
    """Run the asyncio event loop"""
    asyncio.set_event_loop(async_loop)
    async_loop.run_forever()

def main():
    try:
        # Initialize repository
        repository = MetricsRepository()

        # Initialize monitor with repository
        monitor = SystemMonitor(repository=repository)

        # Initialize dashboard
        dashboard = Dashboard(monitor, repository)

        # Create new event loop for async operations
        async_loop = asyncio.new_event_loop()

        # Start monitor in the async loop
        async_loop.create_task(monitor.start())

        # Start GUI updates in the async loop
        async_loop.create_task(update_gui(dashboard, monitor))

        # Run async loop in a separate thread
        thread = threading.Thread(target=run_async_loop, args=(async_loop,), daemon=True)
        thread.start()

        # Start Tkinter main loop in the main thread
        dashboard.root.mainloop()

    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
    finally:
        if 'monitor' in locals():
            monitor.stop()

if __name__ == "__main__":
    main()