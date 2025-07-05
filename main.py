import sys
from time import sleep
from threading import Thread
from gui.main_window import NewMainWindow
from PySide6.QtWidgets import QApplication
import queue
from random import randint

def start_main_window(pressure_sensor_queue, current_sensor_queue,
                      thermocouples_sensor_queue, load_cell_sensor_queue,
                      differential_sensor_queue):
    """
    Start the main UI window
    """
    app = QApplication(sys.argv)
    main_window = NewMainWindow(pressure_sensor_queue, current_sensor_queue,
                                thermocouples_sensor_queue, load_cell_sensor_queue,
                                differential_sensor_queue)
    main_window.show()
    sys.exit(app.exec())

def start_data_handling(pressure_sensor_queue, current_sensor_queue,
                        thermocouples_sensor_queue, load_cell_sensor_queue,
                        differential_sensor_queue):
    """
    This function starts the data handling process.
    """
    while True:
        print("adding new value to queue")
        # simulate sensor values for testing
        pressure_sensor_queue.put(randint(0, 100))
        current_sensor_queue.put(randint(0, 100))
        thermocouples_sensor_queue.put(randint(0, 100))
        load_cell_sensor_queue.put(randint(0, 100))
        differential_sensor_queue.put(randint(0, 100))
        sleep(1)


if __name__ == "__main__":
    # define shared queue between threads to communicate sensor values
    pressure_sensor_queue = queue.Queue()
    current_sensor_queue = queue.Queue()
    thermocouples_sensor_queue = queue.Queue()
    load_cell_sensor_queue = queue.Queue()
    differential_pressure_queue = queue.Queue()

    # start multithreaded environment to separate UI from data handling
    main_window_thread = Thread(target=start_main_window,
                                args=(pressure_sensor_queue,
                                      current_sensor_queue,
                                      thermocouples_sensor_queue,
                                      load_cell_sensor_queue,
                                      differential_pressure_queue))

    data_handling_thread = Thread(target=start_data_handling,
                                  args=(pressure_sensor_queue,
                                        current_sensor_queue,
                                        thermocouples_sensor_queue,
                                        load_cell_sensor_queue,
                                        differential_pressure_queue))
    main_window_thread.start()
    data_handling_thread.start()

    # @TODO stop data thread if UI thread is stopped
    # join the threads again
    main_window_thread.join()
    #data_handling_thread.join()

