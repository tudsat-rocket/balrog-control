import sys
import queue

from time import sleep
from threading import Thread, Event
from control.controller import Controller
from gui.main_window import NewMainWindow
from PySide6.QtWidgets import QApplication
from random import randint


def start_data_handling(pressure_sensor_queue, current_sensor_queue,
                        thermocouples_sensor_queue, load_cell_sensor_queue,
                        differential_sensor_queue, thread_killer):
    """
    This function starts the data handling process.
    """
    while not thread_killer.is_set():
        print("adding new value to queue")
        # simulate sensor values for testing
        pressure_sensor_queue.put(randint(0, 100))
        current_sensor_queue.put(randint(0, 100))
        thermocouples_sensor_queue.put(randint(0, 100))
        load_cell_sensor_queue.put(randint(0, 100))
        differential_sensor_queue.put(randint(0, 100))
        sleep(1)

    print("Exiting data handling thread")


if __name__ == "__main__":
    # define shared queue between threads to communicate sensor values
    thread_killer = Event()
    pressure_sensor_queue = queue.Queue()
    current_sensor_queue = queue.Queue()
    thermocouples_sensor_queue = queue.Queue()
    load_cell_sensor_queue = queue.Queue()
    differential_pressure_queue = queue.Queue()

    # start multithreaded environment to separate UI from data handling


    data_handling_thread = Thread(target=start_data_handling,
                                  args=(pressure_sensor_queue,
                                        current_sensor_queue,
                                        thermocouples_sensor_queue,
                                        load_cell_sensor_queue,
                                        differential_pressure_queue, thread_killer))

    controller = Controller()

    data_handling_thread.start()

    """
    Start the main UI window
    """
    app = QApplication(sys.argv)
    main_window = NewMainWindow(pressure_sensor_queue, current_sensor_queue,
                                thermocouples_sensor_queue, load_cell_sensor_queue,
                                differential_pressure_queue, controller)
    main_window.show()
    rc = app.exec()


    # @TODO stop data thread if UI thread is stopped
    # join the threads again
    thread_killer.set()
    data_handling_thread.join(timeout=5)
    sys.exit(rc)
