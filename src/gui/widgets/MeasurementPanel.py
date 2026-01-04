"""Measurement Panel Widget"""
import csv
from datetime import datetime

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MeasurementPanel(QWidget):
    measurementRequested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.measurements = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        group = QGroupBox("Measurements")
        group_layout = QVBoxLayout(group)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Time', 'Mean (V)', 'Min (V)', 'Max (V)', 'Pk-Pk (V)'])
        group_layout.addWidget(self.table)

        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.exportToCSV)
        group_layout.addWidget(export_btn)

        layout.addWidget(group)

    def addMeasurement(self, meas_dict):
        """Add measurement to table"""
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(meas_dict['timestamp'].strftime('%H:%M:%S')))
        self.table.setItem(row, 1, QTableWidgetItem(f"{meas_dict['mean']:.3f}"))
        self.table.setItem(row, 2, QTableWidgetItem(f"{meas_dict['min']:.3f}"))
        self.table.setItem(row, 3, QTableWidgetItem(f"{meas_dict['max']:.3f}"))
        self.table.setItem(row, 4, QTableWidgetItem(f"{meas_dict['pkpk']:.3f}"))

        self.measurements.append(meas_dict)
        self.table.scrollToBottom()

    def exportToCSV(self):
        """Export measurements to CSV file"""
        if not self.measurements:
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Measurements",
                                                   "measurements.csv", "CSV Files (*.csv)")
        if filename:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Mean (V)', 'Min (V)', 'Max (V)', 'Pk-Pk (V)'])
                for m in self.measurements:
                    writer.writerow([m['timestamp'], m['mean'], m['min'], m['max'], m['pkpk']])
