# Advanced System Performance Monitor

A sophisticated, enterprise-grade system monitoring application built with Python, featuring real-time metrics collection, data persistence, alerting, and visualization capabilities.

## Project Structure
```
system_monitor/
├── README.md
├── requirements.txt
├── main.py
├── core/
│   ├── __init__.py
│   └── monitor.py
├── storage/
│   ├── __init__.py
│   └── repository.py
├── ui/
│   ├── __init__.py
│   └── dashboard.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

## Features

### Core Monitoring
- Real-time CPU usage monitoring (per core)
- Memory utilization tracking
- Disk usage analytics
- Network throughput measurement (upload/download)
- CPU temperature monitoring
- Process count tracking
- Battery level monitoring (for laptops)
- Swap memory usage

### Advanced Capabilities
- **Asynchronous Operations**: Built with `asyncio` for efficient concurrent operations
- **Multi-threaded Data Collection**: Parallel metric collection using ThreadPoolExecutor
- **Data Persistence**: SQLite database with async operations via `aiosqlite`
- **Clean Architecture**: Follows SOLID principles and clean architecture patterns
- **Real-time Alerting**: Configurable alert thresholds with queue-based notification system
- **Data Aggregation**: Historical data analysis with customizable time windows
- **Export Capabilities**: Data export to JSON format
- **Robust Error Handling**: Comprehensive logging and error management

## Technical Requirements

- Python 3.9+
- Dependencies (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/system-monitor.git
cd system-monitor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Run the application:
```bash
python main.py
```

2. The GUI dashboard will open automatically, showing:
    - Real-time system metrics
    - Historical data graphs
    - Active alerts
    - System information
