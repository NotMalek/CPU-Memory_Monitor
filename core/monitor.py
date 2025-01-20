from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import psutil
import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from abc import ABC, abstractmethod
from queue import Queue
import asyncio
from storage.repository import MetricsRepository

@dataclass
class SystemMetrics:
    """Data class for storing system metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: float
    network_recv: float

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'disk_percent': self.disk_percent,
            'network_sent': self.network_sent,
            'network_recv': self.network_recv
        }

class MetricsCollector:
    """Base class for collecting system metrics"""
    def __init__(self):
        self._lock = Lock()
        self._last_network = (0, 0)
        self._last_network_time = datetime.now()
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def collect(self) -> SystemMetrics:
        """Collect all system metrics"""
        try:
            cpu_percent = await self._get_cpu_usage()
            memory = await self._get_memory_usage()
            disk = await self._get_disk_usage()
            network = await self._get_network_usage()

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_sent=network[0],
                network_recv=network[1]
            )
        except Exception as e:
            logging.error(f"Error collecting metrics: {str(e)}")
            raise

    async def _get_cpu_usage(self) -> float:
        """Get CPU usage with improved accuracy"""
        loop = asyncio.get_event_loop()
        try:
            cpu_percentages = await loop.run_in_executor(
                self._executor,
                lambda: psutil.cpu_percent(interval=0.5, percpu=True)
            )

            if not cpu_percentages:
                return 0.0

            return max(
                sum(cpu_percentages) / len(cpu_percentages),
                max(cpu_percentages)
            )
        except Exception as e:
            logging.error(f"Error getting CPU usage: {str(e)}")
            return 0.0

    async def _get_memory_usage(self):
        """Get memory usage stats"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            psutil.virtual_memory
        )

    async def _get_disk_usage(self):
        """Get disk usage stats"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: psutil.disk_usage('/')
        )

    async def _get_network_usage(self) -> Tuple[float, float]:
        """Calculate network throughput in MB/s with improved accuracy"""
        try:
            current_network = psutil.net_io_counters()
            current_time = datetime.now()

            with self._lock:
                time_delta = (current_time - self._last_network_time).total_seconds()
                if time_delta > 0:
                    sent_speed = max(0, (current_network.bytes_sent - self._last_network[0]) / time_delta / 1024 / 1024)
                    recv_speed = max(0, (current_network.bytes_recv - self._last_network[1]) / time_delta / 1024 / 1024)

                    sent_speed = min(sent_speed, 100)
                    recv_speed = min(recv_speed, 100)
                else:
                    sent_speed = recv_speed = 0.0

                self._last_network = (current_network.bytes_sent, current_network.bytes_recv)
                self._last_network_time = current_time

                return sent_speed, recv_speed
        except Exception as e:
            logging.error(f"Error calculating network usage: {str(e)}")
            return 0.0, 0.0

class MetricsBuffer:
    """Buffer for storing historical metrics"""
    def __init__(self, max_size: int = 3600):  # 1 hour of data at 1s intervals
        self.max_size = max_size
        self._buffer: List[SystemMetrics] = []
        self._lock = Lock()

    def add(self, metrics: SystemMetrics) -> None:
        """Add metrics to buffer"""
        with self._lock:
            self._buffer.append(metrics)
            if len(self._buffer) > self.max_size:
                self._buffer.pop(0)

    def get_last_n(self, n: int) -> List[SystemMetrics]:
        """Get last n metrics"""
        with self._lock:
            return self._buffer[-n:]

class Alert(ABC):
    """Base class for system alerts"""
    @abstractmethod
    def check(self, metrics: SystemMetrics) -> Optional[str]:
        pass

class HighCPUAlert(Alert):
    def __init__(self, threshold: float = 80.0):
        self.threshold = threshold

    def check(self, metrics: SystemMetrics) -> Optional[str]:
        if metrics.cpu_percent > self.threshold:
            return f"High CPU usage: {metrics.cpu_percent:.1f}%"
        return None

class AlertManager:
    """Manages system alerts"""
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_queue: Queue = Queue()
        self._setup_default_alerts()

    def _setup_default_alerts(self):
        self.add_alert(HighCPUAlert())

    def add_alert(self, alert: Alert) -> None:
        self.alerts.append(alert)

    def check_alerts(self, metrics: SystemMetrics) -> None:
        for alert in self.alerts:
            message = alert.check(metrics)
            if message:
                self.alert_queue.put((datetime.now(), message))

class SystemMonitor:
    """Main system monitoring class"""
    def __init__(self, repository: Optional[MetricsRepository] = None):
        self.metrics_collector = MetricsCollector()
        self.metrics_buffer = MetricsBuffer()
        self.alert_manager = AlertManager()
        self.repository = repository
        self.running = False
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._collection_lock = Lock()

    async def start(self):
        """Start monitoring system"""
        self.running = True

        while self.running:
            try:
                # Collect metrics
                metrics = await self.metrics_collector.collect()

                # Store in buffer
                self.metrics_buffer.add(metrics)

                # Check alerts
                self.alert_manager.check_alerts(metrics)

                # Save to database if repository is available
                if self.repository:
                    await self.repository.save_metrics(metrics.to_dict())

                    # Save any new alerts
                    alerts = self.get_alerts()
                    for timestamp, message in alerts:
                        await self.repository.save_alert(
                            alert_type="system",
                            message=message,
                            severity="warning"
                        )

                await asyncio.sleep(1)  # Collect metrics every second

            except Exception as e:
                logging.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    def stop(self):
        """Stop monitoring system"""
        self.running = False
        self._executor.shutdown(wait=True)

    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get most recent metrics"""
        last_metrics = self.metrics_buffer.get_last_n(1)
        return last_metrics[0] if last_metrics else None

    def get_metrics_history(self, seconds: int) -> List[SystemMetrics]:
        """Get historical metrics"""
        return self.metrics_buffer.get_last_n(seconds)

    def get_alerts(self) -> List[Tuple[datetime, str]]:
        """Get pending alerts"""
        alerts = []
        while not self.alert_manager.alert_queue.empty():
            alerts.append(self.alert_manager.alert_queue.get())
        return alerts