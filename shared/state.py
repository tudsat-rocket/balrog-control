import threading
from queue import Queue

# Last known values
telemetry = {}
telemetry_lock = threading.Lock()

# Data for disk/sqlite
disk_queue = Queue()