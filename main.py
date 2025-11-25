import sys
from queue import Queue
from threading import Event, Thread
from time import sleep

from PySide6.QtWidgets import QApplication

from control.controller import Controller
from control.data_handling import DataHandler
from gui.main_window import NewMainWindow


def data_handler(thread_killer, connected_signal) -> None:
    """Handle the sensor data thread, store latest data in CSV.

    This calls a long as the thread_killer flag is not set,
    the save method to store the latest sensor values
    in the csv file.
    """
    handler = DataHandler()
    connected_signal.wait()
    while not thread_killer.is_set():
        # store the latest data in CSV
        connected_signal.wait()
        handler.save()
        sleep(0.1)  # @todo


if __name__ == "__main__":
    # define shared queue between threads to communicate sensor values
    thread_killer = Event()
    abort_signal = Event()
    run_signal = Event()
    connected_signal = Event()

    event_queue: Queue = Queue()

    # start multithreaded environment to separate UI from data handling

    controller = Controller(
        event_queue, thread_killer, abort_signal, run_signal, connected_signal
    )

    data_handler = Thread(target=data_handler, args=(thread_killer, connected_signal))
    data_handler.start()

    """
    Start the main UI window
    """
    app = QApplication(sys.argv)
    main_window = NewMainWindow(event_queue, controller)
    main_window.show()
    rc = app.exec()

    # join the threads again
    thread_killer.set()
    data_handler.join(timeout=1)
    sys.exit(rc)
