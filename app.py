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
    QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from pyqtgraph import PlotWidget, mkPen
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

class SerialApp(QWidget):
    def __init__(self):
        super().__init__()
        self.training_mode = True
        self.evaluation_mode = False
        self.ser = None
        self.value_prev = 150
        self.pressure_values = []
        self.frequency_values = []
        self.time_press_values = []
        self.time_freq_values = []
        self.i = 0
        self.optimal_pressure = 0
        self.optimal_frequency = 0
        self.insuficient_pressure = 0
        self.excesive_pressure = 0
        self.wrong_frequency = 0
        self.optimal_percentage = 0
        self.insuficient_percentage = 0
        self.excesive_percentage = 0
        self.wrong_freq_percentage = 0
        self.optimal_freq_percentage = 0
        self.value = 150
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(50)

    def initUI(self):
        self.setWindowTitle("Simulador de RCP Neonatal")
        main_layout = QVBoxLayout()
        left_layout = QVBoxLayout()
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
        self.pressure_plot.setLabel('left', 'Profundidad [cm]')
        simulation_layout.addWidget(self.pressure_plot)
        self.frequency_plot = PlotWidget()
        self.frequency_plot.setTitle("Frecuencia")
        self.frequency_plot.setLabel('left', 'Frecuencia [bpm]') 
        simulation_layout.addWidget(self.frequency_plot)
        self.pressure_plot.getAxis('bottom').setTicks([])
        self.frequency_plot.getAxis('bottom').setTicks([])
        self.start_finish_button = QPushButton("Iniciar")
        self.start_finish_button.clicked.connect(self.start_finish)
        self.start_finish_button.hide()
        self.export_button = QPushButton("Exportar resultados")
        self.export_button.clicked.connect(self.export)
        self.export_button.hide() 
        simulation_layout.addWidget(self.start_finish_button)
        simulation_layout.addWidget(self.export_button)
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
            if (self.i > 0):
                self.value_prev = self.value
            self.value = float(line[1:]) 
            print(line)
            if line.startswith('P'):
                if self.training_mode:
                    self.pressure_values.append(self.value/10)
                    self.time_press_values.append(self.i)
                    self.pressure_plot.plot(self.time_press_values, self.pressure_values, pen=mkPen('r', width=3))
            elif line.startswith('B'):
                if self.training_mode:
                    self.frequency_values.append(self.value)
                    self.time_freq_values.append(self.i)
                    self.frequency_plot.plot(self.time_freq_values, self.frequency_values, pen=mkPen('r', width=3))
            if self.evaluation_mode:
                if line.startswith('P'):
                    self.pressure_values.append(self.value/10)
                    self.time_press_values.append(self.i)
                    if self.value <= 80 and self.value > 63.8 and self.value_prev < self.value:
                        print("Presión insuficiente")
                        self.insuficient_pressure += 1
                    elif self.value > 54.2 and self.value <= 63.8 and self.value_prev < self.value:
                        print("Presión óptima")
                        self.optimal_pressure += 1
                    elif self.value <= 54.2 and self.value_prev < self.value:
                        print("Presión excesiva")
                        self.excesive_pressure += 1
                elif line.startswith('B'):
                    self.frequency_values.append(self.value)
                    self.time_freq_values.append(self.i)
                    if self.value > 100 and self.value <= 120:
                        print("Frecuencia óptima")
                        self.optimal_frequency += 1
                    else:
                        print("Frecuencia errónea")
                        self.wrong_frequency += 1
            
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
            self.frequency_plot.clear()
            self.pressure_plot.clear()
            self.frequency_values.clear()
            self.pressure_values.clear()
            self.time_freq_values.clear()
            self.time_press_values.clear()
            self.frequency_plot.show()
            self.pressure_plot.show()
            self.i = 0
        else:
            self.frequency_plot.hide()
            self.pressure_plot.hide()
            self.frequency_plot.clear()
            self.pressure_plot.clear()
            self.frequency_values.clear()
            self.pressure_values.clear()
            self.time_freq_values.clear()
            self.time_press_values.clear()
            self.start_finish_button.show()
            self.i = 0

    def start_finish(self):
        if self.start_finish_button.text() == "Iniciar":
            self.evaluation_mode = True
            QMessageBox.information(self, "Evaluación", "Evaluación iniciada")
            self.start_finish_button.setText("Finalizar")
        else:
            self.evaluation_mode = False
            self.optimal_percentage = self.optimal_pressure/(self.optimal_pressure+self.insuficient_pressure+self.excesive_pressure)*100
            self.insuficient_percentage = self.insuficient_pressure/(self.optimal_pressure+self.insuficient_pressure+self.excesive_pressure)*100
            self.excesive_percentage = self.excesive_pressure/(self.optimal_pressure+self.insuficient_pressure+self.excesive_pressure)*100
            self.optimal_freq_percentage = self.optimal_frequency/(self.optimal_frequency+self.wrong_frequency)*100
            self.wrong_freq_percentage = self.wrong_frequency/(self.optimal_frequency+self.wrong_frequency)*100
            self.start_finish_button.hide()
            self.export_button.show()
            QMessageBox.information(self, "Evaluación", "Evaluación finalizada")
            summary = (f'Presión insuficiente: {self.insuficient_percentage:.2f}%\n'
                   f'Presión óptima: {self.optimal_percentage:.2f}%\n'
                   f'Presión excesiva: {self.excesive_percentage:.2f}%\n'
                   f'Frecuencia óptima: {self.optimal_freq_percentage:.2f}%\n'
                   f'Frecuencia errónea: {self.wrong_freq_percentage:.2f}%\n')
            QMessageBox.information(self, "Resumen de resultados", summary)

    def export(self):
        self.export_button.hide()
        self.start_finish_button.show()
        try:
            self.export_pdf()
            QMessageBox.information(self, "Exportar", "Reporte exportado")
        except:
            QMessageBox.critical(self, "Exportar", "Error al exportar reporte")
        self.excesive_pressure = 0
        self.insuficient_pressure = 0
        self.optimal_frequency = 0
        self.optimal_pressure = 0
        self.wrong_frequency = 0
        self.optimal_percentage = 0
        self.insuficient_percentage = 0
        self.excesive_percentage = 0
        self.wrong_freq_percentage = 0
        self.optimal_freq_percentage = 0
        self.start_finish_button.setText("Iniciar")
    
    def export_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar como", "", "PDF Files (*.pdf)")
        if file_name:
            with PdfPages(file_name) as pdf:
                fig = Figure(figsize=(6, 10))
                ax1 = fig.add_axes([0.1, 0.71, 0.8, 0.2])
                ax1.plot(self.pressure_values, 'r')
                ax1.set_title('Presión ejercida sobre el pecho')
                ax1.set_ylabel('Profundidad [cm]')
                ax2 = fig.add_axes([0.1, 0.5, 0.8, 0.2])
                ax2.pie([self.optimal_pressure, self.insuficient_pressure, self.excesive_pressure], labels=['Presión óptima', 'Presión insuficiente', 'Presión excesiva'], autopct='%1.1f%%')
                ax3 = fig.add_axes([0.1, 0.25, 0.8, 0.2])
                ax3.plot(self.frequency_values, 'r')
                ax3.set_title('Frecuencia de compresiones')
                ax3.set_ylabel('Frecuencia [bpm]')
                ax4 = fig.add_axes([0.1, 0, 0.8, 0.2])
                ax4.pie([self.optimal_frequency, self.wrong_frequency], labels=['Frecuencia óptima', 'Frecuencia errónea'], autopct='%1.1f%%')
                fig.suptitle('Simulador de RCP Neonatal, reporte de desempeño')
                pdf.savefig(fig)

if __name__ == "__main__":
    app = QApplication([])
    ex = SerialApp()
    ex.show()
    app.exec()