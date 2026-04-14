import sys
import numpy as np
import pyaudio
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit
from PySide6.QtCore import QThread, Signal, Slot, QTimer
import time

# --- Dicionário Morse ---
MORSE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', 
    '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', 
    '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U', 
    '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '.----': '1', 
    '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7', 
    '---..': '8', '----.': '9', '-----': '0'
}

class AudioEngine(QThread):
    def __init__(self):
        super().__init__()
        self.active = True
        self.chunk = 1024
        self.rate = 44100
        self.threshold = 4000
        
        # Configurações de Tempo Morse
        self.U = 0.6  # Unidade base em segundos (60 ms)

        # Configurações de sinal
        self.DOT_LENGTH = self.U         # Limite para identificar ponto
        self.DASH_LENGTH = self.U * 3    # Limite para identificar traço

        self.SIGNAL_GAP_LENGTH = self.U # Tempo de silêncio entre sinais
        self.LETTER_GAP_LENGTH = self.U * 3    # Tempo de silêncio entre letras
        self.WORD_GAP_LENGTH = self.U * 7    # Tempo de silêncio entre palavras

        # Configurações de intervalos
        self.DOT_DASH_LIMIT = (self.DOT_LENGTH + self.DASH_LENGTH) / 2
        self.SIGNAL_LETTER_GAP_LIMIT = (self.SIGNAL_GAP_LENGTH + self.LETTER_GAP_LENGTH) / 2
        self.LETTER_WORD_GAP_LIMIT = (self.LETTER_GAP_LENGTH + self.WORD_GAP_LENGTH) / 2
        

        # Configurações do buffer
        self.buffer_size = self.rate * 3 # 3 segundos no gráfico
        self.raw_data = np.zeros(self.buffer_size, dtype=np.int16)
        self.clean_data = np.zeros(self.buffer_size, dtype=np.int16)
        
        self.current_signal = ""
        self.morse_str = ""
        self.text_str = ""
        self.last_state = False
        self.signal_pushed = False
        self.last_time = time.time()

    def morse_to_text(self, morse_str):
        message = ""

        words = morse_str.split(" / ")
        for i, word in enumerate(words):
            letters = word.split(" ")
            for letter in letters:
                if letter == "":
                    continue
                message += MORSE_DICT.get(letter, "?")

            if i < len(words) - 1:
                message += " "

        return message

    def push_signal(self): 
        if self.signal_pushed:
            return

        self.morse_str += self.current_signal
        self.current_signal = ""
        self.signal_pushed = True

    def run(self):
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=self.rate,
                            input=True, frames_per_buffer=self.chunk)
        except: return

        while self.active:
            try:
                # Carregando Chunk de Áudio
                block = np.frombuffer(stream.read(self.chunk, exception_on_overflow=False), dtype=np.int16)
                self.raw_data = np.roll(self.raw_data, -self.chunk)
                self.raw_data[-self.chunk:] = block
                
                # Digitalizando Dados
                is_on = np.max(np.abs(block)) > self.threshold
                self.clean_data = np.roll(self.clean_data, -self.chunk)
                self.clean_data[-self.chunk:] = 10000 if is_on else 0
                
                now = time.time()
                duration = now - self.last_time
                

                if not self.signal_pushed:
                    if self.last_state:
                        if duration < self.DOT_DASH_LIMIT:
                            self.current_signal = "."
                        
                        else:
                            self.current_signal = "-"
                            self.push_signal()

                    else:
                        if self.morse_str == "" or duration < self.SIGNAL_LETTER_GAP_LIMIT:
                            self.current_signal = ""
                        
                        elif duration < self.LETTER_WORD_GAP_LIMIT:
                            self.current_signal = " "
                        
                        elif self.morse_str != "":
                            self.current_signal = " / "
                            self.push_signal()


                # Processando Código Morse
                if is_on != self.last_state:
                    self.push_signal()
                    self.signal_pushed = False

                    self.last_time = now
                    self.last_state = is_on

            except Exception as e:
                print(e)
                continue

        stream.stop_stream()
        p.terminate()

class MorseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Decodificador Morse")
        self.resize(1100, 700)
        self.setStyleSheet("background-color: #0a0a0a; color: #eee;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        pg.setConfigOptions(antialias=False)

        def setup_plot(title, color, y_range):
            layout.addWidget(QLabel(title))
            pw = pg.PlotWidget()
            pw.setBackground('#0a0a0a')

            vb = pw.getViewBox()
            vb.setDefaultPadding(0)
            vb.setContentsMargins(0, 0, 0, 0)
            vb.setBorder(pg.mkPen(color='#333', width=1))
            
            pw.setYRange(y_range[0], y_range[1])
            pw.setMouseEnabled(x=False, y=False)
            pw.hideButtons()
            pw.setMenuEnabled(False)
            pw.showAxis('left', False)
            pw.showAxis('bottom', False)
            curve = pw.plot(pen=pg.mkPen(color, width=1.5))
            layout.addWidget(pw)
            return curve

        self.raw_curve = setup_plot("SINAL BRUTO", '#00d2ff', [-16000, 16000])
        self.clean_curve = setup_plot("SINAL DIGITALIZADO", '#ffeb3b', [-500, 11000])

        layout.addWidget(QLabel("CÓDIGO MORSE"))
        self.morse_display = QTextEdit()
        self.morse_display.setFixedHeight(60)
        self.morse_display.setReadOnly(True)
        self.morse_display.setStyleSheet("background: #0a0a0a; border: 1px solid #333; font-family: monospace; font-size: 18px; color: orange;")
        layout.addWidget(self.morse_display)

        layout.addWidget(QLabel("TEXTO DECODIFICADO"))
        self.text_display = QTextEdit()
        self.text_display.setFixedHeight(100)
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("background: #0a0a0a; border: 1px solid #333; font-size: 32px; font-weight: bold; color: #4caf50;")
        layout.addWidget(self.text_display)

        self.engine = AudioEngine()
        self.engine.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(40)

    def update_ui(self):
        self.raw_curve.setData(self.engine.raw_data[::16])
        self.clean_curve.setData(self.engine.clean_data[::16])
        
        # Mostra o sinal em progresso
        display_text = self.engine.morse_str + self.engine.current_signal
        if self.morse_display.toPlainText() != display_text:
            self.morse_display.setText(display_text)
            self.text_display.setText(self.engine.morse_to_text(display_text))
            scroll = self.morse_display.verticalScrollBar()
            scroll.setValue(scroll.maximum())

    def closeEvent(self, event):
        self.engine.active = False
        self.engine.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MorseApp()
    window.show()
    sys.exit(app.exec())
