from datetime import datetime
import csv
import os

def start_logging(self):
    """
    create a new logfile for new sensor values
    """
    print("start logging")
    self.is_logging = True
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    self.current_log_filename = f"log_{timestamp}.csv"
    filepath = os.path.join("logs", self.current_log_filename)
    self.log_file = open(filepath, "w", newline="")
    self.writer = csv.writer(self.log_file)
    self.writer.writerow(["Time", "Pressure", "Current"])


def end_logging(self):
    """
    finish the logging and close the logfile
    """
    print("end logging")
    self.is_logging = False
    if self.log_file:
        self.log_file.close()