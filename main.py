import sys
from PySide6.QtWidgets import QApplication, QStackedWidget, QMainWindow

from pages.decoder_page import DecoderPage

# class SettingsPage(QWidget):
#     def __init__(self):
#         super().__init__()
#         self._layout = QVBoxLayout(self)
        
#         header = QWidget()
#         header_layout = QHBoxLayout(header)
        
#         title = QLabel("Configurações")
#         title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4caf50; margin-bottom: 20px")
#         header_layout.addWidget(title)

#         back_button = QPushButton("Voltar")
#         def go_back():
#             parent = self.parentWidget()
#             if isinstance(parent, QStackedWidget):
#                 parent.setCurrentIndex(0)
#         back_button.clicked.connect(go_back)
#         header_layout.addWidget(back_button)
#         back_button.setStyleSheet("color: #eee;")

#         self._layout.addWidget(header)

        
class MorseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Decodificador Morse")
        self.resize(1100, 700)
        self.setStyleSheet("background-color: #0a0a0a; color: #eee;")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.pages = {
            "decoder": DecoderPage(self),
            # "settings": SettingsPage(self)
        }
        self.history = []

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.goto("decoder")

    def goto(self, page_name):
        if page_name in self.pages:
            page = self.pages[page_name]
            self.stack.setCurrentWidget(page)

            self.history.append(page_name)
            if len(self.history) > 10:
                self.history.pop(0)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()  # Remove a página atual
            previous_page = self.history[-1]  # Página anterior
            self.goto(previous_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MorseApp()
    window.show()
    sys.exit(app.exec())
