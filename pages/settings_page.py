from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    thresholdChanged = Signal(int)
    frequencyFilterToggled = Signal(bool)

    def __init__(
        self,
        root,
        initial_threshold: int = 6000,
        frequency_filter_enabled: bool = False,
    ):
        super().__init__()
        self._root = root
        self._layout = QVBoxLayout(self)

        head_widget = QWidget()
        head_layout = QHBoxLayout(head_widget)
        head_layout.setContentsMargins(0, 0, 0, 0)

        head_layout.addWidget(QLabel("CONFIGURAÇÕES"), 1)

        back_button = QPushButton("Voltar")
        back_button.setStyleSheet(
            "font-size: 18px; color: #eee; background: none; border: none;"
        )

        def _go_back():
            if hasattr(root, "go_back"):
                root.go_back()
            elif hasattr(root, "goto"):
                root.goto("decoder")

        back_button.clicked.connect(_go_back)
        head_layout.addWidget(back_button)

        self._layout.addWidget(head_widget)

        threshold_row = QWidget()
        threshold_row_layout = QHBoxLayout(threshold_row)
        threshold_row_layout.setContentsMargins(0, 0, 0, 0)
        threshold_row_layout.addWidget(QLabel("LIMIAR DE ENTRADA:"), 1)
        self.threshold_value_label = QLabel(str(initial_threshold))
        threshold_row_layout.addWidget(self.threshold_value_label)
        self._layout.addWidget(threshold_row)

        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(0, 12000)
        self.threshold_slider.setValue(int(initial_threshold))
        self.threshold_slider.valueChanged.connect(self._on_threshold_changed)
        self._layout.addWidget(self.threshold_slider)

        self._layout.addWidget(QLabel("FILTRO DE FREQUÊNCIA"))

        self.frequency_filter_checkbox = QCheckBox("Usar filtro de frequência")
        self.frequency_filter_checkbox.setChecked(bool(frequency_filter_enabled))
        self.frequency_filter_checkbox.toggled.connect(self._on_frequency_filter_toggled)
        self._layout.addWidget(self.frequency_filter_checkbox)

        self._layout.addStretch(1)

    def _on_threshold_changed(self, value: int):
        self.threshold_value_label.setText(f"{value}")
        self._root.pages["decoder"].controller.threshold = value
        self._root.pages["decoder"]._update_threshold()
        self.thresholdChanged.emit(value)

    def _on_frequency_filter_toggled(self, checked: bool):
        self._root.pages["decoder"].controller.frequency_filter_enabled = checked
        self.frequencyFilterToggled.emit(checked)

