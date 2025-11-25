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
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
import tomllib


class MemoryEdit(QLineEdit):
    def __init__(self, default):
        super().__init__(default)
        regex = QRegularExpression(r"^\d{1,5}\s*[kKmMgG]?$")
        regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
        validator = QRegularExpressionValidator(regex)
        self.setValidator(validator)


class Page(QWidget):
    def __init__(self, data, name):
        super().__init__()
        self.layout = QVBoxLayout(self)
        tab_vm_label = QLabel()
        tab_vm_label.setText(f"<h1>{name}</h1>")
        self.layout.addWidget(tab_vm_label)

        form = QFormLayout()

        mem_input = MemoryEdit(data["memory"])
        mem_input.setFixedWidth(60)
        form.addRow("Memory:", mem_input)

        toggles = QWidget()
        toggles_layout = QHBoxLayout()
        toggles.setLayout(toggles_layout)

        kvm_checkbox = QCheckBox("Enable KVM")
        kvm_checkbox.setChecked(data["kvm"])
        network_checkbox = QCheckBox("Enable Network")
        network_checkbox.setChecked(data["network"])
        toggles_layout.addWidget(kvm_checkbox)
        toggles_layout.addWidget(network_checkbox)
        toggles_layout.addStretch()

        form.addRow(toggles)

        self.layout.addLayout(form)

        self.layout.addStretch()


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

        self.layout = QHBoxLayout(self)
        self.stack = QStackedWidget()

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)

        for file in self.vms_folder.glob("*.toml"):
            if file.is_file():
                # file_path = self.vms_folder / vm
                with file.open("rb") as f:
                    data = tomllib.load(f)
                self.sidebar.addItem(file.stem)
                self.stack.addWidget(Page(data, file.name))

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        # self.sidebar.layout.addStretch()
        self.layout.addWidget(self.sidebar)
        self.sidebar.setCurrentRow(0)

        self.layout.addWidget(self.stack)


if __name__ == "__main__":
    app = QApplication([])

    widget = PyEmu()
    widget.show()

    sys.exit(app.exec())
