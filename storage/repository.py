import sqlite3
import logging
import aiosqlite
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

class MetricsRepository:
    """Repository for storing and retrieving system metrics"""

    def __init__(self, db_path: str = "metrics.db"):
        """Initialize the repository with database path"""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Drop existing tables if they exist
                conn.execute("DROP TABLE IF EXISTS metrics")
                conn.execute("DROP INDEX IF EXISTS idx_metrics_timestamp")

                # Create metrics table with only essential metrics
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        cpu_percent REAL NOT NULL,
                        memory_percent REAL NOT NULL,
                        disk_percent REAL NOT NULL,
                        network_sent REAL NOT NULL,
                        network_recv REAL NOT NULL
                    )
                """)

                # Create index for better query performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)")
                conn.commit()
                logging.info("Database initialized successfully")

        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
            raise

    @asynccontextmanager
    async def _get_db(self):
        """Async context manager for database connections"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            yield db

    async def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to database"""
        async with self._get_db() as db:
            await db.execute("""
                INSERT INTO metrics (
                    timestamp, cpu_percent, memory_percent, disk_percent,
                    network_sent, network_recv
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(),
                metrics['cpu_percent'],
                metrics['memory_percent'],
                metrics['disk_percent'],
                metrics['network_sent'],
                metrics['network_recv']
            ))
            await db.commit()
            logging.debug("Metrics saved successfully")

    async def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """Get the most recent metrics"""
        async with self._get_db() as db:
            async with db.execute("""
                SELECT * FROM metrics 
                ORDER BY timestamp DESC LIMIT 1
            """) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None