from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox, QGroupBox, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
import serial
import serial.tools.list_ports

class Switch(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = "Entrenamiento" if self.isChecked() else "Evaluación"
        bg_color = Qt.green if self.isChecked() else Qt.red

        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(bg_color))

        painter.drawRect(0, 0, self.width(), self.height())
        painter.setBrush(QColor("#ffffff"))
        painter.drawRect(13 if self.isChecked() else 1, 1, 28, 28)
        painter.drawText(24 if self.isChecked() else 38, 20, label)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.ser = None

        self.device_combobox = QComboBox()
        self.device_combobox.addItems([port.device for port in serial.tools.list_ports.comports()])

        self.baudrate_combobox = QComboBox()
        self.baudrate_combobox.addItems(['9600', '14400', '19200', '38400', '57600', '115200'])

        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect_to_device)

        connection_group = QGroupBox("Conexión")
        connection_layout = QVBoxLayout()
        connection_layout.addWidget(self.device_combobox)
        connection_layout.addWidget(self.baudrate_combobox)
        connection_layout.addWidget(self.connect_button)
        connection_group.setLayout(connection_layout)

        self.mode_switch = Switch()
        mode_group = QGroupBox("Modo")
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.mode_switch)
        mode_group.setLayout(mode_layout)

        layout = QVBoxLayout()
        layout.addWidget(connection_group)
        layout.addWidget(mode_group)

        self.setLayout(layout)
        self.resize(1280, 720)

        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_from_device)

    def connect_to_device(self):
        if self.connect_button.text() == "Connect":
            device = self.device_combobox.currentText()
            baudrate = int(self.baudrate_combobox.currentText())
            self.ser = serial.Serial(device, baudrate)
            self.connect_button.setText("Disconnect")
            QMessageBox.information(self, "Connection status", f"Connected to {device} at {baudrate} baudrate")
            self.read_timer.start(80)
        else:
            if self.ser:
                self.read_timer.stop()
                self.ser.close()
                self.ser = None
            self.connect_button.setText("Connect")
            QMessageBox.information(self, "Connection status", "Disconnected")

    def read_from_device(self):
        if self.ser:
            line = self.ser.readline().decode().strip()
            print(line)

app = QApplication([])
window = MyApp()
window.show()
app.exec_()