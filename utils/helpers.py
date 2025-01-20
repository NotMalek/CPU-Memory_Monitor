from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

def format_bytes(bytes: float, decimal_places: int = 2) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.{decimal_places}f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.{decimal_places}f} PB"

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def calculate_rate(current: float, previous: float, time_delta: timedelta) -> float:
    """Calculate rate of change"""
    if time_delta.total_seconds() == 0:
        return 0.0
    return (current - previous) / time_delta.total_seconds()

def moving_average(data: List[float], window: int = 5) -> List[float]:
    """Calculate moving average of a data series"""
    if not data:
        return []

    result = []
    for i in range(len(data)):
        start_idx = max(0, i - window + 1)
        window_data = data[start_idx:i + 1]
        average = sum(window_data) / len(window_data)
        result.append(average)
    return result

def save_json_data(data: Dict[str, Any], filepath: Path) -> None:
    """Save data to JSON file with error handling"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        logging.error(f"Error saving JSON data: {str(e)}")
        raise

def load_json_data(filepath: Path) -> Optional[Dict[str, Any]]:
    """Load data from JSON file with error handling"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON data: {str(e)}")
        return None

def validate_metrics_data(data: Dict[str, Any]) -> bool:
    """Validate metrics data structure"""
    required_fields = {
        'timestamp',
        'cpu_percent',
        'memory_percent',
        'disk_percent',
        'network_sent',
        'network_recv'
    }

    return all(field in data for field in required_fields)

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hours"
    else:
        days = seconds // 86400
        return f"{days} days"

def get_threshold_color(value: float, warning: float, critical: float) -> str:
    """Get color code based on threshold values"""
    if value >= critical:
        return '#FF4444'  # Red
    elif value >= warning:
        return '#FFAA00'  # Orange
    return '#44FF44'  # Green

class DataBuffer:
    """Circular buffer for storing time-series data"""
    def __init__(self, max_size: int = 3600):
        self.max_size = max_size
        self.buffer: List[Any] = []

    def add(self, item: Any) -> None:
        """Add item to buffer, maintaining max size"""
        self.buffer.append(item)
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)

    def get_all(self) -> List[Any]:
        """Get all items in buffer"""
        return self.buffer.copy()

    def get_last_n(self, n: int) -> List[Any]:
        """Get last n items from buffer"""
        return self.buffer[-n:]

    def clear(self) -> None:
        """Clear the buffer"""
        self.buffer.clear()

def parse_time_range(time_range: str) -> timedelta:
    """Parse time range string to timedelta"""
    try:
        value = int(time_range[:-1])
        unit = time_range[-1].lower()

        if unit == 'h':
            return timedelta(hours=value)
        elif unit == 'd':
            return timedelta(days=value)
        elif unit == 'w':
            return timedelta(weeks=value)
        else:
            raise ValueError(f"Invalid time unit: {unit}")
    except Exception as e:
        logging.error(f"Error parsing time range: {str(e)}")
        return timedelta(hours=1)  # Default to 1 hour