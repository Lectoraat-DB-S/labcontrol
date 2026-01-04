"""
Device Status Widget - Shows connection status of all devices at a glance
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class DeviceStatusWidget(QWidget):
    """Widget showing status of all connected devices"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.status_labels = {}
        self.initUI()

    def initUI(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        group = QGroupBox("Device Status")
        group_layout = QGridLayout(group)

        # Device types
        devices = [
            ('scope', '📊 Oscilloscope'),
            ('supply', '⚡ Power Supply'),
            ('generator', '〰️ Function Generator'),
            ('dmm', '🔢 Multimeter')
        ]

        for row, (dev_id, dev_name) in enumerate(devices):
            # Device name label
            name_label = QLabel(dev_name)
            name_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
            group_layout.addWidget(name_label, row, 0)

            # Status indicator
            status_label = QLabel("⚫ Not detected")
            status_label.setStyleSheet("QLabel { color: #888; }")
            self.status_labels[dev_id] = status_label
            group_layout.addWidget(status_label, row, 1)

        layout.addWidget(group)
        layout.addStretch()

    def setDeviceStatus(self, device_id, connected, info=""):
        """
        Update device status

        Args:
            device_id: Device identifier ('scope', 'supply', 'generator', 'dmm')
            connected: True if connected, False otherwise
            info: Additional info string (model name, error message, etc.)
        """
        if device_id not in self.status_labels:
            return

        label = self.status_labels[device_id]

        if connected:
            label.setText(f"🟢 {info}")
            label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; }")
        else:
            label.setText(f"🔴 {info}")
            label.setStyleSheet("QLabel { color: #888; }")
