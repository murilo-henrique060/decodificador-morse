from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QTextEdit, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer

from widgets.plot_widget import PlotWidget

from controllers.decoder_controller import DecoderController

class DecoderPage(QWidget):
    def __init__(self, root):
        super().__init__()
        self._layout = QVBoxLayout(self)        


        headWidget = QWidget()
        headLayout = QHBoxLayout(headWidget)
        headLayout.setContentsMargins(0, 0, 0, 0)
        headLayout.addWidget(QLabel("SINAL BRUTO"), 1)
        self.settings_btn = QPushButton("")
        self.settings_btn.setIcon(QIcon("img/gear-fill.svg"))
        self.settings_btn.setStyleSheet("font-size: 18px; color: #eee; background: none; border: none;")
        self.settings_btn.clicked.connect(lambda: root.goto("settings"))
        headLayout.addWidget(self.settings_btn)
        self._layout.addWidget(headWidget)

        self.raw_curve = PlotWidget(color="#00d2ff", y_range=(-12000, 12000))
        self._layout.addWidget(self.raw_curve)


        self._layout.addWidget(QLabel("SINAL DIGITALIZADO"))
        self.clean_curve = PlotWidget(color="#ecc546", y_range=(0, 1.2))
        self._layout.addWidget(self.clean_curve)


        rowWidget = QWidget()
        rowLayout = QHBoxLayout(rowWidget)
        rowLayout.setContentsMargins(0, 0, 0, 0)
        rowLayout.addWidget(QLabel("CÓDIGO MORSE"), 1)
        self.settings_btn = QPushButton("Reiniciar")
        self.settings_btn.clicked.connect(lambda: self.controller.reset())
        rowLayout.addWidget(self.settings_btn)
        self._layout.addWidget(rowWidget)

        self.morse_display = QTextEdit()
        self.morse_display.setFixedHeight(60)
        self.morse_display.setReadOnly(True)
        self.morse_display.setStyleSheet("background: #0a0a0a; border: 1px solid #333; font-family: monospace; font-size: 18px; color: orange;")
        self._layout.addWidget(self.morse_display)


        self._layout.addWidget(QLabel("TEXTO DECODIFICADO"))
        self.text_display = QTextEdit()
        self.text_display.setFixedHeight(100)
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("background: #0a0a0a; border: 1px solid #333; font-size: 32px; font-weight: bold; color: #4caf50;")
        self._layout.addWidget(self.text_display)


        self.controller = DecoderController()
        self.controller.start()

        self._update_threshold()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(40)


    def _update_threshold(self):
        value = self.controller.threshold
        
        self.raw_curve.clearHLines()
        self.raw_curve.addHLine(y=value)
        self.raw_curve.addHLine(y=-value)


    def update_ui(self):
        self.raw_curve.setData(self.controller.raw_data[::16])
        self.clean_curve.setData(self.controller.clean_data[::16])

        if self.morse_display.toPlainText() != self.controller.morse_str:
            self.morse_display.setText(self.controller.morse_str)
        
        if self.text_display.toPlainText() != self.controller.text_str:
            self.text_display.setText(self.controller.text_str)
    

    def closeEvent(self, event):
        self.controller.close()
        self.controller.wait()
        event.accept()