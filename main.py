import sys
from PySide6.QtWidgets import QApplication, QStackedWidget, QMainWindow

from pages.decoder_page import DecoderPage
from pages.settings_page import SettingsPage

        
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
            "settings": SettingsPage(self),
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
