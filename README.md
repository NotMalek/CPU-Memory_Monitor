# System Performance Monitor

A lightweight, real-time system monitoring application built with Python, featuring core system metrics visualization and data persistence.

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
- Real-time CPU usage monitoring
- Memory utilization tracking
- Disk usage visualization with pie chart
- Network throughput measurement (upload/download)

### Technical Features
- **Asynchronous Operations**: Built with `asyncio` for efficient real-time monitoring
- **Multi-threaded Data Collection**: Parallel metric collection using ThreadPoolExecutor
- **Data Persistence**: SQLite database with async operations via `aiosqlite`
- **Modern UI**: Clean and responsive interface with matplotlib-based visualizations
- **Error Handling**: Comprehensive logging system

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

2. The GUI dashboard will display:
   - CPU usage over time
   - Memory utilization graph
   - Network throughput metrics
   - Disk usage pie chart

## Data Visualization

The dashboard provides real-time visualizations of:
- CPU usage with historical trending
- Memory utilization patterns
- Network upload/download speeds
- Disk space distribution in pie chart format

All graphs automatically update every second to provide current system metrics.