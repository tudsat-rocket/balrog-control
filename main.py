import os.path
import csv

from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QLabel, QApplication, QWidget, QGridLayout, QLineEdit, QFrame, QPushButton, QVBoxLayout, QGroupBox
from PySide6.QtCore import QTimer
import sys
import pyqtgraph as pg
from datetime import datetime

class MainWindow(QMainWindow):
    """
    Main window of GUI
    """
    def __init__(self):
        super().__init__()

        self.is_logging = False
        self.current_log_filename = None
        self.log_file = None
        self.writer = None

        self.pressure_data = []
        self.current_data = []
        self.time_data = []

        # start with the gui widgets
        self.setWindowTitle("Balrog Control")
        self.setStyleSheet("QLabel {color: #FFFFFF;} QGroupBox {color: #FFFFFF;}")
        self.setGeometry(100,100,1000,500)
        self.centralWidget = QWidget()
        self.centralWidget.setObjectName("centralWidget")
        self.centralWidget.setStyleSheet("#centralWidget { background-color: #444444}")
        self.setCentralWidget(self.centralWidget)

        # define main layout as horizontal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # controller side
        controller_vlayout = QVBoxLayout()
        controller_layout = QGridLayout()

        self.start_logging_pb = QPushButton("Start Logging")
        self.start_logging_pb.clicked.connect(self.start_logging)
        self.end_logging_pb = QPushButton("End Logging")
        self.end_logging_pb.clicked.connect(self.end_logging)

        # live data labels
        self.time_label = QLabel("Time: ")
        self.time_data_label = QLabel("-")
        self.time_data_unit = QLabel("ms")
        self.pressure_label = QLabel("Pressure: ")

        self.pressure_data_label = QLabel("-")
        self.pressure_data_unit = QLabel("?")
        self.current_label = QLabel("Current: ")
        self.current_data_label = QLabel("-")
        self.current_data_unit = QLabel("?")

        controller_layout.addWidget(self.start_logging_pb, 4, 0)
        controller_layout.addWidget(self.end_logging_pb, 4, 1)

        live_data_label = QLabel("Live Data:")
        live_data_label.setStyleSheet("font-weight: bold; ")
        controller_layout.addWidget(live_data_label, 9, 0)
        controller_layout.addWidget(self.time_label, 10, 0)
        controller_layout.addWidget(self.time_data_label, 10, 1)
        controller_layout.addWidget(self.time_data_unit, 10, 2)
        controller_layout.addWidget(self.pressure_label, 11, 0)
        controller_layout.addWidget(self.pressure_data_label, 11, 1)
        controller_layout.addWidget(self.pressure_data_unit, 11, 2)
        controller_layout.addWidget(self.current_label, 12, 0)
        controller_layout.addWidget(self.current_data_label, 12, 1)
        controller_layout.addWidget(self.current_data_unit, 12, 2)

        controller_vlayout.addLayout(controller_layout)
        controller_vlayout.addStretch(0)

        # vertical line
        vline = QFrame()
        vline.setFrameShape(QFrame.VLine)
        vline.setFrameShadow(QFrame.Plain)
        vline.setLineWidth(1)
        vline.setStyleSheet("color: #FFFFFF")

        figure_group_box = QGroupBox("Live Serial Controller Data")
        figure_group_layout = QVBoxLayout()
        figure_group_layout.setContentsMargins(10, 10, 10, 10)


        # global coloring configuration for GraphicsLayoutWidget
        pg.setConfigOption('background', '#444444')
        pg.setConfigOption('foreground', 'w')

        self.plot_layout_widget = pg.GraphicsLayoutWidget()



        # create new pressure graph with plotwidget
        self.pressure_graph_widget = self.plot_layout_widget.addPlot()
        self.pressure_graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.pressure_graph_widget.setLabel('bottom', 'Time (ms)', color='#FFFFFF')

        self.pressure_graph_widget.setLabel('left', 'pressure', color='#FFFFFF')

        # create pressure graph line (curve)
        self.pressure_curve = self.pressure_graph_widget.plot([], [], pen=pg.mkPen(color="r", width=2))


        # create new current graph with plotwidget
        self.plot_layout_widget.nextRow()
        self.current_graph_widget = self.plot_layout_widget.addPlot()
        self.current_graph_widget.showGrid(x=True, y=True, alpha=0.3)

        self.current_graph_widget.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.current_graph_widget.setLabel('left', 'Current', color='#FFFFFF')

        # create graph line (curve)
        self.current_graph_curve = self.current_graph_widget.plot([], [], pen=pg.mkPen(color="r", width=2))

        # fill in figure layout
        figure_group_layout.addWidget(self.plot_layout_widget)
        figure_group_box.setLayout(figure_group_layout)

        # fill in main layout
        main_layout.addLayout(controller_vlayout)
        main_layout.addWidget(vline)
        main_layout.addWidget(figure_group_box)

        # Define Layout
        self.centralWidget.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(200)


    def start_logging(self):

        print("start logging")
        self.is_logging = True
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.current_log_filename = f"log_{timestamp}.csv"
        filepath = os.path.join("logs", self.current_log_filename)
        self.log_file = open(filepath, "w", newline="")
        self.writer = csv.writer(self.log_file)

        self.writer.writerow(["Time", "Pressure", "Current"])


    def end_logging(self):
        print("end logging")
        self.is_logging = False
        if self.log_file:
            self.log_file.close()


    def update_plots(self):
        view_buffer = 500
        if len(self.time_data) < 1:
            return

        if len(self.time_data) > 1:
            self.pressure_curve.setData(self.time_data, self.pressure_data)
            self.current_graph_curve.setData(self.time_data, self.current_data)

            # print value that is last in the list to the label
            self.pressure_data_label.setText(str(self.pressure_data[-1]))

            self.time_data_label.setText(str(self.time_data[-1]))
            self.current_data_label.setText(str(self.current_data[-1]))
        if len(self.time_data) > view_buffer:

            self.current_graph_widget.setXRange(self.time_data[-view_buffer], self.time_data[-1])
            self.pressure_graph_widget.setXRange(self.time_data[-view_buffer], self.time_data[-1])


def start_main_window():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    start_main_window()
