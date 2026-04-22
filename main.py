import sys
from queue import Queue
from threading import Event, Thread
from time import sleep

from PySide6.QtWidgets import QApplication

from control.controller import Controller
from gui.main_window import NewMainWindow

if __name__ == "__main__":
    # define shared queue between threads to communicate Events
    # TODO Hier oder in Shared? Dependency Injektion vs Singelton/Global-state
    thread_killer = Event()
    abort_signal = Event()
    run_signal = Event()
    connected_signal = Event()

    event_queue: Queue = Queue()

    # start multithreaded environment to separate UI from Controller

    controller = Controller(
        event_queue, thread_killer, abort_signal, run_signal, connected_signal
    )

    """
    Start the main UI window
    """
    app = QApplication(sys.argv)
    main_window = NewMainWindow(event_queue, controller)
    main_window.show()
    rc = app.exec()

    # join the threads again
    thread_killer.set()
    controller.stop()
    sys.exit(rc)
