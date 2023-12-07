from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QMessageBox,
    QGroupBox,
    QLabel,
)
from PyQt6.QtCore import Qt, QTimer
from pyqtgraph import PlotWidget, mkPen
import serial
import serial.tools.list_ports


class SerialApp(QWidget):
    def __init__(self):
        super().__init__()

        self.training_mode = True
        self.ser = None

        self.pressure_values = []
        self.frequency_values = []
        self.time_press_values = []
        self.time_freq_values = []
        self.i = 0

        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(50)

    def initUI(self):
        self.setWindowTitle("Simulador de RCP Neonatal")

        main_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        # Serial group
        serial_group = QGroupBox("Conexiones")
        serial_layout = QHBoxLayout()

        self.port_combo = QComboBox()
        self.port_combo.addItems(
            [port.device for port in serial.tools.list_ports.comports()]
        )

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(
            ["9600", "14400", "19200", "38400", "57600", "115200"]
        )

        self.connect_button = QPushButton("Conectar")
        self.connect_button.clicked.connect(self.connect_serial)

        serial_layout.addWidget(self.port_combo)
        serial_layout.addWidget(self.baudrate_combo)
        serial_layout.addWidget(self.connect_button)

        serial_group.setLayout(serial_layout)

        # Mode group
        mode_group = QGroupBox("Modo")
        mode_layout = QVBoxLayout()

        simulation_group = QGroupBox("Simulación")
        simulation_layout = QVBoxLayout()
        simulation_group.setLayout(simulation_layout)


        self.mode_button = QPushButton("Cambiar a modo de evaluación")
        self.mode_button.clicked.connect(self.switch_mode)

        self.mode_label = QLabel("Modo actual: Entrenamiento")

        mode_layout.addWidget(self.mode_button)
        mode_layout.addWidget(self.mode_label)

        mode_group.setLayout(mode_layout)

        self.pressure_plot = PlotWidget()
        self.pressure_plot.setTitle("Presión")
        self.pressure_plot.setLabel('left', 'Presión [cm]')
        simulation_layout.addWidget(self.pressure_plot)

        self.frequency_plot = PlotWidget()
        self.frequency_plot.setTitle("Frecuencia")
        self.frequency_plot.setLabel('left', 'Frecuencia [bpm]') 
        simulation_layout.addWidget(self.frequency_plot)

        simulation_group.setLayout(simulation_layout)

        main_layout.addLayout(left_layout)
        main_layout.addWidget(serial_group)
        main_layout.addWidget(mode_group)
        main_layout.addWidget(simulation_group)

        self.setLayout(main_layout)

    def connect_serial(self):
        if self.connect_button.text() == "Conectar":
            try:
                self.ser = serial.Serial(
                    self.port_combo.currentText(),
                    int(self.baudrate_combo.currentText()),
                )
                self.connect_button.setText("Desconectar")
                QMessageBox.information(self, "Serial", "Conectado al puerto serie")
            except Exception as e:
                QMessageBox.critical(self, "Serial", f"Fallo al intentar conectar: {e}")
        else:
            self.ser.close()
            self.ser = None
            self.connect_button.setText("Conectar")
            QMessageBox.information(self, "Serial", "Desconectado del puerto serie")

    def read_serial(self):
        if self.ser is not None and self.ser.in_waiting > 0:
            self.i = self.i+1
            line = self.ser.readline().decode("utf-8").strip()
            print(line)
            if line.startswith('P'):
                value = float(line[1:])  
                if self.training_mode:
                    self.pressure_values.append(value/10)
                    self.time_press_values.append(self.i)
                    self.pressure_plot.plot(self.time_press_values, self.pressure_values, pen=mkPen('r', width=3))
            elif line.startswith('B'):
                value = float(line[1:])  
                if self.training_mode:
                    self.frequency_values.append(value)
                    self.time_freq_values.append(self.i)
                    self.frequency_plot.plot(self.time_freq_values, self.frequency_values, pen=mkPen('r', width=3))

    def switch_mode(self):
        self.training_mode = not self.training_mode
        self.mode_button.setText(
            "Cambiar a modo de entrenamiento"
            if not self.training_mode
            else "Cambiar a modo de evaluación"
        )
        self.mode_label.setText(
            f'Modo actual: {"Entrenamiento" if self.training_mode else "Evaluación"}'
        )
        if self.training_mode:
            self.frequency_plot.show()
            self.pressure_plot.show()
            self.i = 0
        else:
            self.frequency_plot.hide()
            self.pressure_plot.hide()
            self.i = 0


if __name__ == "__main__":
    app = QApplication([])
    ex = SerialApp()
    ex.show()
    app.exec()
