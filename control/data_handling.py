import sqlite3
from queue import Empty, Queue
from threading import Event



class TelemetryLogger:
    def __init__(self, db_path: str = "test_run.db"):
        self.db_path = db_path
        self.batch_size = 200  # Schreibt ca. 10x pro Sekunde bei 2000 Pkt/s
        self._prepare_db()

    def _prepare_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Vertical Table Format
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS sensor_data
                       (
                           timestamp
                           REAL,
                           sensor_name
                           TEXT,
                           value
                           REAL
                       )
                       """)
        # Index für schnelle spätere Analyse (z.B. in Grafana oder Excel)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ts ON sensor_data (timestamp)")

        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        conn.commit()
        conn.close()

    def run(self, disk_queue: Queue, stop_event: Event):
        """Worker-Loop für den Thread."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA journal_mode=WAL")
        batch_buffer = []

        while not stop_event.is_set() or not disk_queue.empty():
            try:
                #(name, ts, val)
                data = disk_queue.get(timeout=0.2)

                #(ts, name, val)
                batch_buffer.append((data[1], data[0], data[2]))

                if len(batch_buffer) >= self.batch_size:
                    cursor.executemany(
                        "INSERT INTO sensor_data VALUES (?, ?, ?)",
                        batch_buffer
                    )
                    conn.commit()
                    batch_buffer = []

            except Empty:
                if batch_buffer:
                    cursor.executemany("INSERT INTO sensor_data VALUES (?, ?, ?)", batch_buffer)
                    conn.commit()
                    batch_buffer = []
                continue

        if batch_buffer:
            cursor.executemany("INSERT INTO sensor_data VALUES (?, ?, ?)", batch_buffer)
            conn.commit()

        conn.close()
        print("DB worker shut down safely.")