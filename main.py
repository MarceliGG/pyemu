#!/bin/python
from pathlib import Path
import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QSize, Qt, QRegularExpression
from PySide6.QtGui import QIcon, QRegularExpressionValidator
import tomllib
from importlib import resources


def get_icon(name): return resources.files("assets").joinpath(name)


class MemoryEdit(QLineEdit):
    def __init__(self, default):
        super().__init__(default)
        regex = QRegularExpression(r"^\d{1,5}\s*[kKmMgG]?$")
        validator = QRegularExpressionValidator(regex)
        self.setValidator(validator)


class Device(QListWidgetItem):
    def __init__(self, data: dict):
        super().__init__()
        match data.get("type", "unknown"):
            case "cdrom":
                self.setText(f"cdrom ({data.get("path", "no path")})")
                self.setIcon(QIcon(str(get_icon("cd.svg"))))
            case _:
                self.setText("Unknown or incorrect device type")
                self.setIcon(QIcon(str(get_icon("unknonw.svg"))))


class Page(QWidget):
    def __init__(self, data, name, parent=None):
        super().__init__(parent)
        self.lo = QVBoxLayout(self)
        tab_vm_label = QLabel(f"<h1>{name}</h1>")
        self.lo.addWidget(tab_vm_label)

        form = QFormLayout()

        mem_input = MemoryEdit(data["memory"])
        mem_input.setFixedWidth(60)
        form.addRow("Memory:", mem_input)

        toggles = QWidget()
        toggles_layout = QHBoxLayout()
        toggles.setLayout(toggles_layout)

        kvm_checkbox = QCheckBox("Enable KVM")
        kvm_checkbox.setChecked(data.get("kvm", True))
        network_checkbox = QCheckBox("Enable Network")
        network_checkbox.setChecked(data.get("network", True))
        toggles_layout.addWidget(kvm_checkbox)
        toggles_layout.addWidget(network_checkbox)
        toggles_layout.addStretch()

        form.addRow(toggles)

        self.lo.addLayout(form)

        devices = QListWidget()
        devices.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        devices.setIconSize(QSize(48, 48))

        for d in data.get("devices", []):
            devices.addItem(Device(d))

        self.lo.addWidget(devices)

        self.lo.addStretch()


class PyEmu(QWidget):
    def __init__(self):
        super().__init__()

        # Fix transparency for kvantum
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

        base = os.getenv("XDG_DATA_HOME")
        self.vms_folder = (
            Path(base) / "pyemu" / "vms"
            if base and base.strip()
            else Path.home() / ".local" / "share" / "pyemu" / "vms"
        )
        self.vms_folder.mkdir(parents=True, exist_ok=True)

        self.lo = QHBoxLayout(self)
        self.stack = QStackedWidget()

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(150)

        for file in sorted(self.vms_folder.glob("*.toml")):
            if file.is_file():
                # file_path = self.vms_folder / vm
                with file.open("rb") as f:
                    data = tomllib.load(f)
                self.sidebar.addItem(file.stem)
                self.stack.addWidget(Page(data, file.name, self.stack))

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.lo.addWidget(self.sidebar)
        self.sidebar.setCurrentRow(0)

        self.lo.addWidget(self.stack)


if __name__ == "__main__":
    app = QApplication([])

    widget = PyEmu()
    widget.show()

    sys.exit(app.exec())
